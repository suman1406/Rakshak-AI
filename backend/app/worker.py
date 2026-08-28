import asyncio
from celery import Celery
from .core.config import settings

celery_app = Celery("rakshak", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

@celery_app.task
def process_video(video_id: str) -> str:
    from .modules.ingestion.service import ingestion_service
    asyncio.run(ingestion_service.execute_processing_pipeline(video_id))
    return video_id
