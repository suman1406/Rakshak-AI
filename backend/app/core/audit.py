from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.governance import AuditLog


async def write_audit_log(
    db: AsyncSession,
    *,
    actor_user_id: str | None,
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Persist a small, non-sensitive audit event in the same transaction."""
    db.add(
        AuditLog(
            actor_user_id=actor_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata_json=metadata,
        )
    )
