"""Persist website contact requests for the platform administrator."""
from alembic import op
import sqlalchemy as sa

revision = '0012_contact_inquiries'
down_revision = '0011_privacy_controls'
branch_labels = None
depends_on = None


def upgrade():
    if 'contact_inquiries' not in sa.inspect(op.get_bind()).get_table_names():
        op.create_table('contact_inquiries', sa.Column('id', sa.String(36), primary_key=True), sa.Column('name', sa.String(255), nullable=False), sa.Column('email', sa.String(320), nullable=False), sa.Column('message', sa.Text(), nullable=False), sa.Column('status', sa.String(16), nullable=False), sa.Column('request_key', sa.String(64), nullable=False), sa.Column('created_at', sa.DateTime(timezone=True), nullable=False))
        op.create_index('ix_contact_inquiries_request_key', 'contact_inquiries', ['request_key'])


def downgrade():
    op.drop_table('contact_inquiries')
