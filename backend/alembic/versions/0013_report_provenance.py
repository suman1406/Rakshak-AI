"""Keep the actual aggregate distribution and model provenance per assessment."""
from alembic import op
import sqlalchemy as sa

revision = '0013_report_provenance'
down_revision = '0012_contact_inquiries'
branch_labels = None
depends_on = None


def upgrade():
    existing = {column['name'] for column in sa.inspect(op.get_bind()).get_columns('video_diagnoses')}
    for name in ('probability_distribution', 'model_versions'):
        if name not in existing:
            op.add_column('video_diagnoses', sa.Column(name, sa.JSON(), nullable=True))


def downgrade():
    op.drop_column('video_diagnoses', 'model_versions')
    op.drop_column('video_diagnoses', 'probability_distribution')
