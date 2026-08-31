"""Persist agronomist verification notes.

Revision ID: 0002_verified_label_notes
Revises: 0001_initial_schema
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_verified_label_notes"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("verified_labels")}
    if "notes" not in columns:
        op.add_column("verified_labels", sa.Column("notes", sa.Text(), nullable=True))


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("verified_labels")}
    if "notes" in columns:
        op.drop_column("verified_labels", "notes")
