import os
import json
from datetime import datetime
from database import SessionLocal
import models
import requests

class PublisherAgent:
    def __init__(self):
        self.webflow_api_key = os.getenv("WEBFLOW_API_KEY")
        self.webflow_collection_id = os.getenv("WEBFLOW_COLLECTION_ID")
        self.buffer_access_token = os.getenv("BUFFER_ACCESS_TOKEN")
        self.buffer_profile_ids = {
            "linkedin": os.getenv("BUFFER_LINKEDIN_PROFILE_ID"),
            "x": os.getenv("BUFFER_X_PROFILE_ID")
        }

    def schedule_content(self, content_id: int, platform: str, schedule_time: str) -> dict:
        """
        Approves a draft and hands it off for distribution.
        Updates the content status in the database and triggers external APIs.
        """
        db = SessionLocal()
        try:
            log = db.query(models.ContentLog).filter(models.ContentLog.id == content_id).first()
            if not log:
                return {"status": "error", "message": "Content not found."}

            content_data = json.loads(log.content)
            
            # Simulated Webflow Publishing
            if platform in ["blog", "all"]:
                blog_data = content_data.get("blog")
                if blog_data:
                    self._publish_to_webflow(blog_data)
                    print(f"Blog content queued for Webflow.")

            # Simulated Buffer Scheduling
            if platform in ["linkedin", "x", "all"]:
                if platform in ["linkedin", "all"]:
                    li_data = content_data.get("linkedin")
                    if li_data:
                        self._schedule_via_buffer(li_data, "linkedin", schedule_time)
                        print(f"LinkedIn content scheduled via Buffer.")
                        
                if platform in ["x", "all"]:
                    x_data = content_data.get("x_thread")
                    if x_data:
                        self._schedule_via_buffer(x_data, "x", schedule_time)
                        print(f"X thread scheduled via Buffer.")

            # Update database status
            log.status = "scheduled"
            try:
                log.published_at = datetime.now() if schedule_time == "now" else datetime.fromisoformat(schedule_time.replace('Z', '+00:00'))
            except ValueError:
                log.published_at = datetime.now()
            db.commit()

            return {"status": "success", "message": "Content successfully scheduled for publishing."}
            
        except Exception as e:
            db.rollback()
            print(f"Publishing Error: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            db.close()

    def _publish_to_webflow(self, blog_data: dict):
        """
        Scaffold logic for Webflow CMS API.
        """
        if not self.webflow_api_key or not self.webflow_collection_id:
            print("Webflow API keys not configured. Skipping actual HTTP request.")
            return

        url = f"https://api.webflow.com/collections/{self.webflow_collection_id}/items"
        headers = {
            "Authorization": f"Bearer {self.webflow_api_key}",
            "accept-version": "1.0.0",
            "content-type": "application/json"
        }
        
        payload = {
            "fields": {
                "name": blog_data.get("h1_title", "Untitled Blog"),
                "slug": blog_data.get("url_slug", "untitled"),
                "post-body": blog_data.get("body", ""),
                "meta-description": blog_data.get("meta_description", ""),
                "_archived": False,
                "_draft": False
            }
        }
        
        # Real HTTP Request commented out until keys are present
        # response = requests.post(url, json=payload, headers=headers)
        # response.raise_for_status()
        pass

    def _schedule_via_buffer(self, social_data: dict, platform: str, schedule_time: str):
        """
        Scaffold logic for Buffer API.
        """
        if not self.buffer_access_token:
            print("Buffer Access Token not configured. Skipping actual HTTP request.")
            return
            
        profile_id = self.buffer_profile_ids.get(platform)
        if not profile_id:
            print(f"Buffer Profile ID for {platform} not configured.")
            return

        url = "https://api.bufferapp.com/1/updates/create.json"
        
        text_content = ""
        if platform == "linkedin":
            text_content = social_data.get("post", "")
        elif platform == "x":
            tweets = social_data.get("tweets", [])
            text_content = "\n\n".join(tweets)

        payload = {
            "access_token": self.buffer_access_token,
            "profile_ids[]": profile_id,
            "text": text_content,
            "scheduled_at": schedule_time
        }
        
        # Real HTTP Request commented out until keys are present
        # response = requests.post(url, data=payload)
        # response.raise_for_status()
        pass
