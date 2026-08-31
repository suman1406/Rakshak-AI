"""Add persisted agronomist review workflow."""
from alembic import op
import sqlalchemy as sa

revision = "0003_review_work_items"
down_revision = "0002_verified_label_notes"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("review_work_items", sa.Column("id", sa.String(36), primary_key=True), sa.Column("video_diagnosis_id", sa.String(36), sa.ForeignKey("video_diagnoses.id"), nullable=False, unique=True), sa.Column("status", sa.Enum("pending", "in_review", "completed", name="reviewstatus"), nullable=False), sa.Column("assigned_agronomist_id", sa.String(36), sa.ForeignKey("users.id")), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("completed_at", sa.DateTime(timezone=True)))

def downgrade(): op.drop_table("review_work_items")
