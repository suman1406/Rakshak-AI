import pytest
from sqlalchemy import select

from app.db.bootstrap_accounts import (
    BOOTSTRAP_ACCOUNTS,
    BOOTSTRAP_ORGANIZATION_NAME,
    ensure_bootstrap_access_accounts,
    ensure_initial_admin_account,
)
from app.models.identity import Organization, User, UserRole


@pytest.mark.asyncio
async def test_bootstrap_creates_only_access_accounts_and_is_idempotent(test_db):
    created = await ensure_bootstrap_access_accounts(test_db, "A-strong-test-password")

    assert created == [email for email, _, _ in BOOTSTRAP_ACCOUNTS]
    organization = (
        await test_db.execute(
            select(Organization).where(Organization.name == BOOTSTRAP_ORGANIZATION_NAME)
        )
    ).scalar_one()
    accounts = (await test_db.execute(select(User).order_by(User.email))).scalars().all()
    assert [(account.email, account.role, account.org_id) for account in accounts] == [
        (email, role, organization.id) for email, _, role in BOOTSTRAP_ACCOUNTS
    ]

    assert await ensure_bootstrap_access_accounts(test_db, "A-different-password") == []
    accounts_after_retry = (await test_db.execute(select(User))).scalars().all()
    assert len(accounts_after_retry) == len(BOOTSTRAP_ACCOUNTS)


@pytest.mark.asyncio
async def test_initial_admin_is_explicit_and_never_resets(test_db):
    assert await ensure_initial_admin_account(test_db, "admin@rakshak.local", "A secure passphrase 2026") is True
    account = (await test_db.execute(select(User).where(User.email == "admin@rakshak.local"))).scalar_one()
    assert account.role == UserRole.admin
    assert await ensure_initial_admin_account(test_db, "admin@rakshak.local", "Different secure phrase") is False
