from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
import requests
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models
from database import engine, get_db
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()

from agents.icp_agent import ICPAgent
from agents.seo_agent import SEOAgent
from agents.writer_agent import WriterAgent
from agents.repurposing_agent import RepurposingAgent
from agents.scheduler import Scheduler
from agents.analytics_agent import AnalyticsAgent
from agents.trigger_agent import TriggerAgent
from agents.trend_agent import TrendAgent
from tasks import celery_app, generate_content_task

import time
TREND_CACHE = {"data": None, "timestamp": 0}

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

import asyncio
import json
import redis.asyncio as aioredis

async def listen_to_redis_logs():
    try:
        r = await aioredis.from_url("redis://localhost:6379/0", decode_responses=True)
        pubsub = r.pubsub()
        await pubsub.subscribe("agent_logs")
        print("Subscribed to agent_logs channel")
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    print("Broadcasting log:", data)
                    await manager.broadcast(data)
                except Exception as e:
                    print(f"Error broadcasting message: {e}")
    except Exception as e:
        print(f"Redis listener failed to start: {e}")

background_tasks = set()

@app.on_event("startup")
async def startup_event():
    task = asyncio.create_task(listen_to_redis_logs())
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TopicRequest(BaseModel):
    keywords: list[str]
    mode: str = "manual" # manual, scheduled, spike

class EnhanceRequest(BaseModel):
    topic: str
    angle: str = ""
    target_persona: str = ""
    direction: str = ""
    image_idea: str = ""

class GenerateRequest(BaseModel):
    topic: str
    angle: str = ""
    target_persona: str = ""
    tone: str = "thought_leader"
    author_voice: str = "bitcot"
    image_idea: str = ""
    use_web_search: bool = False
    image_source: str = "ai"

@app.get("/")
def read_root():
    return {"status": "Bitcot Content OS Active"}

@app.get("/proxy-image")
def proxy_image(url: str):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        }
        r = requests.get(url, headers=headers, timeout=10)
        return Response(content=r.content, media_type=r.headers.get("Content-Type", "image/jpeg"))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to fetch image")

@app.get("/discover-trends")
def discover_trends():
    """Fetches trending topics from HN/DDG and scores them, caching for 30 minutes."""
    global TREND_CACHE
    now = time.time()
    
    # Cache for 30 minutes (1800 seconds)
    if TREND_CACHE["data"] is not None and (now - TREND_CACHE["timestamp"]) < 1800:
        return {"trends": TREND_CACHE["data"], "cached": True}
        
    try:
        agent = TrendAgent()
        trends = agent.discover_trends()
        if trends:
            TREND_CACHE["data"] = trends
            TREND_CACHE["timestamp"] = now
        return {"trends": trends, "cached": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

@app.post("/enhance-topic")
def enhance_topic_endpoint(request: EnhanceRequest, db: Session = Depends(get_db)):
    """
    Takes a basic topic and user angle, and returns a highly creative, ICP-aligned enhanced topic and angle.
    """
    icp_agent = ICPAgent()
    enhanced = icp_agent.enhance_topic(
        topic=request.topic,
        angle=request.angle,
        target_persona=request.target_persona,
        direction=request.direction,
        image_idea=request.image_idea,
        db=db
    )
    return {
        "status": "success",
        "enhanced_topic": enhanced.get("enhanced_topic", request.topic),
        "enhanced_angle": enhanced.get("enhanced_angle", ""),
        "enhanced_image_idea": enhanced.get("enhanced_image_idea", "")
    }

@app.post("/generate")
def generate_content(request: GenerateRequest, db: Session = Depends(get_db)):
    """
    Chains ICP → SEO → Writer agents.
    Both agents load brand context from the Supabase memory layer.
    """
    from agents.graph import app_graph

    # Initialize Graph State
    initial_state = {
        "topic": request.topic,
        "angle": request.angle,
        "target_persona": request.target_persona,
        "tone": request.tone,
        "author_voice": request.author_voice,
        "image_idea": request.image_idea,
        "use_web_search": request.use_web_search,
        "image_source": request.image_source,
        "db_session": db,
        "icp_result": None,
        "seo_data": None,
        "draft": None,
        "status": ""
    }

    # Execute LangGraph
    final_state = app_graph.invoke(initial_state)

    if final_state["status"] == "rejected":
        icp_result = final_state.get("icp_result", {})
        score = icp_result.get("score", 0.0)
        raise HTTPException(
            status_code=400,
            detail=(
                f"Topic rejected by ICP Agent. "
                f"Score: {score:.2f}. "
                f"Reason: {icp_result.get('reasoning', 'Does not match Bitcot ICP.')} "
                f"Suggestion: {icp_result.get('reshape_suggestion', '')}"
            )
        )

    draft = final_state["draft"]
    score = final_state.get("icp_result", {}).get("score", 0.0)
    decision = final_state.get("icp_result", {}).get("decision", "PASS")
    icp_result = final_state.get("icp_result", {})


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
    task = generate_content_task.delay(request.topic, request.angle, request.tone, request.image_idea, request.use_web_search, request.image_source)
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

class RegenerateRequest(BaseModel):
    content_id: int
    target_part: str
    feedback: str

@app.post("/regenerate")
def regenerate_content_endpoint(request: RegenerateRequest, db: Session = Depends(get_db)):
    from agents.regenerate_agent import RegenerateAgent
    import json
    
    agent = RegenerateAgent()
    try:
        new_draft = agent.regenerate_content(db, request.content_id, request.target_part, request.feedback)
        
        # Get original log for versioning
        old_log = db.query(models.ContentLog).filter(models.ContentLog.id == request.content_id).first()
        new_version = (old_log.version or 1) + 1
        
        # Save as new row
        log = models.ContentLog(
            topic=old_log.topic,
            icp_score=old_log.icp_score,
            platform=old_log.platform,
            content=json.dumps(new_draft),
            status="pending_review",
            needs_human_check=new_draft.get("needs_human_check", True),
            parent_id=old_log.id,
            version=new_version
        )
        db.add(log)
        
        # Update old log to mark as replaced/archived? We'll just leave it as draft or rejected
        old_log.status = "draft"
        
        db.commit()
        db.refresh(log)
        
        return {
            "status": "success",
            "content_id": log.id,
            "version": log.version,
            "topic": new_draft.get("topic"),
            "blog": new_draft.get("blog", {}),
            "linkedin": new_draft.get("linkedin", {}),
            "x_thread": new_draft.get("x_thread", {}),
            "needs_human_check": log.needs_human_check,
            "check_flags": new_draft.get("check_flags", [])
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class ScheduleRequest(BaseModel):
    content_id: int
    platform: str
    schedule_time: str

@app.post("/schedule")
def schedule_post(request: ScheduleRequest, db: Session = Depends(get_db)):
    """
    Schedules an approved post.
    """
    from agents.publisher_agent import PublisherAgent
    scheduler = PublisherAgent()
    result = scheduler.schedule_content(request.content_id, request.platform, request.schedule_time)
    return result

@app.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):
    """
    Fetches the analytics data for View 3.
    """
    analytics_agent = AnalyticsAgent()
    metrics = analytics_agent.get_metrics()
    
    bc = db.query(models.BrandContext).filter_by(key="ai_learnings").first()
    learnings = bc.value if bc else None
    
    return {
        "linkedin_engagement_rate": metrics.linkedin_engagement_rate,
        "form_conversion_rate": metrics.form_conversion_rate,
        "x_bookmark_rate": metrics.x_bookmark_rate,
        "top_performers": metrics.top_performers,
        "under_performers": metrics.under_performers,
        "ai_learnings": learnings
    }

@app.post("/trigger-learning-loop")
def trigger_learning_loop():
    agent = AnalyticsAgent()
    try:
        rulebook = agent.run_learning_loop()
        return {"status": "success", "rulebook": rulebook}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        if not isinstance(draft, dict):
            draft = {"blog": {"body": str(draft)}}
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
