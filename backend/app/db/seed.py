"""
Seed script: populates demo data on first startup.
Idempotent — checks for existing rows before inserting anything.
"""
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func

from .session import async_session_factory
from ..core.security import get_password_hash
from ..models.identity import Organization, OrgType, User, UserRole
from ..models.farm import Crop, Disease, Farm, Field
from ..models.video import Video, VideoStatus, Frame
from ..models.prediction import (
    Detection, DetectionClass, FrameDiagnosis,
    VideoDiagnosis, ConfidenceBand, DecisionAuthorityStatus,
)
from ..models.governance import ModelVersion, DeploymentStatus, AuditLog
from ..core.logging import logger

# ── Fixed deterministic UUIDs (stable across restarts) ───────────────────────
ID = {
    "org_fpo":      "00000000-0001-0001-0001-000000000001",
    "org_insurer":  "00000000-0001-0001-0001-000000000002",
    "user_admin":       "00000000-0002-0002-0002-000000000001",
    "user_farmer1":     "00000000-0002-0002-0002-000000000002",
    "user_farmer2":     "00000000-0002-0002-0002-000000000003",
    "user_agronomist":  "00000000-0002-0002-0002-000000000004",
    "user_enterprise":  "00000000-0002-0002-0002-000000000005",
    "crop_soybean":     "00000000-0003-0003-0003-000000000001",
    "crop_cotton":      "00000000-0003-0003-0003-000000000002",
    "dis_soybean_rust":      "00000000-0004-0004-0004-000000000001",
    "dis_soybean_blight":    "00000000-0004-0004-0004-000000000002",
    "dis_soybean_mosaic":    "00000000-0004-0004-0004-000000000003",
    "dis_soybean_frogeye":   "00000000-0004-0004-0004-000000000004",
    "dis_soybean_healthy":   "00000000-0004-0004-0004-000000000005",
    "dis_cotton_boll":       "00000000-0004-0004-0004-000000000006",
    "dis_cotton_wilt":       "00000000-0004-0004-0004-000000000007",
    "farm_1": "00000000-0005-0005-0005-000000000001",
    "farm_2": "00000000-0005-0005-0005-000000000002",
    "farm_3": "00000000-0005-0005-0005-000000000003",
    "field_1a": "00000000-0006-0006-0006-000000000001",
    "field_1b": "00000000-0006-0006-0006-000000000002",
    "field_2a": "00000000-0006-0006-0006-000000000003",
    "field_3a": "00000000-0006-0006-0006-000000000004",
    "video_1": "00000000-0007-0007-0007-000000000001",
    "video_2": "00000000-0007-0007-0007-000000000002",
    "video_3": "00000000-0007-0007-0007-000000000003",
    "video_4": "00000000-0007-0007-0007-000000000004",
    "frame_1_1": "00000000-0008-0008-0008-000000000001",
    "frame_1_2": "00000000-0008-0008-0008-000000000002",
    "frame_2_1": "00000000-0008-0008-0008-000000000003",
    "frame_3_1": "00000000-0008-0008-0008-000000000004",
    "det_1_1": "00000000-0009-0009-0009-000000000001",
    "det_1_2": "00000000-0009-0009-0009-000000000002",
    "det_3_1": "00000000-0009-0009-0009-000000000003",
    "mv_detector":   "00000000-0010-0010-0010-000000000001",
    "mv_classifier": "00000000-0010-0010-0010-000000000002",
}


def _dt(days_ago: int = 0, hours_ago: int = 0) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=days_ago, hours=hours_ago)


async def seed_database() -> None:
    """Run all seeds. No-op if data already exists."""
    async with async_session_factory() as session:
        # Guard: skip if crops already seeded
        result = await session.execute(select(func.count()).select_from(Crop))
        if result.scalar_one() > 0:
            logger.info("Seed: demo data already present — skipping.")
            return

        logger.info("Seed: populating demo data…")
        now = datetime.now(timezone.utc)

        # 1. Organisations ────────────────────────────────────────────────────
        session.add_all([
            Organization(id=ID["org_fpo"],     name="Vidarbha Soybean FPO",    org_type=OrgType.fpo,     created_at=_dt(30)),
            Organization(id=ID["org_insurer"], name="AgroShield Insurance Ltd.", org_type=OrgType.insurer, created_at=_dt(30)),
        ])

        # 2. Users ────────────────────────────────────────────────────────────
        session.add_all([
            User(id=ID["user_admin"],       email="admin@rakshak.ai",          phone="+919000000001", password_hash=get_password_hash("Admin@1234"),      role=UserRole.admin,       display_name="Rakshak Admin",       org_id=ID["org_fpo"],     created_at=_dt(30), updated_at=_dt(30)),
            User(id=ID["user_farmer1"],     email="rajan.patil@example.com",   phone="+919111111111", password_hash=get_password_hash("Farmer@1234"),     role=UserRole.farmer,      display_name="Rajan Patil",         org_id=ID["org_fpo"],     created_at=_dt(20), updated_at=_dt(20)),
            User(id=ID["user_farmer2"],     email="sunita.devi@example.com",   phone="+919222222222", password_hash=get_password_hash("Farmer@1234"),     role=UserRole.farmer,      display_name="Sunita Devi",         org_id=ID["org_fpo"],     created_at=_dt(15), updated_at=_dt(15)),
            User(id=ID["user_agronomist"],  email="dr.mehta@rakshak.ai",       phone="+919333333333", password_hash=get_password_hash("Agro@1234"),       role=UserRole.agronomist,  display_name="Dr. Priya Mehta",     org_id=None,              created_at=_dt(25), updated_at=_dt(25)),
            User(id=ID["user_enterprise"],  email="analyst@agroshield.com",    phone="+919444444444", password_hash=get_password_hash("Enterprise@1234"), role=UserRole.enterprise,  display_name="AgroShield Analyst",  org_id=ID["org_insurer"], created_at=_dt(10), updated_at=_dt(10)),
        ])

        # 3. Crops ────────────────────────────────────────────────────────────
        session.add_all([
            Crop(id=ID["crop_soybean"], name="Soybean", taxonomy_version="v1.0", active=True, created_at=_dt(60)),
            Crop(id=ID["crop_cotton"],  name="Cotton",  taxonomy_version="v1.0", active=True, created_at=_dt(60)),
        ])

        # 4. Diseases ─────────────────────────────────────────────────────────
        session.add_all([
            Disease(id=ID["dis_soybean_rust"],    crop_id=ID["crop_soybean"], name="Soybean Rust",             taxonomy_version="v1.0", active=True, created_at=_dt(60)),
            Disease(id=ID["dis_soybean_blight"],  crop_id=ID["crop_soybean"], name="Sudden Death Syndrome",    taxonomy_version="v1.0", active=True, created_at=_dt(60)),
            Disease(id=ID["dis_soybean_mosaic"],  crop_id=ID["crop_soybean"], name="Bean Pod Mottle Virus",    taxonomy_version="v1.0", active=True, created_at=_dt(60)),
            Disease(id=ID["dis_soybean_frogeye"], crop_id=ID["crop_soybean"], name="Frogeye Leaf Spot",        taxonomy_version="v1.0", active=True, created_at=_dt(60)),
            Disease(id=ID["dis_soybean_healthy"], crop_id=ID["crop_soybean"], name="Healthy",                  taxonomy_version="v1.0", active=True, created_at=_dt(60)),
            Disease(id=ID["dis_cotton_boll"],     crop_id=ID["crop_cotton"],  name="Boll Weevil Infestation",  taxonomy_version="v1.0", active=True, created_at=_dt(60)),
            Disease(id=ID["dis_cotton_wilt"],     crop_id=ID["crop_cotton"],  name="Fusarium Wilt",            taxonomy_version="v1.0", active=True, created_at=_dt(60)),
        ])

        # 5. Farms ────────────────────────────────────────────────────────────
        session.add_all([
            Farm(id=ID["farm_1"], owner_user_id=ID["user_farmer1"], org_id=ID["org_fpo"],     name="Patil Soybean Farm",   state="Maharashtra",    district="Nagpur",       created_at=_dt(18)),
            Farm(id=ID["farm_2"], owner_user_id=ID["user_farmer1"], org_id=ID["org_fpo"],     name="Patil North Block",    state="Maharashtra",    district="Wardha",       created_at=_dt(18)),
            Farm(id=ID["farm_3"], owner_user_id=ID["user_farmer2"], org_id=ID["org_fpo"],     name="Sunita Ji Ki Khet",    state="Madhya Pradesh", district="Hoshangabad",  created_at=_dt(12)),
        ])

        # 6. Fields ───────────────────────────────────────────────────────────
        session.add_all([
            Field(id=ID["field_1a"], farm_id=ID["farm_1"], name="Plot A — East", crop_id=ID["crop_soybean"], area_hectares=2.4, created_at=_dt(18)),
            Field(id=ID["field_1b"], farm_id=ID["farm_1"], name="Plot B — West", crop_id=ID["crop_soybean"], area_hectares=1.8, created_at=_dt(18)),
            Field(id=ID["field_2a"], farm_id=ID["farm_2"], name="North Field",   crop_id=ID["crop_soybean"], area_hectares=3.1, created_at=_dt(18)),
            Field(id=ID["field_3a"], farm_id=ID["farm_3"], name="Khet No. 1",    crop_id=ID["crop_cotton"],  area_hectares=1.5, created_at=_dt(12)),
        ])

        await session.flush()  # resolve FKs before videos/frames

        # 7. Model Versions ───────────────────────────────────────────────────
        session.add_all([
            ModelVersion(id=ID["mv_detector"],   model_name="soybean-detector-yolov8",         version_hash="sha256:abc123def456", training_dataset_version="dataset-v1.2", eval_metrics={"mAP50": 0.87, "precision": 0.91, "recall": 0.84},              deployment_status=DeploymentStatus.production, created_at=_dt(45)),
            ModelVersion(id=ID["mv_classifier"], model_name="soybean-classifier-efficientnet", version_hash="sha256:xyz789uvw012", training_dataset_version="dataset-v1.2", eval_metrics={"top1_acc": 0.93, "top3_acc": 0.98, "f1_macro": 0.91}, deployment_status=DeploymentStatus.production, created_at=_dt(45)),
        ])

        # 8. Videos ───────────────────────────────────────────────────────────
        session.add_all([
            Video(id=ID["video_1"], field_id=ID["field_1a"], uploaded_by=ID["user_farmer1"], status=VideoStatus.ready,      quality_score=0.88, gps_geohash="te7ud3", storage_path="uploads/demo/video_1.mp4", duration_seconds=18.4, device_metadata={"model": "Redmi Note 12", "os": "Android 13"}, total_frames_extracted=55, usable_frames_count=42, created_at=_dt(5),  updated_at=_dt(4)),
            Video(id=ID["video_2"], field_id=ID["field_1b"], uploaded_by=ID["user_farmer1"], status=VideoStatus.ready,      quality_score=0.95, gps_geohash="te7ud4", storage_path="uploads/demo/video_2.mp4", duration_seconds=22.1, device_metadata={"model": "Redmi Note 12", "os": "Android 13"}, total_frames_extracted=66, usable_frames_count=61, created_at=_dt(3),  updated_at=_dt(2)),
            Video(id=ID["video_3"], field_id=ID["field_2a"], uploaded_by=ID["user_farmer1"], status=VideoStatus.ready,      quality_score=0.72, gps_geohash="te7ud5", storage_path="uploads/demo/video_3.mp4", duration_seconds=14.0, device_metadata={"model": "Samsung Galaxy M33", "os": "Android 12"}, total_frames_extracted=42, usable_frames_count=28, created_at=_dt(1),  updated_at=_dt(0, hours_ago=3)),
            Video(id=ID["video_4"], field_id=ID["field_3a"], uploaded_by=ID["user_farmer2"], status=VideoStatus.processing, quality_score=None, gps_geohash=None,     storage_path="uploads/demo/video_4.mp4", duration_seconds=30.5, device_metadata={"model": "iPhone 13", "os": "iOS 17"},           total_frames_extracted=91, usable_frames_count=None, created_at=_dt(0, hours_ago=1), updated_at=_dt(0, hours_ago=1)),
        ])
        await session.flush()

        # 9. Frames ───────────────────────────────────────────────────────────
        session.add_all([
            Frame(id=ID["frame_1_1"], video_id=ID["video_1"], storage_path="uploads/demo/video_1/frame_001.jpg", blur_score=142.3, exposure_score=0.91, is_selected=True,  sequence_index=1,  created_at=_dt(5)),
            Frame(id=ID["frame_1_2"], video_id=ID["video_1"], storage_path="uploads/demo/video_1/frame_015.jpg", blur_score=138.7, exposure_score=0.88, is_selected=True,  sequence_index=15, created_at=_dt(5)),
            Frame(id=ID["frame_2_1"], video_id=ID["video_2"], storage_path="uploads/demo/video_2/frame_001.jpg", blur_score=201.0, exposure_score=0.96, is_selected=True,  sequence_index=1,  created_at=_dt(3)),
            Frame(id=ID["frame_3_1"], video_id=ID["video_3"], storage_path="uploads/demo/video_3/frame_008.jpg", blur_score=96.5,  exposure_score=0.79, is_selected=True,  sequence_index=8,  created_at=_dt(1)),
        ])
        await session.flush()

        # 10. Detections ──────────────────────────────────────────────────────
        DET_VER = "soybean-detector-yolov8@sha256:abc123def456"
        session.add_all([
            Detection(id=ID["det_1_1"], frame_id=ID["frame_1_1"], bbox={"x": 0.12, "y": 0.31, "w": 0.18, "h": 0.14}, detection_class=DetectionClass.diseased_leaf, detector_confidence=0.91, detector_model_version=DET_VER, created_at=_dt(5)),
            Detection(id=ID["det_1_2"], frame_id=ID["frame_1_2"], bbox={"x": 0.55, "y": 0.22, "w": 0.15, "h": 0.12}, detection_class=DetectionClass.lesion,        detector_confidence=0.87, detector_model_version=DET_VER, created_at=_dt(5)),
            Detection(id=ID["det_3_1"], frame_id=ID["frame_3_1"], bbox={"x": 0.33, "y": 0.45, "w": 0.20, "h": 0.16}, detection_class=DetectionClass.diseased_leaf, detector_confidence=0.73, detector_model_version=DET_VER, created_at=_dt(1)),
        ])
        await session.flush()

        # 11. Frame Diagnoses ─────────────────────────────────────────────────
        CLS_VER = "soybean-classifier-efficientnet@sha256:xyz789uvw012"
        session.add_all([
            FrameDiagnosis(id=str(uuid.uuid4()), detection_id=ID["det_1_1"], probability_distribution={"Soybean Rust": 0.82, "Frogeye Leaf Spot": 0.10, "Healthy": 0.05, "Bean Pod Mottle Virus": 0.03}, classifier_model_version=CLS_VER, created_at=_dt(5)),
            FrameDiagnosis(id=str(uuid.uuid4()), detection_id=ID["det_1_2"], probability_distribution={"Soybean Rust": 0.79, "Frogeye Leaf Spot": 0.13, "Healthy": 0.05, "Bean Pod Mottle Virus": 0.03}, classifier_model_version=CLS_VER, created_at=_dt(5)),
            FrameDiagnosis(id=str(uuid.uuid4()), detection_id=ID["det_3_1"], probability_distribution={"Frogeye Leaf Spot": 0.61, "Soybean Rust": 0.22, "Healthy": 0.10, "Bean Pod Mottle Virus": 0.07}, classifier_model_version=CLS_VER, created_at=_dt(1)),
        ])

        # 12. Video Diagnoses (aggregated roll-up) ────────────────────────────
        AGG_VER = "bayes-agg-v1.0"
        session.add_all([
            VideoDiagnosis(id=str(uuid.uuid4()), video_id=ID["video_1"], disease_id=ID["dis_soybean_rust"],    is_unknown=False, confidence=0.86, confidence_band=ConfidenceBand.high,   severity_level=2, affected_plant_estimate=0.34, supporting_frames=36, total_frames=42, aggregation_model_version=AGG_VER, decision_authority=DecisionAuthorityStatus.advisory_only, explanation="High-confidence Soybean Rust (Phakopsora pachyrhizi). Rust pustules on abaxial leaf surfaces in 36/42 frames. ~34% plant coverage. Severity: Moderate. Recommended: Apply fungicide (trifloxystrobin + tebuconazole) within 48 hrs.", created_at=_dt(5)),
            VideoDiagnosis(id=str(uuid.uuid4()), video_id=ID["video_2"], disease_id=ID["dis_soybean_healthy"], is_unknown=False, confidence=0.94, confidence_band=ConfidenceBand.high,   severity_level=0, affected_plant_estimate=0.00, supporting_frames=61, total_frames=61, aggregation_model_version=AGG_VER, decision_authority=DecisionAuthorityStatus.advisory_only, explanation="All 61 frames show healthy soybean plants. No lesions, discolouration, or structural anomalies detected. Continue standard agronomic practice.", created_at=_dt(3)),
            VideoDiagnosis(id=str(uuid.uuid4()), video_id=ID["video_3"], disease_id=ID["dis_soybean_frogeye"], is_unknown=False, confidence=0.61, confidence_band=ConfidenceBand.medium, severity_level=1, affected_plant_estimate=0.17, supporting_frames=19, total_frames=28, aggregation_model_version=AGG_VER, decision_authority=DecisionAuthorityStatus.advisory_only, explanation="Medium-confidence Frogeye Leaf Spot (Cercospora sojina). Circular grey-centre lesions in 19/28 frames. Severity: Mild. Agronomist verification recommended before treatment.", created_at=_dt(1)),
        ])

        # 13. Audit log ───────────────────────────────────────────────────────
        session.add(AuditLog(
            id=str(uuid.uuid4()),
            actor_user_id=ID["user_admin"],
            action="SEED_DEMO_DATA",
            entity_type="system",
            entity_id=None,
            metadata_json={"seeded_at": now.isoformat(), "version": "v1.0"},
            created_at=now,
        ))

        await session.commit()
        logger.info(
            "Seed: demo data inserted — "
            "2 orgs | 5 users | 2 crops | 7 diseases | 3 farms | 4 fields | "
            "4 videos | 4 frames | 3 detections | 3 video diagnoses."
        )
