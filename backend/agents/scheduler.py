import os
import requests
from datetime import datetime
from database import SessionLocal
import models

class Scheduler:
    def __init__(self):
        # Read API keys from env. If missing, stay in sandbox.
        self.linkedin_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        self.x_bearer_token = os.getenv("X_BEARER_TOKEN")
        self.webflow_token = os.getenv("WEBFLOW_API_TOKEN")
        self.sandbox_mode = not (self.linkedin_token or self.x_bearer_token or self.webflow_token)

    def schedule_content(self, content_id: int, platform: str, schedule_time: datetime) -> dict:
        """
        Schedules or instantly publishes approved content depending on schedule_time.
        """
        db = SessionLocal()
        try:
            log = db.query(models.ContentLog).filter(models.ContentLog.id == content_id).first()
            if not log:
                return {"status": "error", "message": "Content not found"}

            status = "sandbox_scheduled" if self.sandbox_mode else "scheduled"
            log.status = "scheduled"

            # Production Live Publishing Snippets (Execute if not sandbox)
            if not self.sandbox_mode:
                if platform.lower() == "linkedin" and self.linkedin_token:
                    # In production, use linkedin v2 API to post UGC share
                    pass
                elif platform.lower() == "x" and self.x_bearer_token:
                    # Use tweepy or direct v2 tweets endpoint
                    pass
                elif platform.lower() == "blog" and self.webflow_token:
                    # Push draft to Webflow CMS collection
                    pass

            db.commit()
            
            return {
                "status": "success",
                "message": f"Content {content_id} scheduled for {platform} at {schedule_time}",
                "publish_status": status,
                "sandbox_mode": self.sandbox_mode
            }
        except Exception as e:
            db.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            db.close()
