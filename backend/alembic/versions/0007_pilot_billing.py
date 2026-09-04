"""Add pilot plan and organization subscription records.

Revision ID: 0007_pilot_billing
Revises: 0006_add_video_diag_cols
"""

from alembic import op
import sqlalchemy as sa

revision = "0007_pilot_billing"
down_revision = "0006_add_video_diag_cols"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if not sa.inspect(bind).has_table("plans"):
        op.create_table("plans", sa.Column("id", sa.String(36), primary_key=True), sa.Column("code", sa.String(50), nullable=False, unique=True), sa.Column("name", sa.String(100), nullable=False), sa.Column("monthly_price_paise", sa.Integer()), sa.Column("annual_price_paise", sa.Integer()), sa.Column("farm_limit", sa.Integer()), sa.Column("scan_limit", sa.Integer()), sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")))
    if not sa.inspect(bind).has_table("organization_subscriptions"):
        op.create_table("organization_subscriptions", sa.Column("id", sa.String(36), primary_key=True), sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=False, unique=True), sa.Column("plan_id", sa.String(36), sa.ForeignKey("plans.id"), nullable=False), sa.Column("status", sa.String(16), nullable=False, server_default="trial"), sa.Column("billing_interval", sa.String(16), nullable=False, server_default="monthly"), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")))


def downgrade() -> None:
    op.drop_table("organization_subscriptions")
    op.drop_table("plans")
