import pytest
from app.core.security import create_access_token, get_password_hash
from app.models.identity import User, UserRole
from app.models.farm import Farm, Field
from app.models.video import Video, VideoStatus
from app.models.prediction import VideoDiagnosis, ConfidenceBand

@pytest.mark.asyncio
async def test_independent_farmer_review_shares_only_requested_scan(client, test_db):
    farmer = User(email="owner@scope.test", password_hash=get_password_hash("Password123!"), role=UserRole.farmer)
    expert = User(email="expert@scope.test", password_hash=get_password_hash("Password123!"), role=UserRole.agronomist)
    test_db.add_all([farmer, expert]); await test_db.flush()
    farm = Farm(name="Private farm", owner_user_id=farmer.id)
    test_db.add(farm); await test_db.flush()
    field = Field(name="Soybean", farm_id=farm.id)
    test_db.add(field); await test_db.flush()
    videos = [Video(field_id=field.id, uploaded_by=farmer.id, status=VideoStatus.ready, storage_path="/tmp/test.mp4") for _ in range(2)]
    test_db.add_all(videos); await test_db.flush()
    diagnoses = [VideoDiagnosis(video_id=v.id, confidence=.4, confidence_band=ConfidenceBand.low, aggregation_model_version="test", is_unknown=True) for v in videos]
    test_db.add_all(diagnoses); await test_db.commit()
    owner_headers = {"Authorization": "Bearer " + create_access_token(farmer.id, "farmer")}
    expert_headers = {"Authorization": "Bearer " + create_access_token(expert.id, "agronomist")}
    case = f"/api/v1/agronomist/cases/{diagnoses[0].id}"
    assert (await client.get(case, headers=expert_headers)).status_code == 404
    assert (await client.get(case + "/history", headers=expert_headers)).status_code == 404
    assert (await client.post(f"/api/v1/diagnosis/{diagnoses[0].id}/review-requests", headers=owner_headers)).status_code == 201
    assert (await client.get(case, headers=expert_headers)).status_code == 200
    assert (await client.get(case, headers=expert_headers)).json()['created_at']
    assert (await client.get(f"/api/v1/videos/{videos[0].id}", headers=expert_headers)).status_code == 200
    assert (await client.get(f"/api/v1/videos/{videos[1].id}", headers=expert_headers)).status_code == 404
    assert (await client.get(f"/api/v1/agronomist/cases/{diagnoses[1].id}/history", headers=expert_headers)).status_code == 404
    assert (await client.get(f"/api/v1/farms/{farm.id}", headers=expert_headers)).status_code == 404
    assert (await client.post(case + '/claim', headers=expert_headers)).status_code == 200
    payload = {'is_healthy_override': True, 'severity_level': 0, 'affected_plant_estimate_independent': 0, 'notes': 'No clear symptoms in the submitted evidence.'}
    review_path = f'/api/v1/diagnosis/{diagnoses[0].id}/verify'
    assert (await client.post(review_path, json=payload, headers=expert_headers)).status_code == 201
    assert (await client.post(review_path, json=payload, headers=expert_headers)).status_code == 409
    report = (await client.get(f'/api/v1/videos/{videos[0].id}/analysis', headers=owner_headers)).json()
    assert report['expert_review']['status'] == 'completed'
    assert report['expert_review']['notes'] == payload['notes']
    history = (await client.get('/api/v1/agronomist/reviews', headers=expert_headers)).json()
    assert len(history) == 1
    assert history[0]['field_name'] == 'Soybean'
    from app.dataset_export import eligible_records
    assert await eligible_records(test_db) == []
    farmer.training_consent = True
    await test_db.commit()
    exported = await eligible_records(test_db)
    assert len(exported) == 1 and exported[0]['disease'] == 'healthy'
    assert 'email' not in exported[0] and 'notes' not in exported[0]
    farmer.training_consent = False
    await test_db.commit()
    assert await eligible_records(test_db) == []
