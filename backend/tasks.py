import asyncio
from celery_app import celery_app
from database import SessionLocal
from dotenv import load_dotenv
load_dotenv()
import models
from agents.icp_agent import ICPAgent
from agents.seo_agent import SEOAgent
from agents.writer_agent import WriterAgent

@celery_app.task(bind=True, name="generate_content_task")
def generate_content_task(self, topic: str, angle: str, tone: str, image_idea: str = "", use_web_search: bool = False, image_source: str = "ai"):
    """
    Background task to run the heavy agentic pipeline.
    """
    db = SessionLocal()
    try:
        from agents.graph import app_graph

        # Initialize Graph State
        initial_state = {
            "topic": topic,
            "angle": angle,
            "target_persona": "",
            "tone": tone,
            "author_voice": "bitcot",
            "image_idea": image_idea,
            "use_web_search": use_web_search,
            "image_source": image_source,
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
            return {
                "status": "rejected",
                "reason": icp_result.get("reasoning", "Failed ICP check")
            }

        draft = final_state["draft"]
        score = final_state.get("icp_result", {}).get("score", 0.0)
        icp_result = final_state.get("icp_result", {})


        import json
        blog_body = draft.get("blog", {}).get("body", "")
        needs_check = draft.get("needs_human_check", True)

        # Apply QC Verification
        from agents.qc_agent import QCAgent
        qc_agent = QCAgent()
        qc_result = qc_agent.evaluate_draft(draft, topic)
        
        status = "pending_review"
        if qc_result.get("status") == "rejected":
            status = "qc_rejected"
            draft["qc_feedback"] = qc_result.get("feedback", "Failed QC standards.")

        # Apply AI Detection Scoring
        from agents.ai_score_agent import AIScoreAgent
        ai_agent = AIScoreAgent()
        ai_score_result = ai_agent.evaluate(blog_body)
        draft["ai_probability_score"] = ai_score_result.get("ai_probability_score", 100)
        draft["ai_reasoning"] = ai_score_result.get("reasoning", "")

        log = models.ContentLog(
            topic=topic,
            icp_score=score,
            platform="all",
            content=json.dumps(draft),
            status=status,
            needs_human_check=needs_check,
        )
        db.add(log)
        db.commit()
        db.refresh(log)

        return {
            "status": "success",
            "content_id": log.id,
            "topic": topic
        }
    except Exception as e:
        db.rollback()
        return {"status": "error", "error": str(e)}
    finally:
        db.close()
