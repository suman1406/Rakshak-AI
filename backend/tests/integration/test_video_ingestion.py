import io
import tempfile
import cv2
import numpy as np
import pytest
from app.modules.ingestion.service import ingestion_service

def create_synthetic_mp4(num_frames=30, is_blurry=False, is_dark=False):
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        path = tmp.name

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(path, fourcc, 5.0, (128, 128))
    for i in range(num_frames):
        if is_dark:
            frame = np.full((128, 128, 3), 10, dtype=np.uint8)
        elif is_blurry:
            sharp = np.zeros((128, 128, 3), dtype=np.uint8)
            for y in range(0, 128, 8):
                for x in range(0, 128, 8):
                    if (x // 8 + y // 8) % 2 == 0:
                        sharp[y:y+8, x:x+8] = [255, 255, 255]
            frame = cv2.GaussianBlur(sharp, (31, 31), 15.0)
        else:
            # Sharp checkerboard with varying colors per frame
            frame = np.zeros((128, 128, 3), dtype=np.uint8)
            val = (i * 25) % 255
            for y in range(0, 128, 16):
                for x in range(0, 128, 16):
                    if (x // 16 + y // 16) % 2 == 0:
                        frame[y:y+16, x:x+16] = [255, val, 255 - val]

        out.write(frame)
    out.release()

    with open(path, "rb") as f:
        data = f.read()
    return data

@pytest.mark.asyncio
async def test_video_upload_consent_required(client):
    # Create farm & field first
    farm_res = await client.post("/api/v1/farms", json={"name": "Test Farm"})
    farm_id = farm_res.json()["id"]
    field_res = await client.post(f"/api/v1/farms/{farm_id}/fields", json={"name": "Field 1"})
    field_id = field_res.json()["id"]

    video_data = create_synthetic_mp4(5)
    files = {"file": ("video.mp4", video_data, "video/mp4")}
    data = {"field_id": field_id, "consent": "false"}

    res = await client.post("/api/v1/videos", data=data, files=files)
    assert res.status_code == 400
    assert "consent is required" in res.json()["detail"].lower()

@pytest.mark.asyncio
async def test_video_upload_and_pipeline_success(client, test_db):
    farm_res = await client.post("/api/v1/farms", json={"name": "Indore Soy Farm"})
    farm_id = farm_res.json()["id"]
    field_res = await client.post(f"/api/v1/farms/{farm_id}/fields", json={"name": "Soy Plot Alpha"})
    field_id = field_res.json()["id"]

    # 35 frames at 5 fps = 7 seconds -> extracts 7 frames (>= 5 threshold)
    video_bytes = create_synthetic_mp4(num_frames=35, is_blurry=False)
    files = {"file": ("good_video.mp4", video_bytes, "video/mp4")}
    data = {"field_id": field_id, "consent": "true"}

    upload_res = await client.post("/api/v1/videos", data=data, files=files)
    assert upload_res.status_code == 201
    upload_data = upload_res.json()
    video_id = upload_data["video_id"]
    assert upload_data["status"] == "uploaded"

    # Execute processing pipeline directly with test_db
    await ingestion_service.execute_processing_pipeline(video_id, db_session=test_db)

    # Check status endpoint
    status_res = await client.get(f"/api/v1/videos/{video_id}/status")
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert status_data["status"] == "ready"
    assert status_data["usable_frames_count"] >= 5
    assert status_data["quality_score"] > 50.0

    # Check frames endpoint
    frames_res = await client.get(f"/api/v1/videos/{video_id}/frames")
    assert frames_res.status_code == 200
    frames = frames_res.json()
    assert len(frames) >= 5
    assert any(f["is_selected"] for f in frames)

    # Check analysis endpoint
    analysis_res = await client.get(f"/api/v1/videos/{video_id}/analysis")
    assert analysis_res.status_code == 200
    analysis = analysis_res.json()
    assert analysis["crop"] == "soybean"
    assert "diagnosis" in analysis
    assert "evidence" in analysis
    assert "model_versions" in analysis
    assert analysis["model_versions"]["detector"] != ""

@pytest.mark.asyncio
async def test_video_insufficient_evidence_routing(client, test_db):
    farm_res = await client.post("/api/v1/farms", json={"name": "Dark Field Farm"})
    farm_id = farm_res.json()["id"]
    field_res = await client.post(f"/api/v1/farms/{farm_id}/fields", json={"name": "Dark Field"})
    field_id = field_res.json()["id"]

    # 30 dark/unusable frames -> all fail exposure check (< 5 usable)
    dark_video_bytes = create_synthetic_mp4(num_frames=30, is_dark=True)
    files = {"file": ("dark_video.mp4", dark_video_bytes, "video/mp4")}
    data = {"field_id": field_id, "consent": "true"}

    upload_res = await client.post("/api/v1/videos", data=data, files=files)
    assert upload_res.status_code == 201
    video_id = upload_res.json()["video_id"]

    # Execute processing pipeline with test_db
    await ingestion_service.execute_processing_pipeline(video_id, db_session=test_db)

    # Check status endpoint -> must be insufficient_evidence
    status_res = await client.get(f"/api/v1/videos/{video_id}/status")
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert status_data["status"] == "insufficient_evidence"
    assert status_data["usable_frames_count"] < 5
    assert "insufficient usable frames" in status_data["error_detail"].lower()
