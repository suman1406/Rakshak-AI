"""Add the confidence band expected by the diagnosis model.

Older production databases were created before this column existed.  The
initial schema migration uses ``checkfirst``, so it does not evolve an already
existing ``video_diagnoses`` table when the ORM model gains a field.

Revision ID: 0006_confidence_band
Revises: 0005_add_videos_status_column
"""

from alembic import op
import sqlalchemy as sa


revision = "0006_confidence_band"
down_revision = "0005_add_videos_status_column"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("video_diagnoses")}
    if "confidence_band" in columns:
        return

    # SQLAlchemy's ConfidenceBand enum is stored as the PostgreSQL type
    # ``confidenceband``.  Create it independently so this is safe for older
    # databases that predate both the enum and its column.
    bind.execute(
        sa.text(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'confidenceband') THEN
                    CREATE TYPE confidenceband AS ENUM ('high', 'medium', 'low');
                END IF;
            END
            $$;
            """
        )
    )
    op.add_column(
        "video_diagnoses",
        sa.Column("confidence_band", sa.Enum("high", "medium", "low", name="confidenceband", create_type=False), nullable=True),
    )
    # Preserve existing diagnosis rows while giving them the same bands used
    # by the application for future diagnoses.
    bind.execute(
        sa.text(
            """
            UPDATE video_diagnoses
            SET confidence_band = CASE
                WHEN confidence >= 0.80 THEN 'high'::confidenceband
                WHEN confidence >= 0.65 THEN 'medium'::confidenceband
                ELSE 'low'::confidenceband
            END
            WHERE confidence_band IS NULL
            """
        )
    )
    op.alter_column("video_diagnoses", "confidence_band", nullable=False)


def downgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("video_diagnoses")}
    if "confidence_band" in columns:
        op.drop_column("video_diagnoses", "confidence_band")
