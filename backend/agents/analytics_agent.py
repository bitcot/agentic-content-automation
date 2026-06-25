import os
from pydantic import BaseModel
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from database import SessionLocal
import models

class AnalyticsMetrics(BaseModel):
    linkedin_engagement_rate: float
    form_conversion_rate: float
    x_bookmark_rate: float
    top_performers: list
    under_performers: list
    time_series: list

class AnalyticsAgent:
    def __init__(self):
        self.ga4_credentials_path = os.getenv("GA4_CREDENTIALS_JSON")
        self.ga4_property_id = os.getenv("GA4_PROPERTY_ID")
        self.linkedin_access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        self.model_name = "claude-opus-4-7"

    def get_metrics(self) -> AnalyticsMetrics:
        """
        Fetches metrics from the database instead of hardcoding.
        """
        db = SessionLocal()
        try:
            metrics = db.query(models.PerformanceMetric, models.ContentLog).join(
                models.ContentLog, models.PerformanceMetric.content_id == models.ContentLog.id
            ).all()

            if not metrics:
                return AnalyticsMetrics(
                    linkedin_engagement_rate=0.0,
                    form_conversion_rate=0.0,
                    x_bookmark_rate=0.0,
                    top_performers=[],
                    under_performers=[]
                )

            total_eng = sum(m[0].engagement_rate for m in metrics)
            total_conv = sum(m[0].conversions for m in metrics) / max(sum(m[0].clicks for m in metrics), 1) * 100
            
            avg_eng = total_eng / len(metrics)
            avg_conv = total_conv / len(metrics)
            
            sorted_metrics = sorted(metrics, key=lambda x: x[0].engagement_rate, reverse=True)
            top = sorted_metrics[:3]
            bottom = sorted_metrics[-3:] if len(sorted_metrics) >= 6 else sorted_metrics[len(top):]

            def format_list(metric_list):
                return [
                    {
                        "id": pm.content_id, 
                        "topic": cl.topic, 
                        "engagement": pm.engagement_rate, 
                        "conversion": pm.conversions,
                        "date": pm.recorded_at.isoformat()
                    } 
                    for pm, cl in metric_list
                ]

            time_series = sorted([
                {"date": pm.recorded_at.strftime("%b %d"), "engagement": pm.engagement_rate}
                for pm, cl in metrics
            ], key=lambda x: x["date"])

            return AnalyticsMetrics(
                linkedin_engagement_rate=round(avg_eng, 2),
                form_conversion_rate=round(avg_conv, 2),
                x_bookmark_rate=2.1, # Mock for now
                top_performers=format_list(top),
                under_performers=format_list(bottom),
                time_series=time_series
            )
        finally:
            db.close()

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

            chat = ChatAnthropic(
                model=self.model_name,
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
                max_tokens=1024
            )
            response = chat.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_msg)
            ])
            rulebook = response.content.strip()

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
