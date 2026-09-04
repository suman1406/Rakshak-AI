import pytest
from sqlalchemy import func, select

from app.db.demo_data import get_demo_workspace, initialize_demo_data
from app.models.farm import Farm, Field
from app.models.video import Video


@pytest.mark.asyncio
async def test_demo_seed_is_idempotent_and_never_creates_videos(test_db):
    first = await initialize_demo_data(test_db)
    assert first["initialized"] is True
    assert first["farms"] == 6
    assert first["fields"] == 12
    assert first["videos"] == 0
    assert (await test_db.execute(select(func.count(Farm.id)))).scalar_one() == 6
    assert (await test_db.execute(select(func.count(Field.id)))).scalar_one() == 12
    assert (await test_db.execute(select(func.count(Video.id)))).scalar_one() == 0
    second = await initialize_demo_data(test_db)
    assert second["initialized"] is False


@pytest.mark.asyncio
async def test_demo_workspace_is_sanitized_and_has_no_video_work(test_db):
    unavailable = await get_demo_workspace(test_db)
    assert unavailable["available"] is False
    await initialize_demo_data(test_db)
    workspace = await get_demo_workspace(test_db)
    assert workspace["available"] is True
    assert workspace["organization"]["metrics"] == {"total_farms": 6, "total_fields": 12, "videos": 0, "reports": 0}
    assert len(workspace["farmer"]["fields"]) == 12
    assert workspace["farmer"]["videos"] == []
    assert workspace["agronomist"]["open_cases"] == 0
    assert all("id" not in field for field in workspace["farmer"]["fields"])
