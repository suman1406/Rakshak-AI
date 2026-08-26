from celery import Celery
from .config import settings

celery_app = Celery("rakshak", broker=settings.redis_url, backend=settings.redis_url)

@celery_app.task
def process_video(video_id: str) -> str:
    return video_id

