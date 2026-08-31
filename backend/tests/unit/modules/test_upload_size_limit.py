import io

import pytest
from fastapi import HTTPException, UploadFile

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.farm import Farm, Field
from app.models.identity import User, UserRole
from app.modules.ingestion.service import ingestion_service


@pytest.mark.asyncio
async def test_oversized_upload_is_rejected_before_full_persistence(test_db, tmp_path, monkeypatch):
    owner = User(email="upload-limit@test.local", password_hash=get_password_hash("Password123!"), role=UserRole.farmer)
    test_db.add(owner)
    await test_db.flush()
    farm = Farm(owner_user_id=owner.id, name="Upload limit farm")
    test_db.add(farm)
    await test_db.flush()
    field = Field(farm_id=farm.id, name="Upload limit field")
    test_db.add(field)
    await test_db.commit()
    monkeypatch.setattr(settings, "LOCAL_STORAGE_DIR", str(tmp_path))
    monkeypatch.setattr(settings, "MAX_UPLOAD_BYTES", 4)
    upload = UploadFile(filename="oversized.mp4", file=io.BytesIO(b"12345"))

    with pytest.raises(HTTPException) as exc_info:
        await ingestion_service.init_upload(upload, field.id, owner.id, True, test_db)

    assert exc_info.value.status_code == 413
    assert list(tmp_path.rglob("*")) == []


@pytest.mark.asyncio
async def test_mislabeled_non_video_upload_is_rejected_and_cleaned_up(test_db, tmp_path, monkeypatch):
    owner = User(email="decode-limit@test.local", password_hash=get_password_hash("Password123!"), role=UserRole.farmer)
    test_db.add(owner)
    await test_db.flush()
    farm = Farm(owner_user_id=owner.id, name="Decode limit farm")
    test_db.add(farm)
    await test_db.flush()
    field = Field(farm_id=farm.id, name="Decode limit field")
    test_db.add(field)
    await test_db.commit()
    monkeypatch.setattr(settings, "LOCAL_STORAGE_DIR", str(tmp_path))
    upload = UploadFile(filename="not-a-video.mp4", file=io.BytesIO(b"not an mp4"))

    with pytest.raises(HTTPException) as exc_info:
        await ingestion_service.init_upload(upload, field.id, owner.id, True, test_db)

    assert exc_info.value.status_code == 422
    assert not list(tmp_path.rglob("*.mp4"))
