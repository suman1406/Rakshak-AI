import pytest
from sqlalchemy import func, select

from app.core.security import get_password_hash
from app.models.farm import Farm, Field
from app.models.identity import User, UserRole
from app.models.video import Frame, Video, VideoStatus
from app.modules.ingestion.service import ingestion_service


@pytest.mark.asyncio
async def test_terminal_video_does_not_reprocess_or_duplicate_frames(test_db):
    owner = User(email="idempotency@test.local", password_hash=get_password_hash("Password123!"), role=UserRole.farmer)
    test_db.add(owner)
    await test_db.flush()
    farm = Farm(owner_user_id=owner.id, name="Idempotency farm")
    test_db.add(farm)
    await test_db.flush()
    field = Field(farm_id=farm.id, name="Idempotency field")
    test_db.add(field)
    await test_db.flush()
    video = Video(field_id=field.id, uploaded_by=owner.id, status=VideoStatus.insufficient_evidence, storage_path="/tmp/not-processed.mp4")
    test_db.add(video)
    await test_db.flush()
    test_db.add(Frame(video_id=video.id, storage_path="/tmp/frame.jpg", sequence_index=1))
    await test_db.commit()

    await ingestion_service.execute_processing_pipeline(video.id, db_session=test_db)

    frame_count = (await test_db.execute(select(func.count(Frame.id)).where(Frame.video_id == video.id))).scalar_one()
    assert frame_count == 1
