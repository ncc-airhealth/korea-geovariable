import os

from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# Configure Celery
celery_app = Celery(
    "tasks",
    broker=os.getenv("REDIS_BROKER", "redis://redis:6379/0"),
    backend=os.getenv("REDIS_BACKEND", "redis://redis:6379/0"),
    include=["tasks"],
)

# Optional configuration settings
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],  # Ignore other content
    result_serializer="json",
    timezone="Asia/Seoul",
    enable_utc=True,
)

if __name__ == "__main__":
    celery_app.start()
