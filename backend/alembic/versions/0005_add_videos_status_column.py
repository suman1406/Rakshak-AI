"""Add status column to videos table.

The videos table was created without the status column in some early deployments.
This migration ensures the status column exists with a default value.
"""
from alembic import op
import sqlalchemy as sa


revision = "0005_add_videos_status_column"
down_revision = "0004_add_users_role_column"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    
    # Check if column exists
    result = bind.execute(
        sa.text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'videos' AND column_name = 'status'
        """)
    ).fetchone()
    
    if result is None:
        # Create the enum type if it doesn't exist
        bind.execute(
            sa.text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'videostatus') THEN
                        CREATE TYPE videostatus AS ENUM ('uploaded', 'validating', 'processing', 'analyzing', 'aggregating', 'ready', 'failed', 'insufficient_evidence');
                    END IF;
                END
                $$;
            """)
        )
        # Add status column with default value
        op.add_column(
            "videos",
            sa.Column("status", sa.Enum("uploaded", "validating", "processing", "analyzing", "aggregating", "ready", "failed", "insufficient_evidence", name="videostatus"), nullable=False, server_default="uploaded")
        )


def downgrade() -> None:
    op.drop_column("videos", "status")