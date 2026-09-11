import asyncio
import concurrent.futures
from datetime import datetime, timezone, timedelta
from celery import Celery
from .core.config import settings
from .db.session import async_session_factory, engine
from .models.video import Video, VideoStatus
from sqlalchemy import select, update

celery_app = Celery("rakshak", broker=settings.REDIS_URL, backend=settings.REDIS_URL)
celery_app.conf.task_default_queue = settings.CELERY_CPU_QUEUE
celery_app.conf.task_routes = {
    "app.worker.process_video": {"queue": settings.CELERY_CPU_QUEUE},
}
celery_app.conf.update(task_soft_time_limit=600, task_time_limit=660,
    task_reject_on_worker_lost=True, broker_connection_retry_on_startup=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        'recover-stale-scans': {'task': 'app.worker.recover_stale_scans', 'schedule': 60.0},
        'expire-evidence-daily': {'task': 'app.worker.expire_old_evidence', 'schedule': 86400.0},
    })

def _run_sync(coro):
    async def isolated():
        try:
            return await coro
        finally:
            # Celery tasks use distinct event loops; no pooled connection may
            # survive its owning loop or be inherited by the next task.
            await engine.dispose()
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, isolated()).result()
    else:
        return asyncio.run(isolated())


async def recover_interrupted_scans(db):
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=15)
    result = await db.execute(update(Video).where(
        Video.status.in_([VideoStatus.uploaded, VideoStatus.validating, VideoStatus.processing, VideoStatus.analyzing, VideoStatus.aggregating]),
        Video.updated_at < cutoff,
    ).values(status=VideoStatus.failed, error_detail='Processing was interrupted. Retry this saved scan.', last_failure_at=datetime.now(timezone.utc)).execution_options(synchronize_session='fetch'))
    await db.commit()
    return result.rowcount


@celery_app.task
def recover_stale_scans():
    async def recover():
        async with async_session_factory() as db:
            return await recover_interrupted_scans(db)
    return _run_sync(recover())


@celery_app.task
def expire_old_evidence():
    from .retention import expire_evidence
    async def expire():
        async with async_session_factory() as db:
            return await expire_evidence(db, apply=True)
    return _run_sync(expire())

@celery_app.task(bind=True, max_retries=2, default_retry_delay=10, acks_late=True)
def process_video(self, video_id: str) -> str:
    from .modules.ingestion.service import ingestion_service

    async def run() -> bool:
        async with async_session_factory() as db:
            claim = await db.execute(
                update(Video)
                .where(Video.id == video_id, Video.status.in_((VideoStatus.uploaded, VideoStatus.failed)))
                .values(status=VideoStatus.validating, retry_count=self.request.retries, job_started_at=datetime.now(timezone.utc))
            )
            if claim.rowcount != 1:
                return False
            await db.commit()
        await ingestion_service.execute_processing_pipeline(video_id)
        return True

    try:
        if not _run_sync(run()):
            return video_id
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
