import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
import models
from datetime import datetime, timedelta
import json

def seed():
    db = SessionLocal()
    
    # High-performing post 1
    cl1 = models.ContentLog(
        topic="Open-Source LLMs for Enterprise",
        platform="linkedin",
        status="published",
        content=json.dumps({"linkedin": {"body": "Most enterprises think they need a massive $1M proprietary API budget for AI.\n\nThey don't.\n\nOpen-source models like Llama-3 running on bare metal can slash inference costs by 70% while keeping your IP strictly in-house.\n\nHere is how we did it for a Fortune 500 client: [Link]"}}),
        created_at=datetime.utcnow() - timedelta(days=5)
    )
    db.add(cl1)
    db.commit()
    db.refresh(cl1)
    
    pm1 = models.PerformanceMetric(
        content_id=cl1.id,
        impressions=15000,
        engagement_rate=4.8, # High!
        clicks=450,
        conversions=12
    )
    db.add(pm1)

    # Low-performing post 1
    cl2 = models.ContentLog(
        topic="AI in Healthcare",
        platform="linkedin",
        status="published",
        content=json.dumps({"linkedin": {"body": "Artificial Intelligence is transforming the healthcare industry. Many companies are adopting AI to improve patient outcomes and reduce costs. At Bitcot, we believe AI is the future. If you want to learn more about our AI solutions for healthcare, click the link below to read our latest whitepaper and let us know your thoughts in the comments."}}),
        created_at=datetime.utcnow() - timedelta(days=4)
    )
    db.add(cl2)
    db.commit()
    db.refresh(cl2)

    pm2 = models.PerformanceMetric(
        content_id=cl2.id,
        impressions=2000,
        engagement_rate=0.4, # Low!
        clicks=5,
        conversions=0
    )
    db.add(pm2)

    # High-performing post 2
    cl3 = models.ContentLog(
        topic="SaaS Architecture",
        platform="linkedin",
        status="published",
        content=json.dumps({"linkedin": {"body": "Monolith vs Microservices is the wrong debate.\n\nThe real question: Can your team deploy independently without breaking prod?\n\nStop over-engineering. Start with a modular monolith. Only break out microservices when scaling pain demands it. (Framework attached below). \n\nWhat's your biggest deployment bottleneck right now?"}}),
        created_at=datetime.utcnow() - timedelta(days=2)
    )
    db.add(cl3)
    db.commit()
    db.refresh(cl3)

    pm3 = models.PerformanceMetric(
        content_id=cl3.id,
        impressions=12500,
        engagement_rate=3.9, # High!
        clicks=310,
        conversions=8
    )
    db.add(pm3)

    db.commit()
    print("Seed complete. Added 3 posts and performance metrics.")

if __name__ == "__main__":
    seed()
