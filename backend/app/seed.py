"""Create a repeatable local dataset for the Rakshak AI pilot environment."""

import asyncio

from sqlalchemy import select

from .core.security import get_password_hash
from .db.base import Base
from .db.session import async_session_factory, engine
from .models.farm import Crop, Disease, Farm, Field
from .models.identity import User, UserRole
from .models import farm, identity, prediction, video  # noqa: F401

SEED_USERS = [
    ("agronomist.one@rakshak.ai", "Agronomist One", UserRole.agronomist, "org-fasal-west"),
    ("agronomist.two@rakshak.ai", "Agronomist Two", UserRole.agronomist, "org-fasal-west"),
    ("admin.one@rakshak.ai", "Organization Admin One", UserRole.org_admin, "org-fasal-west"),
    ("admin.two@rakshak.ai", "Organization Admin Two", UserRole.org_admin, "org-fasal-west"),
    ("farmer.one@rakshak.ai", "Farmer One", UserRole.farmer, "org-fasal-west"),
    ("farmer.two@rakshak.ai", "Farmer Two", UserRole.farmer, "org-fasal-west"),
]

PASSWORD = "Rakshak@2026"


async def seed() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        users: dict[str, User] = {}
        for email, display_name, role, org_id in SEED_USERS:
            user = (await session.execute(select(User).where(User.email == email))).scalar_one_or_none()
            if user is None:
                user = User(email=email, display_name=display_name, role=role, org_id=org_id, password_hash=get_password_hash(PASSWORD))
                session.add(user)
                await session.flush()
            else:
                user.display_name = display_name
                user.role = role
                user.org_id = org_id
                user.password_hash = get_password_hash(PASSWORD)
            users[email] = user

        crop = (await session.execute(select(Crop).where(Crop.id == "crop-soybean"))).scalar_one_or_none()
        if crop is None:
            crop = Crop(id="crop-soybean", name="Soybean", taxonomy_version="v1")
            session.add(crop)
        for disease_id, name in (("disease-soybean-rust", "Soybean rust"), ("disease-cercospora", "Cercospora leaf blight")):
            disease = (await session.execute(select(Disease).where(Disease.id == disease_id))).scalar_one_or_none()
            if disease is None:
                session.add(Disease(id=disease_id, crop_id=crop.id, name=name, taxonomy_version="v1"))

        farms = [
            ("farm-patil", "Patil Farm", "Maharashtra", "Latur", "farmer.one@rakshak.ai"),
            ("farm-shinde", "Shinde Farm", "Maharashtra", "Amravati", "farmer.two@rakshak.ai"),
        ]
        for farm_id, name, state, district, owner_email in farms:
            farm_record = (await session.execute(select(Farm).where(Farm.id == farm_id))).scalar_one_or_none()
            if farm_record is None:
                session.add(Farm(id=farm_id, owner_user_id=users[owner_email].id, org_id="org-fasal-west", name=name, state=state, district=district))

        fields = [
            ("field-north-plot", "farm-patil", "North plot", 12.5),
            ("field-east-field", "farm-patil", "East field", 9.0),
            ("field-river-block", "farm-shinde", "River block", 18.0),
        ]
        for field_id, farm_id, name, area_hectares in fields:
            field_record = (await session.execute(select(Field).where(Field.id == field_id))).scalar_one_or_none()
            if field_record is None:
                session.add(Field(id=field_id, farm_id=farm_id, name=name, crop_id=crop.id, area_hectares=area_hectares))

        await session.commit()
    print("Rakshak seed completed: users, soybean taxonomy, farms, and fields are ready.")


if __name__ == "__main__":
    asyncio.run(seed())
