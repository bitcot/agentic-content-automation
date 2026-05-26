import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# Initialize Celery
# Make sure Redis is running locally: docker-compose up -d
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "inbound_lead_tasks",
    broker=redis_url,
    backend=redis_url
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_concurrency=2, # Claude API can be slow, run 2 concurrent tasks max
)

celery_app.autodiscover_tasks(["tasks"])
