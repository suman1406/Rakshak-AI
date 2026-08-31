import pytest
from sqlalchemy import select

from app.core.security import create_access_token, get_password_hash
from app.models.farm import Farm, Field
from app.models.identity import Organization, OrgType, User, UserRole
from app.models.prediction import ConfidenceBand, VideoDiagnosis
from app.models.verification import CorrectionType, Feedback, VerifiedLabel
from app.models.video import Video, VideoStatus


@pytest.mark.asyncio
async def test_feedback_and_verification_persist_for_scoped_diagnosis(client, test_db):
    organization = Organization(name="Shared review organization", org_type=OrgType.fpo)
    test_db.add(organization)
    await test_db.flush()
    farmer = User(
        email="farmer@review.test",
        password_hash=get_password_hash("Password123!"),
        role=UserRole.farmer,
        org_id=organization.id,
    )
    agronomist = User(
        email="agronomist@review.test",
        password_hash=get_password_hash("Password123!"),
        role=UserRole.agronomist,
        org_id=organization.id,
    )
    test_db.add_all([farmer, agronomist])
    await test_db.flush()
    farm = Farm(owner_user_id=farmer.id, org_id=organization.id, name="Review farm")
    test_db.add(farm)
    await test_db.flush()
    field = Field(farm_id=farm.id, name="Review field")
    test_db.add(field)
    await test_db.flush()
    video = Video(field_id=field.id, uploaded_by=farmer.id, status=VideoStatus.ready, storage_path="videos/review.mp4")
    test_db.add(video)
    await test_db.flush()
    diagnosis = VideoDiagnosis(
        video_id=video.id,
        confidence=0.6,
        confidence_band=ConfidenceBand.medium,
        aggregation_model_version="deterministic-test",
    )
    test_db.add(diagnosis)
    await test_db.commit()

    farmer_token = create_access_token(farmer.id, farmer.role.value, farmer.org_id)
    feedback_response = await client.post(
        f"/api/v1/diagnosis/{diagnosis.id}/feedback",
        json={"correction_type": "other", "note": "Please review the affected area."},
        headers={"Authorization": f"Bearer {farmer_token}"},
    )
    assert feedback_response.status_code == 201

    agronomist_token = create_access_token(agronomist.id, agronomist.role.value, agronomist.org_id)
    verification_response = await client.post(
        f"/api/v1/diagnosis/{diagnosis.id}/verify",
        json={
            "is_healthy_override": True,
            "severity_level": 0,
            "affected_plant_estimate_independent": 0.0,
            "notes": "No disease signs in the available evidence.",
        },
        headers={"Authorization": f"Bearer {agronomist_token}"},
    )
    assert verification_response.status_code == 201

    feedback = (await test_db.execute(select(Feedback))).scalar_one()
    verified_label = (await test_db.execute(select(VerifiedLabel))).scalar_one()
    assert feedback.farmer_user_id == farmer.id
    assert feedback.correction_type == CorrectionType.other
    assert verified_label.agronomist_id == agronomist.id
    assert verified_label.notes == "No disease signs in the available evidence."
