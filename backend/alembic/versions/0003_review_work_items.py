"""Mark 0003 migration as complete in alembic_version.

The review_work_items table and reviewstatus type were created in a previous 
partial deployment. This migration marks 0003 as complete without re-running it.
"""
from alembic import op
import sqlalchemy as sa


revision = "0003_review_work_items"
down_revision = "0002_verified_label_notes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """This is a no-op migration that marks 0003 as complete.
    
    The actual table and enum type were created in previous partial deployments.
    We simply record this migration as applied to allow subsequent migrations to run.
    """
    pass


def downgrade() -> None:
    pass