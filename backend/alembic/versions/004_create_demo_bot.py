"""Create demo bot tenant and admin user

Revision ID: 004
Revises: 003
Create Date: 2025-11-12 03:30:00

"""
from alembic import op
import sqlalchemy as sa
import os


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create demo tenant
    op.execute("""
        INSERT INTO tenants (id, name, created_at, updated_at)
        VALUES (
            '00000000-0000-0000-0000-000000000000',
            'Weaver Demo Bot',
            NOW(),
            NOW()
        )
        ON CONFLICT (id) DO NOTHING
    """)
    
    # Create demo bot with custom system prompt
    # config_json stores per-bot customizations (system_prompt)
    # Global settings (temperature, top_k) remain in environment variables
    # Note: tenant trigger creates a bot automatically, so we update it instead
    op.execute("""
        INSERT INTO bots (id, tenant_id, name, config_json, created_at, updated_at)
        VALUES (
            '00000000-0000-0000-0000-000000000001',
            '00000000-0000-0000-0000-000000000000',
            'Demo Bot',
            '{"system_prompt": "You are the Weaver Demo Bot, an AI assistant that helps users learn about the Weaver platform. Your role is to explain how RAG (Retrieval-Augmented Generation) works, demonstrate best practices for building AI-powered knowledge bots, and encourage users to upload their own documents to create custom bots. Always be helpful, educational, and enthusiastic about the platform''s capabilities. When answering questions, cite the provided documentation and encourage exploration of Weaver''s features."}'::jsonb,
            NOW(),
            NOW()
        )
        ON CONFLICT (tenant_id) 
        DO UPDATE SET
            id = '00000000-0000-0000-0000-000000000001',
            name = 'Demo Bot',
            config_json = '{"system_prompt": "You are the Weaver Demo Bot, an AI assistant that helps users learn about the Weaver platform. Your role is to explain how RAG (Retrieval-Augmented Generation) works, demonstrate best practices for building AI-powered knowledge bots, and encourage users to upload their own documents to create custom bots. Always be helpful, educational, and enthusiastic about the platform''s capabilities. When answering questions, cite the provided documentation and encourage exploration of Weaver''s features."}'::jsonb,
            updated_at = NOW()
    """)
    
    # Create admin profile if DEMO_BOT_ADMIN_UUID is set
    # This UUID must match a Supabase auth.users.id
    admin_uuid = os.getenv('DEMO_BOT_ADMIN_UUID')
    admin_email = os.getenv('DEMO_BOT_ADMIN_EMAIL', 'admin@weaver.com')
    
    if admin_uuid:
        # Validate UUID format (basic check)
        try:
            import uuid
            uuid.UUID(admin_uuid)
            
            op.execute(f"""
                INSERT INTO profiles (id, tenant_id, email, role, created_at, updated_at)
                VALUES (
                    '{admin_uuid}',
                    '00000000-0000-0000-0000-000000000000',
                    '{admin_email}',
                    'owner',
                    NOW(),
                    NOW()
                )
                ON CONFLICT (id) DO NOTHING
            """)
            print(f"✓ Created admin profile for {admin_email} (UUID: {admin_uuid})")
        except ValueError:
            print(f"⚠ WARNING: Invalid DEMO_BOT_ADMIN_UUID format: {admin_uuid}. Skipping admin creation.")
    else:
        print("ℹ DEMO_BOT_ADMIN_UUID not set. Skipping admin profile creation.")
        print("  To create an admin later:")
        print("  1. Create user in Supabase Dashboard")
        print("  2. Set DEMO_BOT_ADMIN_UUID and DEMO_BOT_ADMIN_EMAIL")
        print("  3. Re-run migration or manually insert profile")


def downgrade() -> None:
    # Remove admin profile if it was created
    admin_uuid = os.getenv('DEMO_BOT_ADMIN_UUID')
    if admin_uuid:
        op.execute(f"DELETE FROM profiles WHERE id = '{admin_uuid}'")
    
    # Remove demo bot and tenant
    op.execute("DELETE FROM bots WHERE tenant_id = '00000000-0000-0000-0000-000000000000'")
    op.execute("DELETE FROM tenants WHERE id = '00000000-0000-0000-0000-000000000000'")

