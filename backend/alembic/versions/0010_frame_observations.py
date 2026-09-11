"""Record whole-frame baseline observations without inventing leaf detections."""
from alembic import op

revision = "0010_frame_observations"
down_revision = "0009_action_items"
branch_labels = None
depends_on = None

def upgrade():
    if op.get_bind().dialect.name == "postgresql":
        with op.get_context().autocommit_block():
            op.execute("ALTER TYPE detectionclass ADD VALUE IF NOT EXISTS 'frame_region'")

def downgrade():
    # Keep the enum member so recorded baseline evidence remains readable.
    pass
