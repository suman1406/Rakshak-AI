"""Session invalidation, separate training consent and evidence retention."""
from alembic import op
import sqlalchemy as sa

revision = '0011_privacy_controls'
down_revision = '0010_frame_observations'
branch_labels = None
depends_on = None

def upgrade():
    inspector = sa.inspect(op.get_bind())
    for table, column in [
        ('users', sa.Column('token_version', sa.Integer(), nullable=False, server_default='0')),
        ('users', sa.Column('training_consent', sa.Boolean(), nullable=False, server_default=sa.false())),
        ('videos', sa.Column('media_deleted_at', sa.DateTime(timezone=True), nullable=True)),
    ]:
        if column.name not in {item['name'] for item in inspector.get_columns(table)}:
            op.add_column(table, column)

def downgrade():
    op.drop_column('videos', 'media_deleted_at')
    op.drop_column('users', 'training_consent')
    op.drop_column('users', 'token_version')
