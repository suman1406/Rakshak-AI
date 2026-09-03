import asyncio
import concurrent.futures
from datetime import datetime, timezone
from celery import Celery
from .core.config import settings
from .db.session import async_session_factory
from .models.video import Video, VideoStatus
from sqlalchemy import select, update

celery_app = Celery("rakshak", broker=settings.REDIS_URL, backend=settings.REDIS_URL)
celery_app.conf.task_default_queue = settings.CELERY_CPU_QUEUE
celery_app.conf.task_routes = {
    "app.worker.process_video": {"queue": settings.CELERY_CPU_QUEUE},
}

def _run_sync(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, coro).result()
    else:
        return asyncio.run(coro)

@celery_app.task(bind=True, max_retries=2, default_retry_delay=10, acks_late=True)
def process_video(self, video_id: str) -> str:
    from .modules.ingestion.service import ingestion_service

    async def run() -> None:
        async with async_session_factory() as db:
            claim = await db.execute(
                update(Video)
                .where(Video.id == video_id, Video.status.in_((VideoStatus.uploaded, VideoStatus.failed)))
                .values(status=VideoStatus.validating, retry_count=self.request.retries, job_started_at=datetime.now(timezone.utc))
            )
            if claim.rowcount != 1:
                return
            await db.commit()
        await ingestion_service.execute_processing_pipeline(video_id)

    try:
        _run_sync(run())
    except Exception as exc:
        async def mark_failure() -> None:
            async with async_session_factory() as db:
                video = (await db.execute(select(Video).where(Video.id == video_id))).scalar_one_or_none()
                if video:
                    video.retry_count = self.request.retries + 1
                    video.last_failure_at = datetime.now(timezone.utc)
                    video.error_detail = str(exc)[:1000]
                    await db.commit()
        _run_sync(mark_failure())
        raise self.retry(exc=exc)

    async def mark_complete() -> None:
        async with async_session_factory() as db:
            video = (await db.execute(select(Video).where(Video.id == video_id))).scalar_one_or_none()
            if video:
                video.job_completed_at = datetime.now(timezone.utc)
                await db.commit()
    _run_sync(mark_complete())
    return video_id
