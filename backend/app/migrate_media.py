"""Copy legacy local evidence into configured private S3 storage.

Run on a host that still has the old evidence files. Dry-run is the default.
Local originals are intentionally retained until a separate backup review.
"""
import argparse
import asyncio
import json
from pathlib import Path
from sqlalchemy import select
from app.core.config import settings
from app.db.session import async_session_factory, engine
from app.media_storage import media_storage
from app.models.video import Video, Frame


async def migrate(db, apply=False):
    if settings.STORAGE_BACKEND != 's3':
        raise ValueError('Configure private S3 storage before migrating evidence')
    root = Path(settings.LOCAL_STORAGE_DIR).resolve()
    counts = {'eligible': 0, 'copied': 0, 'unavailable': 0}
    videos = (await db.execute(select(Video).where(Video.media_deleted_at.is_(None)))).scalars().all()
    for video in videos:
        frames = (await db.execute(select(Frame).where(Frame.video_id == video.id))).scalars().all()
        for row, prefix in [(video, 'videos'), *((frame, 'frames') for frame in frames)]:
            if row.storage_path.startswith('s3://'):
                continue
            source = Path(row.storage_path).resolve()
            if not source.is_relative_to(root) or not source.is_file() or source.is_symlink():
                counts['unavailable'] += 1
                continue
            counts['eligible'] += 1
            if apply:
                row.storage_path = media_storage.store(f'{prefix}/{video.id}/{source.name}', source)
                await db.commit()
                counts['copied'] += 1
    return counts


async def main(apply):
    try:
        async with async_session_factory() as db:
            print(json.dumps(await migrate(db, apply)))
    finally:
        await engine.dispose()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    asyncio.run(main(args.apply))
