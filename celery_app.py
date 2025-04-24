from celery import Celery

# Configure Celery
celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",  # Default Redis URL
    backend="redis://localhost:6379/0",  # Default Redis URL
    include=["tasks"],  # List of modules to import when the worker starts
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
