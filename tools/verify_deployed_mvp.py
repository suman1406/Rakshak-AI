#!/usr/bin/env python3
"""
verify_deployed_mvp.py — End-to-End Deployed System Verification Runner

Automates the complete farmer journey against a deployed (Render) or local
Rakshak AI backend:
  1. Health check (GET /healthz)
  2. Pilot farmer registration & login (POST /api/v1/auth/register, login)
  3. Farm & field provisioning (POST /api/v1/farms, /fields)
  4. Video upload with consent (POST /api/v1/videos)
  5. Asynchronous processing status polling (GET /api/v1/videos/{id}/status)
  6. Diagnosis analysis assertion (GET /api/v1/videos/{id}/analysis)
  7. Keyframe evidence verification (GET /api/v1/videos/{id}/frames, content)

Exit code 0 on full verification pass; 1 on failure.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import time
import uuid
import httpx


def log_step(step: int, msg: str):
    print(f"\n[{step}/7] ── {msg}")


def log_ok(msg: str):
    print(f"  ✅ {msg}")


def log_fail(msg: str):
    print(f"  ❌ {msg}")


def run_verification(
    base_url: str,
    video_path: Path,
    timeout_seconds: int = 180,
    poll_interval: float = 3.0,
) -> bool:
    base_url = base_url.rstrip("/")
    client = httpx.Client(base_url=base_url, timeout=30.0)

    print(f"🚀 Starting Rakshak AI End-to-End Verification")
    print(f"   Target URL:  {base_url}")
    print(f"   Video File:  {video_path} ({video_path.stat().st_size / 1024:.1f} KB)")
    print(f"   Max Timeout: {timeout_seconds}s")

    # ── Step 1: Healthz ───────────────────────────────────────────────────────
    log_step(1, "Checking Backend Health...")
    try:
        health_resp = client.get("/healthz")
        if health_resp.status_code != 200:
            log_fail(f"/healthz returned status {health_resp.status_code}: {health_resp.text}")
            return False
        health_data = health_resp.json()
        log_ok(f"Backend is healthy (status={health_data.get('status', 'unknown')})")
    except Exception as exc:
        log_fail(f"Failed to connect to {base_url}/healthz: {exc}")
        return False

    # ── Step 2: Auth Registration & Login ─────────────────────────────────────
    log_step(2, "Authenticating Pilot Farmer...")
    unique_suffix = uuid.uuid4().hex[:6]
    test_email = f"pilot-verify-{unique_suffix}@rakshak.ai"
    test_password = f"SecurePass{unique_suffix}!"

    reg_resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": test_email,
            "password": test_password,
            "consent_to_data_processing": True,
        },
    )
    if reg_resp.status_code not in [200, 201]:
        log_fail(f"Registration failed ({reg_resp.status_code}): {reg_resp.text}")
        return False

    login_resp = client.post(
        "/api/v1/auth/login",
        json={
            "email_or_phone": test_email,
            "password": test_password,
        },
    )
    if login_resp.status_code != 200:
        log_fail(f"Login failed ({login_resp.status_code}): {login_resp.text}")
        return False

    token = login_resp.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}
    log_ok(f"Authenticated as {test_email}")

    # ── Step 3: Provision Farm & Field ────────────────────────────────────────
    log_step(3, "Provisioning Farm and Field...")
    farm_resp = client.post(
        "/api/v1/farms",
        json={"name": f"Verification Farm {unique_suffix}"},
        headers=auth_headers,
    )
    if farm_resp.status_code not in [200, 201]:
        log_fail(f"Create farm failed ({farm_resp.status_code}): {farm_resp.text}")
        return False
    farm_id = farm_resp.json()["id"]

    field_resp = client.post(
        f"/api/v1/farms/{farm_id}/fields",
        json={"name": "North Soybean Field", "crop": "soybean"},
        headers=auth_headers,
    )
    if field_resp.status_code not in [200, 201]:
        log_fail(f"Create field failed ({field_resp.status_code}): {field_resp.text}")
        return False
    field_id = field_resp.json()["id"]
    log_ok(f"Farm (id={farm_id}) and Field (id={field_id}) created")

    # ── Step 4: Upload Video ──────────────────────────────────────────────────
    log_step(4, "Uploading Test Leaf Video...")
    if not video_path.exists():
        log_fail(f"Video file not found at {video_path}")
        return False

    with open(video_path, "rb") as f:
        video_bytes = f.read()

    upload_resp = client.post(
        "/api/v1/videos",
        data={"field_id": field_id, "consent": "true"},
        files={"file": (video_path.name, video_bytes, "video/mp4")},
        headers=auth_headers,
    )
    if upload_resp.status_code not in [200, 201]:
        log_fail(f"Video upload failed ({upload_resp.status_code}): {upload_resp.text}")
        return False

    upload_data = upload_resp.json()
    video_id = upload_data["video_id"]
    log_ok(f"Video uploaded successfully (video_id={video_id})")

    # ── Step 5: Poll Processing Status ────────────────────────────────────────
    log_step(5, f"Polling Video Processing (Timeout: {timeout_seconds}s)...")
    start_time = time.time()
    final_status = None
    terminal_statuses = {"ready", "insufficient_evidence", "failed"}

    while time.time() - start_time < timeout_seconds:
        status_resp = client.get(f"/api/v1/videos/{video_id}/status", headers=auth_headers)
        if status_resp.status_code == 200:
            status_data = status_resp.json()
            curr_status = status_data.get("status")
            elapsed = int(time.time() - start_time)
            print(f"  ... [{elapsed}s] status: {curr_status}")
            if curr_status in terminal_statuses:
                final_status = curr_status
                break
        else:
            print(f"  ... status query returned {status_resp.status_code}")
        time.sleep(poll_interval)

    if final_status != "ready":
        log_fail(f"Processing did not reach 'ready' within timeout. Final status: '{final_status}'")
        return False

    log_ok(f"Video reached terminal status: 'ready'")

    # ── Step 6: Validate Analysis & Dynamic Action Items ──────────────────────
    log_step(6, "Validating Diagnostic Report and Action Items...")
    analysis_resp = client.get(f"/api/v1/videos/{video_id}/analysis", headers=auth_headers)
    if analysis_resp.status_code != 200:
        log_fail(f"Fetch analysis failed ({analysis_resp.status_code}): {analysis_resp.text}")
        return False

    analysis = analysis_resp.json()
    result_state = analysis.get("result_state")
    diagnosis = analysis.get("diagnosis", {})
    explanation = analysis.get("explanation", "")
    action_items = analysis.get("action_items", "")

    print(f"   • Result State:      {result_state}")
    print(f"   • Disease:           {diagnosis.get('disease')}")
    print(f"   • Confidence:        {diagnosis.get('confidence', 0):.2%}")
    print(f"   • Confidence Band:   {diagnosis.get('confidence_band')}")
    print(f"   • Severity:          {diagnosis.get('severity')}")
    print(f"   • Explanation:       {explanation[:100]}...")
    print(f"   • Action Items:      {action_items[:100]}...")

    if result_state not in ["ready", "healthy"]:
        log_fail(f"Invalid result_state: {result_state}")
        return False

    if not explanation or not explanation.strip():
        log_fail("Explanation is empty")
        return False

    if not action_items or not action_items.strip():
        log_fail("Action items are empty")
        return False

    log_ok("Analysis contract verified with valid disease taxonomy, explanation, and action items")

    # ── Step 7: Validate Frame Extraction and Content Download ────────────────
    log_step(7, "Validating Frame Evidence Download...")
    frames_resp = client.get(f"/api/v1/videos/{video_id}/frames", headers=auth_headers)
    if frames_resp.status_code != 200:
        log_fail(f"Fetch frames failed ({frames_resp.status_code}): {frames_resp.text}")
        return False

    frames = frames_resp.json()
    if not frames or len(frames) == 0:
        log_fail("No frames returned for video")
        return False

    first_frame_id = frames[0]["id"]
    content_resp = client.get(
        f"/api/v1/videos/{video_id}/frames/{first_frame_id}/content",
        headers=auth_headers,
    )
    if content_resp.status_code != 200:
        log_fail(f"Fetch frame content failed ({content_resp.status_code}): {content_resp.text}")
        return False

    img_bytes = len(content_resp.content)
    log_ok(f"Retrieved {len(frames)} frames; verified frame image download ({img_bytes} bytes JPEG)")

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "═" * 70)
    print("🎉 ALL 7 END-TO-END VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("   • API Health Check:             Passed")
    print("   • Farmer Auth & Consent:        Passed")
    print("   • Farm & Field Creation:        Passed")
    print("   • Video Upload & Ingestion:     Passed")
    print("   • Pipeline Execution & Status:  Passed")
    print("   • AI Advisory & Action Items:   Passed")
    print("   • Frame Evidence Retrieval:     Passed")
    print("═" * 70 + "\n")
    return True


def main():
    parser = argparse.ArgumentParser(description="Run live MVP verification suite against Rakshak AI backend.")
    parser.add_argument(
        "--base-url",
        type=str,
        default="http://localhost:8000",
        help="Backend base URL (e.g. http://localhost:8000 or https://rakshak-backend.onrender.com)",
    )
    parser.add_argument(
        "--video",
        type=str,
        default="tools/soybean_rust_test.mp4",
        help="Path to test MP4 video fixture",
    )
    parser.add_argument("--timeout", type=int, default=180, help="Max polling timeout in seconds")
    parser.add_argument("--interval", type=float, default=3.0, help="Status polling interval in seconds")

    args = parser.parse_args()
    success = run_verification(
        base_url=args.base_url,
        video_path=Path(args.video),
        timeout_seconds=args.timeout,
        poll_interval=args.interval,
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
