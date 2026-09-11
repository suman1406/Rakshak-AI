"""Preserve the selected commercial interval through access approval."""
from alembic import op
import sqlalchemy as sa

revision = '0014_requested_billing'
down_revision = '0013_report_provenance'
branch_labels = None
depends_on = None

def upgrade():
    columns = {c['name'] for c in sa.inspect(op.get_bind()).get_columns('onboarding_applications')}
    if 'requested_billing_interval' not in columns:
        op.add_column('onboarding_applications', sa.Column('requested_billing_interval', sa.String(16), server_default='monthly', nullable=False))

def downgrade():
    op.drop_column('onboarding_applications', 'requested_billing_interval')
