"""Idempotent, explicitly enabled access-account bootstrap.

This intentionally creates credentials and a workspace only. It never creates
farms, fields, uploads, diagnoses, reports, or other synthetic operational data.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.identity import OrgType, Organization, User, UserRole


BOOTSTRAP_ORGANIZATION_NAME = "Rakshak Access Workspace"
BOOTSTRAP_ACCOUNTS = (
    ("agronomist@rakshak.local", "Rakshak Agronomist", UserRole.agronomist),
    ("workspace@rakshak.local", "Rakshak Workspace", UserRole.enterprise),
)


async def ensure_bootstrap_access_accounts(db: AsyncSession, password: str) -> list[str]:
    """Create the authorized test-access accounts if they are missing.

    Existing accounts are never overwritten, including their password or role.
    """
    organization = (
        await db.execute(
            select(Organization).where(Organization.name == BOOTSTRAP_ORGANIZATION_NAME)
        )
    ).scalar_one_or_none()
    if organization is None:
        organization = Organization(name=BOOTSTRAP_ORGANIZATION_NAME, org_type=OrgType.other)
        db.add(organization)
        await db.flush()

    created: list[str] = []
    for email, display_name, role in BOOTSTRAP_ACCOUNTS:
        account = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
        if account is None:
            db.add(
                User(
                    email=email,
                    password_hash=get_password_hash(password),
                    role=role,
                    org_id=organization.id,
                    display_name=display_name,
                )
            )
            created.append(email)

    await db.commit()
    return created
