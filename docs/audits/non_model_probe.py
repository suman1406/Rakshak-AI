"""Readiness audit probes; not an application fix or production test runner.

Run only in the disposable, network-disabled container described in the report.
Uses an in-memory database and fake processing outputs. No trained model runs.
Findings are printed as JSON; observing a bug is not a passing release test.
"""
import asyncio
import ast
import json
import logging
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
import numpy as np

sys.path.insert(0, "/audit")

from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from app.core.deps import get_db
from app.core.security import create_access_token, create_refresh_token
from app.db.base import Base
from app.main import app
from app.models.identity import Organization, OrgType, User, UserRole
from app.models.farm import Crop, Disease, Farm, Field
from app.models.video import Frame, Video, VideoStatus
from app.models.prediction import ConfidenceBand, VideoDiagnosis
from app.models.verification import VerifiedLabel
from app.modules.ingestion.service import ingestion_service
from app.modules.processing.quality import FrameQualityResult

logging.getLogger("rakshak").disabled = True


def show(name, **details):
    print(json.dumps({"probe": name, **details}, default=str))


def headers(user):
    return {"Authorization": "Bearer " + create_access_token(user.id, user.role.value, user.org_id)}


async def main():
    paths = list(Path("/audit/app").rglob("*.py"))
    for path in paths:
        ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    show("backend_python_syntax", files=len(paths), status="parsed")
    # Same sharp frame repeated: duplicates must not count as independent evidence.
    pixels = np.random.default_rng(42).integers(50, 200, (128,128,3), dtype=np.uint8)
    repeats = [SimpleNamespace(sequence_index=i, file_path=f"/tmp/repeat-{i}.jpg", image=pixels) for i in range(6)]
    results, usable, _ = ingestion_service.quality_filter.evaluate_and_filter_frames(repeats)
    show("identical_noise_frames_not_deduplicated", usable=usable, selected=sum(r.is_selected for r in results))
    blocks = (((np.indices((128,128)).sum(axis=0)//16)%2)*150+50).astype(np.uint8)
    blocks = np.repeat(blocks[:,:,None],3,axis=2)
    repeats = [SimpleNamespace(sequence_index=i, file_path=f"/tmp/block-{i}.jpg", image=blocks) for i in range(6)]
    results, usable, _ = ingestion_service.quality_filter.evaluate_and_filter_frames(repeats)
    show("duplicate_evidence_threshold", usable=usable, selected=sum(r.is_selected for r in results), minimum_required=5)
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as db:
        db.add_all([Organization(id="a", name="A", org_type=OrgType.fpo),
                    Organization(id="b", name="B", org_type=OrgType.fpo)])
        await db.flush()
        farmer = User(id="farmer-a", role=UserRole.farmer, org_id="a", password_hash="unused")
        other = User(id="farmer-b", role=UserRole.farmer, org_id="b", password_hash="unused")
        enterprise = User(id="enterprise-a", role=UserRole.enterprise, org_id="a", password_hash="unused")
        agro = User(id="agro-a", role=UserRole.agronomist, org_id="a", password_hash="unused")
        db.add_all([farmer, other, enterprise, agro])
        db.add(Crop(id="crop", name="Soybean"))
        await db.flush()
        db.add_all([Farm(id="farm-a", name="A", owner_user_id=farmer.id, org_id="a"),
                    Farm(id="farm-b", name="B", owner_user_id=other.id, org_id="b")])
        await db.flush()
        db.add_all([Field(id="field-a", farm_id="farm-a", name="A", crop_id="crop"),
                    Disease(id="disease-uuid", crop_id="crop", name="Healthy")])
        await db.flush()
        db.add_all([Video(id="v", field_id="field-a", uploaded_by=farmer.id, storage_path="/tmp/nonexistent", status=VideoStatus.ready),
                    Video(id="poor", field_id="field-a", uploaded_by=farmer.id, storage_path="/tmp/nonexistent", status=VideoStatus.insufficient_evidence)])
        await db.flush()
        db.add_all([VideoDiagnosis(id="diag", video_id="v", disease_id="disease-uuid", confidence=.95, confidence_band=ConfidenceBand.high, severity_level=0, aggregation_model_version="audit-fixture"),
                    Frame(id="frame", video_id="v", storage_path="/tmp/nonexistent.jpg", sequence_index=0)])
        await db.commit()

        async def override_db():
            yield db
        app.dependency_overrides[get_db] = override_db
        async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url="http://audit") as client:
            res = await client.post("/api/v1/auth/register", json={"email":"audit@example.test", "password":"x", "role":"admin"})
            show("public_admin_registration_weak_password", status=res.status_code, role=res.json().get("role"))
            res = await client.get("/api/v1/auth/me", headers={"Authorization":"Bearer "+create_refresh_token(farmer.id)})
            show("refresh_token_as_access_token", status=res.status_code)
            res = await client.get("/api/v1/farms/farm-b", headers=headers(enterprise))
            show("cross_tenant_farm_read_control", status=res.status_code)
            res = await client.post("/api/v1/farms/farm-b/fields", headers=headers(enterprise), json={"name":"cross-tenant-write"})
            show("cross_tenant_field_creation", status=res.status_code, farm_id=res.json().get("farm_id"))
            res = await client.post("/api/v1/diagnosis/diag/feedback", headers=headers(farmer), json={"correction_type":"other", "note":"audit"})
            show("feedback_route", status=res.status_code, body=res.text[:160])
            res = await client.post("/api/v1/diagnosis/diag/verify", headers=headers(agro), json={"severity_level":0, "affected_plant_estimate_independent":0, "is_healthy_override":True})
            show("verification_route", status=res.status_code, body=res.text[:160])
            res = await client.get("/api/v1/videos/v/frames/frame/content", headers=headers(farmer))
            show("frame_content", status=res.status_code, body=res.text[:160])
            res = await client.get("/api/v1/videos/poor/analysis", headers=headers(farmer))
            show("insufficient_evidence_report", status=res.status_code, body=res.json())
            res = await client.get("/api/v1/diagnosis/diag", headers=headers(farmer))
            show("disease_id_vs_slug", status=res.status_code, disease=res.json().get("disease"), headline=res.json().get("headline"))
            res = await client.get("/api/v1/farms/farm-a", headers=headers(farmer))
            show("farm_detail_field_list", status=res.status_code, has_fields="fields" in res.json())
            db.add(VerifiedLabel(video_diagnosis_id="diag", agronomist_id=agro.id, is_healthy_override=True))
            await db.commit()
            res = await client.get("/api/v1/agronomist/queue", headers=headers(agro))
            show("reviewed_case_stays_in_queue", status=res.status_code, count=len(res.json()))

            # Actual ingestion orchestration, with quality/inference replaced by controlled data.
            healthy = [SimpleNamespace(is_unknown=False, quality_score=90, avg_probability_distribution={"healthy":1.0}) for _ in range(5)]
            quality = [FrameQualityResult(i, f"/tmp/audit-{i}.jpg", 90, 90, 90, True, True) for i in range(5)]
            db.add(Video(id="healthy-probe", field_id="field-a", uploaded_by=farmer.id, storage_path="/tmp/unused"))
            await db.commit()
            with patch.object(ingestion_service.extractor, "extract_frames", return_value=[None]*5), patch.object(ingestion_service.quality_filter, "evaluate_and_filter_frames", return_value=(quality,5,90)), patch.object(ingestion_service._inference, "run_frame_inference", AsyncMock(return_value=healthy)):
                await ingestion_service.execute_processing_pipeline("healthy-probe", db_session=db)
                row = (await db.execute(select(VideoDiagnosis).where(VideoDiagnosis.video_id=="healthy-probe"))).scalar_one()
                res = await client.get("/api/v1/videos/healthy-probe/analysis", headers=headers(farmer))
                show("healthy_processing_serialization", saved_severity=row.severity_level, saved_disease=row.disease_id, api_diagnosis=res.json().get("diagnosis"))

            db.add(Video(id="retry-probe", field_id="field-a", uploaded_by=farmer.id, storage_path="/tmp/unused"))
            await db.commit()
            with patch.object(ingestion_service.extractor, "extract_frames", return_value=[None]*5), patch.object(ingestion_service.quality_filter, "evaluate_and_filter_frames", return_value=(quality,5,90)), patch.object(ingestion_service._inference, "run_frame_inference", AsyncMock(side_effect=[RuntimeError("audit transient failure"),healthy])):
                try:
                    await ingestion_service.execute_processing_pipeline("retry-probe", db_session=db)
                except RuntimeError:
                    pass
                await ingestion_service.execute_processing_pipeline("retry-probe", db_session=db)
                count = await db.scalar(select(func.count(Frame.id)).where(Frame.video_id=="retry-probe"))
                show("processing_retry_duplicates_frames", frames=count, expected_unique=5)

    app.dependency_overrides.clear()
    await engine.dispose()
    # Uses the container's /tmp SQLite database, never a user database.
    try:
        async with app.router.lifespan_context(app):
            pass
        show("sqlite_startup", status="started")
    except Exception as exc:
        show("sqlite_startup", error=type(exc).__name__, detail=str(exc).splitlines()[0])
    # Reproduce the URL normalization in alembic/env.py without connecting anywhere.
    try:
        url="postgresql+psycopg://unused:unused@localhost/unused".replace("+psycopg", "")
        create_engine(url)
        show("alembic_postgres_driver", status="driver_loaded")
    except Exception as exc:
        show("alembic_postgres_driver", error=type(exc).__name__, detail=str(exc))


if __name__ == "__main__":
    asyncio.run(main())
