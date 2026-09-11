"""Evidence retention command. Defaults to a dry run; --apply removes media.

Reports and expert audit records remain available after media expiry.
Run daily with: python -m app.retention --apply
"""
import argparse
import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.config import settings
from app.db.session import async_session_factory
from app.media_storage import media_storage
from app.models.video import Video, VideoStatus


async def expire_evidence(db, *, apply=False, now=None):
    if settings.EVIDENCE_RETENTION_DAYS < 1:
        raise ValueError('Retention must be at least one day')
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(days=settings.EVIDENCE_RETENTION_DAYS)
    candidates = (await db.execute(select(Video).options(selectinload(Video.frames)).where(
        Video.created_at < cutoff, Video.media_deleted_at.is_(None),
        Video.status.in_([VideoStatus.ready, VideoStatus.failed, VideoStatus.insufficient_evidence])
    ).limit(500))).scalars().all()
    for video in candidates:
        if not apply:
            continue
        for frame in video.frames:
            media_storage.delete(frame.storage_path)
        media_storage.delete(video.storage_path)
        video.media_deleted_at = now
        await db.commit()
    if apply:
        media_storage.prune_cache()
    return {'eligible': len(candidates), 'deleted': len(candidates) if apply else 0, 'retention_days': settings.EVIDENCE_RETENTION_DAYS}


async def main(apply):
    import app.models  # register schema
    async with async_session_factory() as db:
        print(await expire_evidence(db, apply=apply))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    asyncio.run(main(parser.parse_args().apply))
