"""Add role column to users table.

The users table was created without the role column in some early deployments.
This migration ensures the role column exists with a default value.
"""
from alembic import op
import sqlalchemy as sa


revision = "0004_add_users_role_column"
down_revision = "0003_review_work_items"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if role column exists, if not add it
    # Get the connection to execute raw SQL for the check
    bind = op.get_bind()
    
    # Check if column exists using PostgreSQL information_schema
    result = bind.execute(
        sa.text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'role'
        """)
    ).fetchone()
    
    if result is None:
        # Add role column with default value 'farmer'
        op.add_column(
            "users",
            sa.Column("role", sa.String(50), nullable=False, server_default="farmer")
        )


def downgrade() -> None:
    op.drop_column("users", "role")