import pytest

@pytest.mark.asyncio
async def test_farms_and_fields_api_flow(client):
    # 1. Create a Farm
    farm_payload = {
        "name": "Indore Soybean Farm",
        "state": "Madhya Pradesh",
        "district": "Indore",
    }
    farm_res = await client.post("/api/v1/farms", json=farm_payload)
    assert farm_res.status_code == 201
    farm_data = farm_res.json()
    assert farm_data["name"] == "Indore Soybean Farm"
    farm_id = farm_data["id"]

    # 2. Create a Field under the Farm
    field_payload = {
        "name": "North Plot A",
        "area_hectares": 3.2,
    }
    field_res = await client.post(f"/api/v1/farms/{farm_id}/fields", json=field_payload)
    assert field_res.status_code == 201
    field_data = field_res.json()
    assert field_data["name"] == "North Plot A"
    field_id = field_data["id"]

    # 3. List Fields
    list_res = await client.get("/api/v1/fields")
    assert list_res.status_code == 200
    fields = list_res.json()
    assert len(fields) >= 1
    assert any(f["id"] == field_id for f in fields)

    # 4. Get Field Health
    health_res = await client.get(f"/api/v1/fields/{field_id}/health")
    assert health_res.status_code == 200
    health_data = health_res.json()
    assert health_data["field_id"] == field_id
    assert "fasal_health_score" in health_data
    assert "components" in health_data
    assert "zones" in health_data
