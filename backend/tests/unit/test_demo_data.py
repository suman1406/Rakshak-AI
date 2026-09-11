import pytest
from sqlalchemy import func, select

from app.core.security import get_password_hash
from app.db.demo_data import DEMO_FARMER_EMAIL, DEMO_ORG, get_demo_workspace, initialize_demo_data
from app.models.farm import Farm, Field
from app.models.identity import Organization, OrgType, User, UserRole
from app.models.video import Video


@pytest.mark.asyncio
async def test_demo_seed_is_idempotent_and_never_creates_videos(test_db):
    first = await initialize_demo_data(test_db)
    assert first["initialized"] is True
    assert first["farmer_email"] == DEMO_FARMER_EMAIL
    assert first["farms"] == 6
    assert first["fields"] == 12
    assert first["videos"] == 0
    assert (await test_db.execute(select(func.count(Farm.id)))).scalar_one() == 6
    assert (await test_db.execute(select(func.count(Field.id)))).scalar_one() == 12
    assert (await test_db.execute(select(func.count(Video.id)))).scalar_one() == 0

    second = await initialize_demo_data(test_db)
    assert second["initialized"] is True
    assert (await test_db.execute(select(func.count(Farm.id)))).scalar_one() == 6
    assert (await test_db.execute(select(func.count(Field.id)))).scalar_one() == 12


@pytest.mark.asyncio
async def test_demo_seed_repairs_legacy_non_login_user(test_db):
    org = Organization(name=DEMO_ORG, org_type=OrgType.fpo)
    test_db.add(org)
    await test_db.flush()

    legacy_user = User(
        email="demo.farmer@rakshak.invalid",
        password_hash=get_password_hash("legacy-pass"),
        role=UserRole.farmer,
        org_id=org.id,
        display_name="Demonstration Farmer",
    )
    test_db.add(legacy_user)
    await test_db.flush()

    res = await initialize_demo_data(test_db)
    assert res["initialized"] is True

    updated_user = (await test_db.execute(select(User).where(User.email == DEMO_FARMER_EMAIL))).scalar_one_or_none()
    assert updated_user is not None
    assert updated_user.display_name == "Rakshak Demo Farmer"
    assert updated_user.role == UserRole.farmer


@pytest.mark.asyncio
async def test_demo_workspace_is_sanitized_and_has_no_video_work(test_db):
    unavailable = await get_demo_workspace(test_db)
    assert unavailable["available"] is False
    await initialize_demo_data(test_db)
    workspace = await get_demo_workspace(test_db)
    assert workspace["available"] is True
    assert workspace["organization"]["metrics"] == {"total_farms": 6, "total_fields": 12, "videos": 0, "reports": 0}
    assert len(workspace["farmer"]["fields"]) == 12
    assert workspace["farmer"]["display_name"] == "Rakshak Demo Farmer"
    assert workspace["farmer"]["email"] == "farmer@rakshak.local"
    assert workspace["farmer"]["videos"] == []
    assert workspace["agronomist"]["open_cases"] == 0
    assert all(farm["owner_name"] == "Rakshak Demo Farmer" for farm in workspace["organization"]["farms"])
    assert all("id" not in field for field in workspace["farmer"]["fields"])

