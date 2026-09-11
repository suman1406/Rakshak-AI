"""Idempotent, no-video demonstration data for safe SaaS walkthroughs."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.billing import Plan
from app.models.farm import Crop, Farm, Field
from app.models.identity import AccountStatus, Organization, OrgType, User, UserRole

DEMO_ORG = "Rakshak Demonstration Cooperative"
DEMO_FARMER_EMAIL = "farmer@rakshak.local"
LEGACY_FARMER_EMAIL = "demo.farmer@rakshak.invalid"


async def initialize_demo_data(db: AsyncSession) -> dict:
    """Repairable and idempotent demo data initializer."""
    crop = (await db.execute(select(Crop).where(Crop.name == "Soybean", Crop.taxonomy_version == "v1.0"))).scalar_one_or_none()
    if crop is None:
        crop = Crop(name="Soybean", taxonomy_version="v1.0")
        db.add(crop)
        await db.flush()

    org = (await db.execute(select(Organization).where(Organization.name == DEMO_ORG))).scalar_one_or_none()
    if org is None:
        org = Organization(name=DEMO_ORG, org_type=OrgType.fpo)
        db.add(org)
        await db.flush()
    elif org.org_type != OrgType.fpo:
        org.org_type = OrgType.fpo

    demo_password = settings.DEMO_GATE_PASSWORD or "RakshakDemo@123"
    owner = (await db.execute(select(User).where(User.email == DEMO_FARMER_EMAIL))).scalar_one_or_none()
    legacy_owner = (await db.execute(select(User).where(User.email == LEGACY_FARMER_EMAIL))).scalar_one_or_none()

    if owner is None and legacy_owner is not None:
        legacy_owner.email = DEMO_FARMER_EMAIL
        legacy_owner.display_name = "Rakshak Demo Farmer"
        legacy_owner.role = UserRole.farmer
        legacy_owner.org_id = org.id
        legacy_owner.account_status = AccountStatus.active.value
        legacy_owner.password_hash = get_password_hash(demo_password)
        owner = legacy_owner
    elif owner is None:
        owner = User(
            email=DEMO_FARMER_EMAIL,
            password_hash=get_password_hash(demo_password),
            role=UserRole.farmer,
            org_id=org.id,
            display_name="Rakshak Demo Farmer",
            account_status=AccountStatus.active.value,
        )
        db.add(owner)
        await db.flush()
    else:
        owner.display_name = "Rakshak Demo Farmer"
        owner.role = UserRole.farmer
        owner.org_id = org.id
        owner.account_status = AccountStatus.active.value
        if settings.DEMO_GATE_PASSWORD or settings.BOOTSTRAP_DEMO_ACCOUNTS:
            owner.password_hash = get_password_hash(demo_password)

    if legacy_owner is not None and legacy_owner.id != owner.id:
        legacy_farms = (await db.execute(select(Farm).where(Farm.owner_user_id == legacy_owner.id))).scalars().all()
        for farm in legacy_farms:
            farm.owner_user_id = owner.id
            farm.org_id = org.id

    locations = [
        ("Narmada Field Collective", "Sehore"),
        ("Green Ridge Farm", "Sehore"),
        ("Riverbend Soybean Farm", "Dewas"),
        ("Sankalp Field Group", "Dewas"),
        ("Ujjain Crop Circle", "Ujjain"),
        ("Malwa Demonstration Farm", "Ujjain"),
    ]

    total_farms = 0
    total_fields = 0

    for index, (name, district) in enumerate(locations, start=1):
        farm = (await db.execute(select(Farm).where(Farm.org_id == org.id, Farm.name == name))).scalar_one_or_none()
        if farm is None:
            farm = Farm(owner_user_id=owner.id, org_id=org.id, name=name, state="Madhya Pradesh", district=district)
            db.add(farm)
            await db.flush()
        else:
            farm.owner_user_id = owner.id
            farm.state = "Madhya Pradesh"
            farm.district = district

        total_farms += 1

        for plot_prefix, area_offset in [("North Plot", 1.8), ("South Plot", 1.2)]:
            field_name = f"{plot_prefix} {index}"
            field = (await db.execute(select(Field).where(Field.farm_id == farm.id, Field.name == field_name))).scalar_one_or_none()
            if field is None:
                field = Field(farm_id=farm.id, name=field_name, crop_id=crop.id, area_hectares=area_offset + index / 10)
                db.add(field)
            else:
                field.crop_id = crop.id
                if not field.area_hectares:
                    field.area_hectares = area_offset + index / 10
            total_fields += 1

    plan = (await db.execute(select(Plan).where(Plan.code == "pilot-fpo"))).scalar_one_or_none()
    if plan is None:
        db.add(Plan(code="pilot-fpo", name="FPO Pilot", monthly_price_paise=499900, annual_price_paise=4799000, farm_limit=25, scan_limit=250, is_public=True))

    await db.commit()
    return {
        "initialized": True,
        "organization": DEMO_ORG,
        "farmer_email": DEMO_FARMER_EMAIL,
        "farms": total_farms,
        "fields": total_fields,
        "videos": 0,
        "message": "Demo farms and fields are ready. Videos, diagnoses, and reports remain live-only.",
    }


async def get_demo_workspace(db: AsyncSession) -> dict:
    """Return a role-neutral demo projection with connected demo farmer details.

    This endpoint never returns customer records, uploaded videos, or actual AI analysis results.
    """
    org = (await db.execute(select(Organization).where(Organization.name == DEMO_ORG))).scalar_one_or_none()
    if org is None:
        return {"available": False, "message": "Demo data has not been initialized by an administrator.", "organization": None, "farmer": None, "agronomist": None, "admin": None}

    owner = (await db.execute(select(User).where(User.org_id == org.id, User.email == DEMO_FARMER_EMAIL))).scalar_one_or_none()
    if owner is None:
        owner = (await db.execute(select(User).where(User.org_id == org.id, User.role == UserRole.farmer))).scalar_one_or_none()

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
    owner_display = owner.display_name if owner else "Rakshak Demo Farmer"
    for index, farm in enumerate(farms, start=1):
        farm_rows.append({
            "reference": f"DEMO-FARM-{index:02d}",
            "name": farm.name,
            "district": farm.district or "Not recorded",
            "owner_name": owner_display,
            "fields": fields_by_farm.get(farm.id, []),
        })
    return {
        "available": True,
        "message": "Development demo data is active. It has farms and fields only; no videos, diagnoses, or reports are simulated.",
        "organization": {"name": DEMO_ORG, "farms": farm_rows, "metrics": {"total_farms": len(farm_rows), "total_fields": len(farmer_fields), "videos": 0, "reports": 0}},
        "farmer": {
            "display_name": owner_display,
            "email": owner.email if owner else DEMO_FARMER_EMAIL,
            "fields": farmer_fields,
            "videos": [],
        },
        "agronomist": {"open_cases": 0, "message": "No demo review cases are shown because demo mode never fabricates AI diagnoses or human-review work."},
        "admin": {"pilot_plan": {"code": "pilot-fpo", "name": "FPO Pilot", "monthly_price_paise": 499900, "annual_price_paise": 4799000, "farm_limit": 25, "scan_limit": 250}, "message": "Demo mode includes the pilot plan. Access applications and audit history remain live-only."},
    }

