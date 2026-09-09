import sys
from pathlib import Path
import pytest

# Ensure repo root is on sys.path to import tools
repo_root = Path(__file__).resolve().parent.parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from tools.create_test_video import create_video_from_images
from app.modules.ingestion.service import ingestion_service
from app.db.catalog import ensure_disease_catalog


@pytest.mark.asyncio
async def test_synthetic_real_domain_video_pipeline(client, test_db, tmp_path):
    # 0. Seed disease taxonomy catalog (mimics app lifespan on startup)
    await ensure_disease_catalog(test_db)

    # 1. Synthesize a 55-frame test video from the authentic dataset split
    images_dir = repo_root / "model" / "dataset_split" / "test" / "soybean_rust"
    assert images_dir.exists(), "Dataset split directory for soybean_rust must exist"

    test_video_path = tmp_path / "test_rust_55.mp4"
    create_video_from_images(
        images_dir=images_dir,
        output_path=test_video_path,
        num_frames=55,
        fps=5.0,
        target_size=(256, 256),
    )
    assert test_video_path.exists()
    assert test_video_path.stat().st_size > 1000

    # 2. Register & authenticate test farmer
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "e2e-rust@rakshak.ai", "password": "Password123!", "consent_to_data_processing": True},
    )
    assert reg_resp.status_code in [200, 201]

    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email_or_phone": "e2e-rust@rakshak.ai", "password": "Password123!"},
    )
    assert login_resp.status_code == 200
    headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    # 3. Create Farm & Field
    farm_resp = await client.post("/api/v1/farms", json={"name": "E2E Farm"}, headers=headers)
    assert farm_resp.status_code in [200, 201]
    farm_id = farm_resp.json()["id"]

    field_resp = await client.post(f"/api/v1/farms/{farm_id}/fields", json={"name": "E2E Field"}, headers=headers)
    assert field_resp.status_code in [200, 201]
    field_id = field_resp.json()["id"]

    # 4. Upload synthesized authentic leaf video
    with open(test_video_path, "rb") as f:
        video_bytes = f.read()

    upload_resp = await client.post(
        "/api/v1/videos",
        data={"field_id": field_id, "consent": "true"},
        files={"file": ("test_rust.mp4", video_bytes, "video/mp4")},
        headers=headers,
    )
    assert upload_resp.status_code in [200, 201]
    video_id = upload_resp.json()["video_id"]

    # 5. Execute processing pipeline
    await ingestion_service.execute_processing_pipeline(video_id, db_session=test_db)

    # 6. Verify status endpoint -> ready
    status_resp = await client.get(f"/api/v1/videos/{video_id}/status", headers=headers)
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] == "ready"

    # 7. Verify analysis endpoint
    analysis_resp = await client.get(f"/api/v1/videos/{video_id}/analysis", headers=headers)
    assert analysis_resp.status_code == 200
    analysis = analysis_resp.json()
    assert analysis["result_state"] in ["ready", "healthy"]
    assert analysis["explanation"] is not None and len(analysis["explanation"]) > 0
    assert analysis["action_items"] is not None and len(analysis["action_items"]) > 0

    # 8. Verify frames endpoint and image content
    frames_resp = await client.get(f"/api/v1/videos/{video_id}/frames", headers=headers)
    assert frames_resp.status_code == 200
    frames = frames_resp.json()
    assert len(frames) >= 5

    first_frame_id = frames[0]["id"]
    content_resp = await client.get(f"/api/v1/videos/{video_id}/frames/{first_frame_id}/content", headers=headers)
    assert content_resp.status_code == 200
    assert len(content_resp.content) > 100
