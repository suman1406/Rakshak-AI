"""add action_items to video_diagnoses

Revision ID: 0009_add_action_items_to_video_diagnoses
Revises: 0008_onboarding_lifecycle
"""

from alembic import op
import sqlalchemy as sa


revision = "0009_action_items"
down_revision = "0008_onboarding_lifecycle"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add action_items column — nullable so existing rows are unaffected.
    # Text (unbounded) rather than String(2000): multiple action items joined
    # with newlines can legitimately exceed 2000 chars.
    if "action_items" in {column["name"] for column in sa.inspect(op.get_bind()).get_columns("video_diagnoses")}:
        return
    op.add_column(
        "video_diagnoses",
        sa.Column("action_items", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("video_diagnoses", "action_items")
