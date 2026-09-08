import pytest
from sqlalchemy import select, update
from app.models.video import Video, VideoStatus
from app.models.identity import User, UserRole
from app.models.farm import Farm, Field
from app.core.security import get_password_hash


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "initial_status",
    [
        VideoStatus.uploaded,
        VideoStatus.failed,
        VideoStatus.validating,
        VideoStatus.processing,
        VideoStatus.analyzing,
        VideoStatus.aggregating,
    ],
)
async def test_worker_claim_heals_in_flight_and_failed_statuses(test_db, initial_status):
    owner = User(email=f"worker-{initial_status.value}@test.local", password_hash=get_password_hash("Password123!"), role=UserRole.farmer)
    test_db.add(owner)
    await test_db.flush()

    farm = Farm(owner_user_id=owner.id, name="Worker Recovery Farm")
    test_db.add(farm)
    await test_db.flush()

    field = Field(farm_id=farm.id, name="Worker Recovery Field")
    test_db.add(field)
    await test_db.flush()

    video = Video(
        field_id=field.id,
        uploaded_by=owner.id,
        status=initial_status,
        storage_path="/tmp/recovery_test.mp4",
    )
    test_db.add(video)
    await test_db.commit()

    # Worker claim query pattern from app.worker
    claim = await test_db.execute(
        update(Video)
        .where(
            Video.id == video.id,
            Video.status.in_((
                VideoStatus.uploaded,
                VideoStatus.failed,
                VideoStatus.validating,
                VideoStatus.processing,
                VideoStatus.analyzing,
                VideoStatus.aggregating,
            )),
        )
        .values(status=VideoStatus.validating)
    )
    await test_db.commit()

    assert claim.rowcount == 1
    updated_video = (await test_db.execute(select(Video).where(Video.id == video.id))).scalar_one()
    assert updated_video.status == VideoStatus.validating


@pytest.mark.asyncio
@pytest.mark.parametrize("terminal_status", [VideoStatus.ready, VideoStatus.insufficient_evidence])
async def test_worker_claim_ignores_terminal_videos(test_db, terminal_status):
    owner = User(email=f"terminal-{terminal_status.value}@test.local", password_hash=get_password_hash("Password123!"), role=UserRole.farmer)
    test_db.add(owner)
    await test_db.flush()

    farm = Farm(owner_user_id=owner.id, name="Terminal Farm")
    test_db.add(farm)
    await test_db.flush()

    field = Field(farm_id=farm.id, name="Terminal Field")
    test_db.add(field)
    await test_db.flush()

    video = Video(
        field_id=field.id,
        uploaded_by=owner.id,
        status=terminal_status,
        storage_path="/tmp/terminal_test.mp4",
    )
    test_db.add(video)
    await test_db.commit()

    claim = await test_db.execute(
        update(Video)
        .where(
            Video.id == video.id,
            Video.status.in_((
                VideoStatus.uploaded,
                VideoStatus.failed,
                VideoStatus.validating,
                VideoStatus.processing,
                VideoStatus.analyzing,
                VideoStatus.aggregating,
            )),
        )
        .values(status=VideoStatus.validating)
    )
    await test_db.commit()

    assert claim.rowcount == 0
    video_after = (await test_db.execute(select(Video).where(Video.id == video.id))).scalar_one()
    assert video_after.status == terminal_status
