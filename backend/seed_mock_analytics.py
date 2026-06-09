import os
import sys
from datetime import datetime, timedelta
import random

# Add current dir to sys path so we can import from backend modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from database import SessionLocal, engine
import models

# Ensure tables exist
models.Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    
    # 1. High Performing Posts (Contrarian, Specific, Data-driven)
    high_perf_1 = models.ContentLog(
        topic="Microservices vs Monolith for Seed Stage Startups",
        icp_score=0.92,
        platform="LinkedIn",
        content="""The biggest lie in modern software engineering is that you need microservices from Day 1. 

If you are a seed-stage startup with 3 engineers, splitting your app into 14 Docker containers doesn't make you "web scale." It makes you slow. 

We ran the numbers on our last 50 enterprise integrations. The teams using well-structured Ruby on Rails monoliths shipped features 4x faster and had 60% less DevOps overhead than the teams trying to copy Netflix's Kubernetes architecture. 

Stop doing resume-driven development. Start shipping value. 

#softwareengineering #cto #startups""",
        status="published",
        published_at=datetime.utcnow() - timedelta(days=5)
    )
    
    high_perf_2 = models.ContentLog(
        topic="The Hidden Cost of Cloud Egress Fees",
        icp_score=0.88,
        platform="X Thread",
        content="""Everyone talks about compute costs. No one talks about the silent killer: AWS Data Egress Fees. 

Here is how we accidentally burned $45,000 in a weekend, and the exact architectural change we made to ensure it never happens again. 🧵""",
        status="published",
        published_at=datetime.utcnow() - timedelta(days=3)
    )

    # 2. Low Performing Posts (Generic, Fluffy, Buzzwords)
    low_perf_1 = models.ContentLog(
        topic="The Future of AI in Enterprise",
        icp_score=0.45,
        platform="LinkedIn",
        content="""🚀 Exciting times ahead! AI is revolutionizing the way enterprises do business. 💡

From machine learning to generative models, the landscape is shifting rapidly. Companies must embrace innovation or risk being left behind in the digital transformation wave. 🌊

What are your thoughts on the future of AI? Let me know in the comments below! 👇

#AI #Innovation #DigitalTransformation #Future""",
        status="published",
        published_at=datetime.utcnow() - timedelta(days=7)
    )

    low_perf_2 = models.ContentLog(
        topic="5 Tips for Better Code Quality",
        icp_score=0.51,
        platform="Blog",
        content="""Writing clean code is essential for every developer. Here are 5 tips to improve your code quality:
1. Use meaningful variable names
2. Write unit tests
3. Refactor often
4. Keep functions small
5. Comment your code

Good code is the foundation of good software!""",
        status="published",
        published_at=datetime.utcnow() - timedelta(days=10)
    )

    db.add_all([high_perf_1, high_perf_2, low_perf_1, low_perf_2])
    db.commit()
    db.refresh(high_perf_1)
    db.refresh(high_perf_2)
    db.refresh(low_perf_1)
    db.refresh(low_perf_2)

    # Now assign performance metrics
    metrics = [
        models.PerformanceMetric(
            content_id=high_perf_1.id,
            impressions=45000,
            engagement_rate=4.8, # High
            clicks=320,
            conversions=14
        ),
        models.PerformanceMetric(
            content_id=high_perf_2.id,
            impressions=85000,
            engagement_rate=6.2, # Very High
            clicks=1100,
            conversions=45
        ),
        models.PerformanceMetric(
            content_id=low_perf_1.id,
            impressions=1200,
            engagement_rate=0.4, # Low
            clicks=5,
            conversions=0
        ),
        models.PerformanceMetric(
            content_id=low_perf_2.id,
            impressions=800,
            engagement_rate=0.2, # Very Low
            clicks=2,
            conversions=0
        )
    ]
    
    db.add_all(metrics)
    db.commit()
    db.close()
    
    print("Mock analytics data seeded successfully!")

if __name__ == "__main__":
    seed_data()
