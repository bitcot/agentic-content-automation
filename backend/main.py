from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models
from database import engine, get_db
from pydantic import BaseModel

from agents.icp_agent import ICPAgent
from agents.seo_agent import SEOAgent
from agents.writer_agent import WriterAgent
from agents.repurposing_agent import RepurposingAgent
from agents.scheduler import Scheduler
from agents.analytics_agent import AnalyticsAgent
from agents.trigger_agent import TriggerAgent
from tasks import celery_app, generate_content_task

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bitcot Autonomous Content System API")

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TopicRequest(BaseModel):
    keywords: list[str]
    mode: str = "manual" # manual, scheduled, spike

class GenerateRequest(BaseModel):
    topic: str
    angle: str = ""
    tone: str = "thought_leader"

@app.get("/")
def read_root():
    return {"message": "Welcome to the Bitcot Autonomous Content System API"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/trigger")
def trigger_manual(request: TopicRequest, db: Session = Depends(get_db)):
    """
    Manual trigger: user supplies a keyword list, first keyword is used.
    """
    selected_topic = request.keywords[0] if request.keywords else "AI Infrastructure"
    return {"status": "success", "selected_topic": selected_topic, "mode": request.mode}

@app.post("/trigger/auto")
async def trigger_auto(mode: str = "scheduled", db: Session = Depends(get_db)):
    """
    Autonomous trigger: uses pytrends + anti-cannibalization check to select today's topic.
    mode='scheduled' for Mode B, mode='spike' for Mode A.
    """
    agent = TriggerAgent()
    result = agent.select_topic(db, mode=mode)
    
    if mode == "spike" and result.get("selected_topic"):
        await manager.broadcast({
            "type": "SPIKE_DETECTED",
            "topic": result.get("selected_topic"),
            "data": result
        })
        
    return {"status": "success", **result}

@app.get("/history")
def get_content_history(
    limit: int = 20,
    status: str = None,
    db: Session = Depends(get_db)
):
    """
    Returns past content logs from the memory layer.
    """
    query = db.query(models.ContentLog).order_by(models.ContentLog.created_at.desc())
    if status:
        query = query.filter(models.ContentLog.status == status)
    logs = query.limit(limit).all()
    return {
        "status": "success",
        "count": len(logs),
        "items": [
            {
                "id": log.id,
                "topic": log.topic,
                "icp_score": log.icp_score,
                "platform": log.platform,
                "status": log.status,
                "needs_human_check": log.needs_human_check,
                "created_at": log.created_at.isoformat() if log.created_at else None,
                "published_at": log.published_at.isoformat() if log.published_at else None,
            }
            for log in logs
        ]
    }

@app.post("/research")
def research_agent(topic: str, db: Session = Depends(get_db)):
    """
    Research Agent placeholder.
    In the future, this will use APIs (PRAW, Google Trends, etc.) to gather context.
    """
    # Placeholder logic
    research_data = {
        "topic": topic,
        "summary": f"Initial research findings for '{topic}' indicate high enterprise interest.",
        "key_stats": ["70% of enterprises struggle with this.", "Adoption has increased 3x."],
        "competitor_gaps": ["Lack of actionable implementation guides."]
    }
    return {
        "status": "success",
        "data": research_data
    }

class EnhanceRequest(BaseModel):
    topic: str

@app.post("/enhance-topic")
def enhance_topic_endpoint(request: EnhanceRequest, db: Session = Depends(get_db)):
    """
    Takes a basic topic and returns an ICP-aligned enhanced topic and angle.
    """
    icp_agent = ICPAgent()
    enhanced = icp_agent.enhance_topic(request.topic, db=db)
    return {
        "status": "success",
        "enhanced_topic": enhanced.get("enhanced_topic", request.topic),
        "enhanced_angle": enhanced.get("enhanced_angle", "")
    }

@app.post("/generate")
def generate_content(request: GenerateRequest, db: Session = Depends(get_db)):
    """
    Chains ICP → SEO → Writer agents.
    Both agents load brand context from the Supabase memory layer.
    """
    icp_agent = ICPAgent()
    seo_agent = SEOAgent()
    writer_agent = WriterAgent()

    # Step 1: ICP Alignment — loads personas, geo rules, verticals from DB
    icp_result = icp_agent.score_topic(request.topic, angle=request.angle, db=db)
    score = icp_result.get("score", 0.0)
    decision = icp_result.get("decision", "REJECT")

    if decision == "REJECT" or score < 0.65:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Topic rejected by ICP Agent. "
                f"Score: {score:.2f}. "
                f"Reason: {icp_result.get('reasoning', 'Does not match Bitcot ICP.')} "
                f"Suggestion: {icp_result.get('reshape_suggestion', '')}"
            )
        )

    # Step 2: SEO Analysis (keyword context)
    try:
        seo_package = seo_agent.analyze_topic(request.topic)
        seo_data = seo_package.model_dump() if hasattr(seo_package, 'model_dump') else {}
    except Exception:
        seo_data = {}

    # Step 3: Writer — loads all voice rules + approved stats from DB
    draft = writer_agent.generate_draft(
        topic=request.topic,
        icp_result=icp_result,
        tone=request.tone,
        db=db
    )

    # Save to ContentLog (one row per generation run)
    import json
    blog_body = draft.get("blog", {}).get("body", "")
    needs_check = draft.get("needs_human_check", True)

    log = models.ContentLog(
        topic=request.topic,
        icp_score=score,
        platform="all",
        content=json.dumps(draft),
        status="pending_review",
        needs_human_check=needs_check,
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    return {
        "status": "success",
        "content_id": log.id,
        "icp": {
            "score": score,
            "decision": decision,
            "persona_match": icp_result.get("persona_match"),
            "reasoning": icp_result.get("reasoning"),
        },
        "topic": draft.get("topic"),
        "blog": draft.get("blog", {}),
        "linkedin": draft.get("linkedin", {}),
        "x_thread": draft.get("x_thread", {}),
        "needs_human_check": needs_check,
        "check_flags": draft.get("check_flags", []),
        "token_usage": draft.get("token_usage", {}),
    }

@app.post("/generate/async")
def generate_content_async(request: GenerateRequest):
    """
    Triggers the generation pipeline in the background using Celery.
    Prevents API timeouts during heavy Claude tasks.
    """
    task = generate_content_task.delay(request.topic, request.angle, request.tone)
    return {"status": "processing", "task_id": task.id}

@app.get("/generate/status/{task_id}")
def get_task_status(task_id: str):
    """
    Check the status of a background generation task.
    """
    task = celery_app.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {"state": task.state, "status": "Pending..."}
    elif task.state != 'FAILURE':
        response = {"state": task.state, "result": task.info}
    else:
        response = {"state": task.state, "error": str(task.info)}
    return response

@app.post("/schedule")
def schedule_post(content_id: int, platform: str, schedule_time: str, db: Session = Depends(get_db)):
    """
    Schedules an approved post.
    """
    scheduler = Scheduler()
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(schedule_time)
    except ValueError:
        dt = datetime.utcnow()
        
    result = scheduler.schedule_content(content_id, platform, dt)
    return result

@app.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):
    """
    Fetches the analytics data for View 3.
    """
    analytics_agent = AnalyticsAgent()
    metrics = analytics_agent.get_metrics()
    return metrics

@app.get("/history/{content_id}")
def get_history_item(content_id: int, db: Session = Depends(get_db)):
    """
    Fetch a specific generated item to review it again.
    """
    log = db.query(models.ContentLog).filter(models.ContentLog.id == content_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Item not found")
        
    import json_repair
    try:
        draft = json_repair.loads(log.content)
    except Exception:
        draft = {"blog": {"body": log.content}} # Fallback for old records
        
    return {
        "status": "success",
        "content_id": log.id,
        "icp": {
            "score": log.icp_score,
            "decision": "APPROVED" if log.icp_score >= 0.65 else "REJECTED",
        },
        "topic": log.topic,
        "blog": draft.get("blog", {}),
        "linkedin": draft.get("linkedin", {}),
        "x_thread": draft.get("x_thread", {}),
        "needs_human_check": log.needs_human_check,
        "check_flags": draft.get("check_flags", []),
        "token_usage": draft.get("token_usage", {})
    }
