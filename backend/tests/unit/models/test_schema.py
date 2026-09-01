import pytest
from app.models.farm import Crop, Disease, Farm, Field
from app.models.identity import Organization, OrgType, User, UserRole
from app.models.prediction import (
    ConfidenceBand,
    DecisionAuthorityStatus,
    Detection,
    DetectionClass,
    FrameDiagnosis,
    VideoDiagnosis,
)
from app.models.verification import CorrectionType, Feedback, SourceChannel, VerifiedLabel
from app.models.video import Frame, Video, VideoStatus

@pytest.mark.asyncio
async def test_schema_model_invariants(test_db):
    # 1. Create Organization & User
    org = Organization(name="Test FPO Org", org_type=OrgType.fpo)
    test_db.add(org)
    await test_db.flush()

    user = User(
        email="farmer1@rakshak.ai",
        password_hash="hash123",
        role=UserRole.farmer,
        org_id=org.id,
        display_name="Ramesh",
    )
    agronomist = User(
        email="agro1@rakshak.ai",
        password_hash="hash456",
        role=UserRole.agronomist,
        display_name="Dr. Sharma",
    )
    test_db.add_all([user, agronomist])
    await test_db.flush()

    # 2. Create Crop & Disease Taxonomy
    crop = Crop(name="Soybean", taxonomy_version="v1.0")
    test_db.add(crop)
    await test_db.flush()

    disease = Disease(crop_id=crop.id, name="Soybean Rust", taxonomy_version="v1.0")
    test_db.add(disease)
    await test_db.flush()

    # 3. Create Farm & Field
    farm = Farm(owner_user_id=user.id, name="Green Acres", district="Indore", state="Madhya Pradesh")
    test_db.add(farm)
    await test_db.flush()

    field = Field(farm_id=farm.id, name="Plot 1 - North", crop_id=crop.id, area_hectares=2.5)
    test_db.add(field)
    await test_db.flush()

    # 4. Create Video & Frame
    video = Video(
        field_id=field.id,
        uploaded_by=user.id,
        status=VideoStatus.uploaded,
        storage_path="videos/sample_video.mp4",
    )
    test_db.add(video)
    await test_db.flush()

    frame = Frame(
        video_id=video.id,
        storage_path="frames/sample_001.jpg",
        blur_score=94.5,
        exposure_score=85.0,
        is_selected=True,
        sequence_index=1,
    )
    test_db.add(frame)
    await test_db.flush()

    # 5. Create Detection with mandatory detector_model_version
    detection = Detection(
        frame_id=frame.id,
        bbox={"x": 0.1, "y": 0.2, "w": 0.3, "h": 0.4},
        detection_class=DetectionClass.diseased_leaf,
        detector_confidence=0.92,
        detector_model_version="yolo11n-plantdoc-v1",
    )
    test_db.add(detection)
    await test_db.flush()

    # 6. Create FrameDiagnosis with full probability distribution & classifier_model_version
    frame_diag = FrameDiagnosis(
        detection_id=detection.id,
        probability_distribution={"soybean_rust": 0.88, "bacterial_blight": 0.08, "healthy": 0.04},
        classifier_model_version="effnet-b0-v1",
    )
    test_db.add(frame_diag)
    await test_db.flush()

    # 7. Create VideoDiagnosis with decision_authority = advisory_only invariant
    video_diag = VideoDiagnosis(
        video_id=video.id,
        disease_id=disease.id,
        confidence=0.86,
        confidence_band=ConfidenceBand.medium,
        severity_level=2,
        affected_plant_estimate=0.22,
        supporting_frames=12,
        total_frames=16,
        aggregation_model_version="bayes-v1",
        decision_authority=DecisionAuthorityStatus.advisory_only,
    )
    test_db.add(video_diag)
    await test_db.flush()

    # Assert invariant: decision authority must be advisory_only
    assert video_diag.decision_authority == DecisionAuthorityStatus.advisory_only
    assert video_diag.aggregation_model_version == "bayes-v1"

    # 8. Create VerifiedLabel (structurally separate from VideoDiagnosis)
    verified = VerifiedLabel(
        video_diagnosis_id=video_diag.id,
        agronomist_id=agronomist.id,
        disease_id=disease.id,
        severity_level=2,
        affected_plant_estimate_independent=0.20,
        source_channel=SourceChannel.neutral_agronomist,
    )
    test_db.add(verified)
    await test_db.flush()

    # 9. Create Feedback from farmer
    feedback = Feedback(
        video_diagnosis_id=video_diag.id,
        farmer_user_id=user.id,
        correction_type=CorrectionType.other,
        note="Confirmed rust visual signs on lower leaves.",
    )
    test_db.add(feedback)
    await test_db.commit()

    assert verified.id is not None
    assert feedback.id is not None
    assert feedback.trust_weight == 0.2
