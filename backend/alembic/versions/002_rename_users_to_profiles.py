"""rename users to profiles

Revision ID: 002
Revises: 001
Create Date: 2025-11-09

"""
from alembic import op
import sqlalchemy as sa


revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename users table to profiles
    op.rename_table('users', 'profiles')
    
    # Rename indexes
    op.execute('ALTER INDEX IF EXISTS idx_users_tenant_id RENAME TO idx_profiles_tenant_id')
    op.execute('ALTER INDEX IF EXISTS idx_users_email RENAME TO idx_profiles_email')


def downgrade() -> None:
    # Rename back to users
    op.rename_table('profiles', 'users')
    
    # Rename indexes back
    op.execute('ALTER INDEX IF EXISTS idx_profiles_tenant_id RENAME TO idx_users_tenant_id')
    op.execute('ALTER INDEX IF EXISTS idx_profiles_email RENAME TO idx_users_email')

