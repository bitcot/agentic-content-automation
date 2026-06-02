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
def generate_content_task(self, topic: str, angle: str, tone: str, image_idea: str = ""):
    """
    Background task to run the heavy agentic pipeline.
    """
    db = SessionLocal()
    try:
        icp_agent = ICPAgent()
        seo_agent = SEOAgent()
        writer_agent = WriterAgent()

        # 1. ICP
        icp_result = icp_agent.score_topic(topic, angle=angle, db=db)
        score = icp_result.get("score", 0.0)
        decision = icp_result.get("decision", "REJECT")

        if decision == "REJECT" or score < 0.65:
            return {
                "status": "rejected",
                "reason": icp_result.get("reasoning", "Failed ICP check")
            }

        # 2. SEO
        try:
            seo_package = seo_agent.analyze_topic(topic)
            seo_data = seo_package.model_dump() if hasattr(seo_package, 'model_dump') else {}
        except Exception:
            seo_data = {}

        # 3. Writer
        draft = writer_agent.generate_draft(
            topic=topic,
            icp_result=icp_result,
            tone=tone,
            image_idea=image_idea,
            db=db
        )

        import json
        blog_body = draft.get("blog", {}).get("body", "")
        needs_check = draft.get("needs_human_check", True)

        log = models.ContentLog(
            topic=topic,
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
            "topic": topic
        }
    except Exception as e:
        db.rollback()
        return {"status": "error", "error": str(e)}
    finally:
        db.close()
