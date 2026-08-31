import pytest

from app.core.security import create_access_token, get_password_hash
from app.models.farm import Farm, Field
from app.models.identity import User, UserRole
from app.models.video import Frame, Video, VideoStatus


@pytest.mark.asyncio
async def test_scoped_user_can_fetch_frame_content(client, test_db, tmp_path):
    owner = User(
        email="evidence-owner@test.local",
        password_hash=get_password_hash("Password123!"),
        role=UserRole.farmer,
    )
    test_db.add(owner)
    await test_db.flush()
    farm = Farm(owner_user_id=owner.id, name="Evidence farm")
    test_db.add(farm)
    await test_db.flush()
    field = Field(farm_id=farm.id, name="Evidence field")
    test_db.add(field)
    await test_db.flush()
    video = Video(field_id=field.id, uploaded_by=owner.id, status=VideoStatus.ready, storage_path="/tmp/video.mp4")
    test_db.add(video)
    await test_db.flush()
    frame_path = tmp_path / "frame.jpg"
    frame_path.write_bytes(b"jpeg-test-content")
    frame = Frame(video_id=video.id, storage_path=str(frame_path), sequence_index=1)
    test_db.add(frame)
    await test_db.commit()

    token = create_access_token(owner.id, owner.role.value)
    response = await client.get(
        f"/api/v1/videos/{video.id}/frames/{frame.id}/content",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"
    assert response.content == b"jpeg-test-content"


@pytest.mark.asyncio
async def test_missing_frame_content_returns_not_found(client, test_db):
    owner = User(
        email="missing-evidence-owner@test.local",
        password_hash=get_password_hash("Password123!"),
        role=UserRole.farmer,
    )
    test_db.add(owner)
    await test_db.flush()
    farm = Farm(owner_user_id=owner.id, name="Missing evidence farm")
    test_db.add(farm)
    await test_db.flush()
    field = Field(farm_id=farm.id, name="Missing evidence field")
    test_db.add(field)
    await test_db.flush()
    video = Video(field_id=field.id, uploaded_by=owner.id, status=VideoStatus.ready, storage_path="/tmp/video.mp4")
    test_db.add(video)
    await test_db.flush()
    frame = Frame(video_id=video.id, storage_path="/tmp/not-present.jpg", sequence_index=1)
    test_db.add(frame)
    await test_db.commit()

    token = create_access_token(owner.id, owner.role.value)
    response = await client.get(
        f"/api/v1/videos/{video.id}/frames/{frame.id}/content",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
