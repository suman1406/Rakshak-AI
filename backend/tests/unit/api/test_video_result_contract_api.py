import pytest

from app.core.security import create_access_token, get_password_hash
from app.models.farm import Crop, Disease, Farm, Field
from app.models.identity import User, UserRole
from app.models.prediction import ConfidenceBand, VideoDiagnosis
from app.models.video import Video, VideoStatus


async def _owned_video(test_db, *, status: VideoStatus) -> tuple[User, Video]:
    owner = User(email=f"result-{status.value}@test.local", password_hash=get_password_hash("Password123!"), role=UserRole.farmer)
    test_db.add(owner)
    await test_db.flush()
    farm = Farm(owner_user_id=owner.id, name="Result contract farm")
    test_db.add(farm)
    await test_db.flush()
    field = Field(farm_id=farm.id, name="Result contract field")
    test_db.add(field)
    await test_db.flush()
    video = Video(field_id=field.id, uploaded_by=owner.id, status=status, storage_path="/tmp/result.mp4", total_frames_extracted=6, usable_frames_count=5)
    test_db.add(video)
    await test_db.flush()
    return owner, video


@pytest.mark.asyncio
async def test_analysis_uses_persisted_healthy_taxonomy_not_a_fabricated_disease(client, test_db):
    owner, video = await _owned_video(test_db, status=VideoStatus.ready)
    crop = Crop(name="Soybean")
    test_db.add(crop)
    await test_db.flush()
    healthy = Disease(crop_id=crop.id, name="Healthy")
    test_db.add(healthy)
    await test_db.flush()
    diagnosis = VideoDiagnosis(
        video_id=video.id,
        disease_id=healthy.id,
        confidence=1.0,
        confidence_band=ConfidenceBand.high,
        severity_level=0,
        aggregation_model_version="controlled-test",
    )
    test_db.add(diagnosis)
    await test_db.commit()

    token = create_access_token(owner.id, owner.role.value)
    response = await client.get(f"/api/v1/videos/{video.id}/analysis", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["result_state"] == "healthy"
    assert payload["diagnosis"]["disease"] == "healthy"
    assert payload["diagnosis"]["severity"] == "None"
    assert "crop_confidence" not in payload
    assert set(payload["model_versions"]) == {"aggregation"}


@pytest.mark.asyncio
async def test_analysis_returns_actionable_insufficient_evidence_without_a_diagnosis(client, test_db):
    owner, video = await _owned_video(test_db, status=VideoStatus.insufficient_evidence)
    video.error_detail = "Only two independent usable frames were available. Retake in better light."
    await test_db.commit()

    token = create_access_token(owner.id, owner.role.value)
    response = await client.get(f"/api/v1/videos/{video.id}/analysis", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["result_state"] == "insufficient_evidence"
    assert payload["diagnosis"] is None
    assert "Retake" in payload["retake_guidance"]


@pytest.mark.asyncio
async def test_report_without_a_persisted_disease_is_unknown_not_soybean_rust(client, test_db):
    owner, video = await _owned_video(test_db, status=VideoStatus.ready)
    diagnosis = VideoDiagnosis(
        video_id=video.id,
        is_unknown=True,
        confidence=0.2,
        confidence_band=ConfidenceBand.low,
        aggregation_model_version="controlled-test",
    )
    test_db.add(diagnosis)
    await test_db.commit()

    token = create_access_token(owner.id, owner.role.value)
    response = await client.get(f"/api/v1/diagnosis/{diagnosis.id}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["result_state"] == "unknown"
    assert response.json()["disease"] == "unknown_other"
