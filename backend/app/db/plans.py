"""Versioned launch offers; preserve any administrator edits on restart."""
import uuid
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from app.models.billing import Plan

LAUNCH_PLANS = (
    dict(code='fpo-starter', name='FPO Starter', monthly_price_paise=299900,
         annual_price_paise=2999000, farm_limit=25, scan_limit=250),
    dict(code='organization-growth', name='Organization Growth', monthly_price_paise=999900,
         annual_price_paise=9999000, farm_limit=100, scan_limit=1000),
    dict(code='enterprise', name='Enterprise', monthly_price_paise=None,
         annual_price_paise=None, farm_limit=None, scan_limit=None),
)

async def ensure_launch_plans(db):
    insert = pg_insert if db.get_bind().dialect.name == 'postgresql' else sqlite_insert
    for offer in LAUNCH_PLANS:
        await db.execute(insert(Plan).values(id=str(uuid.uuid4()), **offer,
            is_public=True, is_active=True, created_at=datetime.now(timezone.utc))
            .on_conflict_do_nothing(index_elements=['code']))
    await db.commit()
