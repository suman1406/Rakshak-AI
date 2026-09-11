from datetime import datetime, timedelta, timezone
import pytest
from app.models.video import Video, VideoStatus
from app.worker import recover_interrupted_scans


@pytest.mark.asyncio
async def test_recovery_only_marks_stale_nonterminal_scans(test_db):
    old = datetime.now(timezone.utc) - timedelta(minutes=16)
    recent = datetime.now(timezone.utc)
    interrupted = Video(field_id='field', uploaded_by='owner', storage_path='saved.mp4', status=VideoStatus.analyzing, updated_at=old)
    active = Video(field_id='field', uploaded_by='owner', storage_path='saved.mp4', status=VideoStatus.analyzing, updated_at=recent)
    completed = Video(field_id='field', uploaded_by='owner', storage_path='saved.mp4', status=VideoStatus.ready, updated_at=old)
    test_db.add_all([interrupted, active, completed])
    await test_db.commit()
    assert await recover_interrupted_scans(test_db) == 1
    for video in (interrupted, active, completed):
        await test_db.refresh(video)
    assert interrupted.status == VideoStatus.failed
    assert interrupted.storage_path == 'saved.mp4'
    assert active.status == VideoStatus.analyzing
    assert completed.status == VideoStatus.ready
    assert await recover_interrupted_scans(test_db) == 0
