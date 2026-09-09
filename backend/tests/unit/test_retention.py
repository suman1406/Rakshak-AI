from datetime import datetime, timedelta, timezone
import pytest
from app.core.config import settings
from app.models.identity import User, UserRole
from app.models.farm import Farm, Field
from app.models.video import Video, VideoStatus, Frame
from app.retention import expire_evidence


@pytest.mark.asyncio
async def test_retention_dry_run_then_expiry_preserves_report_records(test_db, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, 'LOCAL_STORAGE_DIR', str(tmp_path))
    user = User(email='retention@example.test', password_hash='unused', role=UserRole.farmer)
    test_db.add(user); await test_db.flush()
    farm = Farm(name='Retention farm', owner_user_id=user.id)
    test_db.add(farm); await test_db.flush()
    field = Field(farm_id=farm.id, name='Field')
    test_db.add(field); await test_db.flush()
    original = tmp_path / 'original.mp4'; original.write_bytes(b'video')
    image = tmp_path / 'frame.jpg'; image.write_bytes(b'image')
    now = datetime.now(timezone.utc)
    video = Video(field_id=field.id, uploaded_by=user.id, status=VideoStatus.ready, storage_path=str(original), created_at=now - timedelta(days=settings.EVIDENCE_RETENTION_DAYS + 1))
    test_db.add(video); await test_db.flush()
    frame = Frame(video_id=video.id, storage_path=str(image), sequence_index=1)
    test_db.add(frame); await test_db.commit()
    assert (await expire_evidence(test_db, now=now))['deleted'] == 0
    assert original.exists() and image.exists()
    assert (await expire_evidence(test_db, apply=True, now=now))['deleted'] == 1
    assert not original.exists() and not image.exists()
    assert await test_db.get(Video, video.id) is not None
    assert await test_db.get(Frame, frame.id) is not None
    assert (await expire_evidence(test_db, apply=True, now=now))['deleted'] == 0
