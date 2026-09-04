"""add onboarding lifecycle

Revision ID: 0008_onboarding_lifecycle
Revises: 0007_pilot_billing
"""

from alembic import op
import sqlalchemy as sa


revision = "0008_onboarding_lifecycle"
down_revision = "0007_pilot_billing"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("account_status", sa.String(length=16), nullable=False, server_default="active"))
    op.add_column("users", sa.Column("consent_accepted_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_users_account_status", "users", ["account_status"])
    op.create_table(
        "onboarding_applications",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("applicant_user_id", sa.String(length=36), nullable=False),
        sa.Column("application_type", sa.String(length=24), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="pending"),
        sa.Column("organization_name", sa.String(length=255), nullable=True),
        sa.Column("requested_org_type", sa.String(length=32), nullable=True),
        sa.Column("requested_plan_code", sa.String(length=50), nullable=True),
        sa.Column("reviewer_user_id", sa.String(length=36), nullable=True),
        sa.Column("review_note", sa.Text(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["applicant_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["reviewer_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("applicant_user_id"),
    )
    op.create_index("ix_onboarding_applications_application_type", "onboarding_applications", ["application_type"])
    op.create_index("ix_onboarding_applications_status", "onboarding_applications", ["status"])


def downgrade() -> None:
    op.drop_index("ix_onboarding_applications_status", table_name="onboarding_applications")
    op.drop_index("ix_onboarding_applications_application_type", table_name="onboarding_applications")
    op.drop_table("onboarding_applications")
    op.drop_index("ix_users_account_status", table_name="users")
    op.drop_column("users", "consent_accepted_at")
    op.drop_column("users", "account_status")
