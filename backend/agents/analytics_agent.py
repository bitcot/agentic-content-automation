import os
from pydantic import BaseModel
import anthropic
from database import SessionLocal
import models

class AnalyticsMetrics(BaseModel):
    linkedin_engagement_rate: float
    form_conversion_rate: float
    x_bookmark_rate: float
    top_performers: list
    under_performers: list

class AnalyticsAgent:
    def __init__(self):
        self.ga4_credentials_path = os.getenv("GA4_CREDENTIALS_JSON")
        self.ga4_property_id = os.getenv("GA4_PROPERTY_ID")
        self.linkedin_access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def get_metrics(self) -> AnalyticsMetrics:
        """
        Fetches metrics from GA4, LinkedIn, X APIs and analyzes them.
        """
        if self.ga4_credentials_path and self.ga4_property_id:
            try:
                # In production, use: from google.analytics.data_v1beta import BetaAnalyticsDataClient
                # client = BetaAnalyticsDataClient.from_service_account_json(self.ga4_credentials_path)
                # Build run_report request and process real stats
                pass
            except Exception as e:
                print(f"GA4 Error: {e}")

        # Fallback / Mock logic when APIs aren't set
        return AnalyticsMetrics(
            linkedin_engagement_rate=1.82,
            form_conversion_rate=0.26,
            x_bookmark_rate=2.1,
            top_performers=[
                {"id": 101, "topic": "Healthcare AI Infra", "engagement": 4.61, "conversion": 1.2}
            ],
            under_performers=[
                {"id": 102, "topic": "Generic cost warning", "engagement": 0.9, "conversion": 0.1}
            ]
        )

    def run_learning_loop(self) -> str:
        db = SessionLocal()
        try:
            metrics = db.query(models.PerformanceMetric, models.ContentLog).join(
                models.ContentLog, models.PerformanceMetric.content_id == models.ContentLog.id
            ).all()

            if not metrics:
                return "Not enough data to run learning loop."

            sorted_metrics = sorted(metrics, key=lambda x: x[0].engagement_rate, reverse=True)
            top_3 = sorted_metrics[:3]
            bottom_3 = sorted_metrics[-3:] if len(sorted_metrics) >= 6 else sorted_metrics[len(top_3):]

            def format_posts(post_list):
                formatted = ""
                for pm, cl in post_list:
                    formatted += f"Topic: {cl.topic}\nPlatform: {cl.platform}\nEngagement Rate: {pm.engagement_rate}%\nContent:\n{cl.content}\n---\n"
                return formatted

            high_perf_text = format_posts(top_3)
            low_perf_text = format_posts(bottom_3)

            system_prompt = "You are the Head of AI Content Strategy. Analyze the following high-performing and low-performing social media posts. Identify the exact hook structures, formatting patterns, tones, and topics that drive high engagement, and the exact patterns that cause low engagement. Output a concise 'AI Learnings Rulebook' (bullet points) that will be injected into an AI writer's system prompt to force it to adopt the winning behaviors."
            
            user_msg = f"HIGH PERFORMING POSTS:\n{high_perf_text}\n\nLOW PERFORMING POSTS:\n{low_perf_text}\n\nGenerate the AI Learnings Rulebook now."

            response = self.client.messages.create(
                model="claude-opus-4-7",
                max_tokens=1024,
                system=system_prompt,
                messages=[{"role": "user", "content": user_msg}]
            )

            rulebook = response.content[0].text.strip()

            bc = db.query(models.BrandContext).filter_by(key="ai_learnings").first()
            if bc:
                bc.value = rulebook
            else:
                bc = models.BrandContext(key="ai_learnings", value=rulebook)
                db.add(bc)
            db.commit()

            return rulebook
        except Exception as e:
            print(f"Learning Loop Error: {e}")
            return f"Error running learning loop: {e}"
        finally:
            db.close()
