import os
from celery import Celery

# Default to local redis if not configured in environment
REDIS_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

# Initialize Celery app
celery_app = Celery(
    "nyaan_vaas_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.workers.ocr_worker"]
)

# Optional Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
)
