"""Create the Phase 1 relational schema from the SQLAlchemy contract."""
from alembic import op
from app.db.base import Base
from app.models import farm, identity, video, prediction, verification, governance  # noqa: F401

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    bind = op.get_bind()
    for table in Base.metadata.sorted_tables:
        table.create(bind=bind, checkfirst=True)

def downgrade() -> None:
    bind = op.get_bind()
    for table in reversed(Base.metadata.sorted_tables):
        table.drop(bind=bind, checkfirst=True)
