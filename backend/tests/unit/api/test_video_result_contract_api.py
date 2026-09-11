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


@pytest.mark.asyncio
async def test_analysis_and_report_returns_persisted_action_items(client, test_db):
    owner, video = await _owned_video(test_db, status=VideoStatus.ready)
    crop = Crop(name="Soybean")
    test_db.add(crop)
    await test_db.flush()
    rust = Disease(crop_id=crop.id, name="Soybean Rust")
    test_db.add(rust)
    await test_db.flush()

    custom_action_items = "1. Isolate infected patch\n2. Apply triazole fungicide within 48h"
    diagnosis = VideoDiagnosis(
        video_id=video.id,
        disease_id=rust.id,
        confidence=0.92,
        confidence_band=ConfidenceBand.high,
        severity_level=2,
        aggregation_model_version="controlled-test",
        explanation="Detected early pustules on soybean leaves.",
        action_items=custom_action_items,
    )
    test_db.add(diagnosis)
    await test_db.commit()

    token = create_access_token(owner.id, owner.role.value)
    
    # Check video analysis endpoint
    analysis_resp = await client.get(f"/api/v1/videos/{video.id}/analysis", headers={"Authorization": f"Bearer {token}"})
    assert analysis_resp.status_code == 200
    assert analysis_resp.json()["action_items"] == custom_action_items

    # Check diagnosis report endpoint
    diag_resp = await client.get(f"/api/v1/diagnosis/{diagnosis.id}", headers={"Authorization": f"Bearer {token}"})
    assert diag_resp.status_code == 200
    assert diag_resp.json()["action_items"] == custom_action_items


@pytest.mark.asyncio
async def test_analysis_and_report_falls_back_to_canned_when_action_items_none(client, test_db):
    owner, video = await _owned_video(test_db, status=VideoStatus.ready)
    crop = Crop(name="Soybean")
    test_db.add(crop)
    await test_db.flush()
    rust = Disease(crop_id=crop.id, name="Soybean Rust")
    test_db.add(rust)
    await test_db.flush()

    diagnosis = VideoDiagnosis(
        video_id=video.id,
        disease_id=rust.id,
        confidence=0.88,
        confidence_band=ConfidenceBand.high,
        severity_level=1,
        aggregation_model_version="controlled-test",
        explanation=None,
        action_items=None,
    )
    test_db.add(diagnosis)
    await test_db.commit()

    token = create_access_token(owner.id, owner.role.value)

    # Check video analysis endpoint fallback
    analysis_resp = await client.get(f"/api/v1/videos/{video.id}/analysis", headers={"Authorization": f"Bearer {token}"})
    assert analysis_resp.status_code == 200
    assert "fungicide" in analysis_resp.json()["action_items"].lower()

    # Check diagnosis report endpoint fallback
    diag_resp = await client.get(f"/api/v1/diagnosis/{diagnosis.id}", headers={"Authorization": f"Bearer {token}"})
    assert diag_resp.status_code == 200
    assert "fungicide" in diag_resp.json()["action_items"].lower()

