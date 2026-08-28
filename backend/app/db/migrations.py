"""Small idempotent schema upgrades used by the pilot container.

The project does not yet ship Alembic migrations.  Keeping these upgrades
idempotent makes an existing pilot database safe to start while the proper
migration history is being introduced.
"""

from sqlalchemy import text


async def apply_pilot_schema_upgrades(engine) -> None:
    async with engine.begin() as connection:
        await connection.execute(text("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'admin'"))
        await connection.execute(text("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'enterprise'"))
        for value in ("diseased_leaf", "lesion", "stem", "pod"):
            await connection.execute(text(f"ALTER TYPE detectionclass ADD VALUE IF NOT EXISTS '{value}'"))
        upgrades = {
            "crops": [
                ("active", "BOOLEAN NOT NULL DEFAULT TRUE"),
                ("created_at", "TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()"),
            ],
            "diseases": [
                ("active", "BOOLEAN NOT NULL DEFAULT TRUE"),
                ("created_at", "TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()"),
            ],
            "users": [("updated_at", "TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()")],
            "videos": [
                ("gps_geohash", "VARCHAR(12)"),
                ("duration_seconds", "DOUBLE PRECISION"),
                ("device_metadata", "JSONB"),
                ("updated_at", "TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()"),
            ],
            "frames": [("created_at", "TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()")],
            "detections": [("created_at", "TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()")],
            "frame_diagnoses": [("created_at", "TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()")],
            "video_diagnoses": [("created_at", "TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()")],
        }
        for table, columns in upgrades.items():
            for column, definition in columns:
                await connection.execute(text(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {column} {definition}"))
