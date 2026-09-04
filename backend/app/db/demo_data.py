"""Idempotent, no-video demonstration data for safe SaaS walkthroughs."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.billing import Plan
from app.models.farm import Crop, Farm, Field
from app.models.identity import Organization, OrgType, User, UserRole

DEMO_ORG = "Rakshak Demonstration Cooperative"


async def initialize_demo_data(db: AsyncSession) -> dict:
    org = (await db.execute(select(Organization).where(Organization.name == DEMO_ORG))).scalar_one_or_none()
    if org:
        return {"initialized": False, "organization": DEMO_ORG, "farms": 6, "fields": 12, "videos": 0, "message": "Demo data is already available. It contains no videos or reports."}
    crop = (await db.execute(select(Crop).where(Crop.name == "Soybean", Crop.taxonomy_version == "v1.0"))).scalar_one_or_none()
    if crop is None:
        crop = Crop(name="Soybean", taxonomy_version="v1.0")
        db.add(crop); await db.flush()
    org = Organization(name=DEMO_ORG, org_type=OrgType.fpo)
    db.add(org); await db.flush()
    owner = User(email="demo.farmer@rakshak.invalid", password_hash=get_password_hash("demo-account-not-for-login"), role=UserRole.farmer, org_id=org.id, display_name="Demonstration Farmer")
    db.add(owner); await db.flush()
    locations = [("Narmada Field Collective", "Sehore"), ("Green Ridge Farm", "Sehore"), ("Riverbend Soybean Farm", "Dewas"), ("Sankalp Field Group", "Dewas"), ("Ujjain Crop Circle", "Ujjain"), ("Malwa Demonstration Farm", "Ujjain")]
    for index, (name, district) in enumerate(locations, start=1):
        farm = Farm(owner_user_id=owner.id, org_id=org.id, name=name, state="Madhya Pradesh", district=district)
        db.add(farm); await db.flush()
        db.add_all([Field(farm_id=farm.id, name=f"North Plot {index}", crop_id=crop.id, area_hectares=1.8 + index / 10), Field(farm_id=farm.id, name=f"South Plot {index}", crop_id=crop.id, area_hectares=1.2 + index / 10)])
    if not (await db.execute(select(Plan).where(Plan.code == "pilot-fpo"))).scalar_one_or_none():
        db.add(Plan(code="pilot-fpo", name="FPO Pilot", monthly_price_paise=499900, annual_price_paise=4799000, farm_limit=25, scan_limit=250, is_public=True))
    await db.commit()
    return {"initialized": True, "organization": DEMO_ORG, "farms": 6, "fields": 12, "videos": 0, "message": "Demo farms and fields are ready. Videos, diagnoses, and reports remain live-only."}


async def get_demo_workspace(db: AsyncSession) -> dict:
    """Return a role-neutral, deliberately non-identifying demo projection.

    This endpoint never returns database identifiers, customer records, videos, or
    analysis results. It lets clients demonstrate the product shell without
    weakening tenant scoping on the normal farm, field, video, or report routes.
    """
    org = (await db.execute(select(Organization).where(Organization.name == DEMO_ORG))).scalar_one_or_none()
    if org is None:
        return {"available": False, "message": "Demo data has not been initialized by an administrator.", "organization": None, "farmer": None, "agronomist": None, "admin": None}

    owner = (await db.execute(select(User).where(User.org_id == org.id, User.email == "demo.farmer@rakshak.invalid"))).scalar_one_or_none()
    farms = (await db.execute(select(Farm).where(Farm.org_id == org.id).order_by(Farm.name))).scalars().all()
    fields = (await db.execute(
        select(Field, Farm).join(Farm, Field.farm_id == Farm.id).where(Farm.org_id == org.id).order_by(Farm.name, Field.name)
    )).all()
    fields_by_farm: dict[str, list[dict]] = {}
    farmer_fields: list[dict] = []
    for index, (field, farm) in enumerate(fields, start=1):
        display = {
            "reference": f"DEMO-FLD-{index:02d}",
            "name": field.name,
            "farm_name": farm.name,
            "district": farm.district or "Not recorded",
            "crop": "Soybean",
            "area_hectares": float(field.area_hectares or 0),
            "scan_count": 0,
        }
        fields_by_farm.setdefault(farm.id, []).append(display)
        farmer_fields.append(display)
    farm_rows = []
    for index, farm in enumerate(farms, start=1):
        farm_rows.append({
            "reference": f"DEMO-FARM-{index:02d}",
            "name": farm.name,
            "district": farm.district or "Not recorded",
            "owner_name": "Demonstration farmer",
            "fields": fields_by_farm.get(farm.id, []),
        })
    return {
        "available": True,
        "message": "Development demo data is active. It has farms and fields only; no videos, diagnoses, or reports are simulated.",
        "organization": {"name": DEMO_ORG, "farms": farm_rows, "metrics": {"total_farms": len(farm_rows), "total_fields": len(farmer_fields), "videos": 0, "reports": 0}},
        "farmer": {"display_name": owner.display_name if owner else "Demonstration farmer", "fields": farmer_fields, "videos": []},
        "agronomist": {"open_cases": 0, "message": "No demo review cases are shown because demo mode never fabricates AI diagnoses or human-review work."},
        "admin": {"pilot_plan": {"code": "pilot-fpo", "name": "FPO Pilot", "monthly_price_paise": 499900, "annual_price_paise": 4799000, "farm_limit": 25, "scan_limit": 250}, "message": "Demo mode includes the pilot plan. Access applications and audit history remain live-only."},
    }
