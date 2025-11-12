# Demo Bot Admin User Implementation

## Overview

Added support for creating an admin user in the demo bot migration using environment variables. The admin user is linked to the demo bot tenant and can upload/manage demo content.

## Changes Made

### 1. Migration Update
**File:** `backend/alembic/versions/004_create_demo_bot.py`

**What Changed:**
- Added `import os` for environment variable access
- Added admin profile creation logic (optional, based on env vars)
- Added UUID validation before insertion
- Added helpful console output messages
- Updated downgrade to remove admin profile

**Key Features:**
```python
# Reads environment variables
admin_uuid = os.getenv('DEMO_BOT_ADMIN_UUID')
admin_email = os.getenv('DEMO_BOT_ADMIN_EMAIL', 'admin@weaver.com')

# Validates UUID format
uuid.UUID(admin_uuid)

# Creates profile linked to demo tenant
INSERT INTO profiles (id, tenant_id, email, role, ...)
VALUES (admin_uuid, demo_tenant_id, admin_email, 'owner', ...)

# Provides clear feedback
print("✓ Created admin profile for {email} (UUID: {uuid})")
```

### 2. Environment Configuration
**Files:** `docker-compose.yml`, `env.template`

**Added Variables:**
```bash
DEMO_BOT_ADMIN_UUID=          # Supabase user UUID (leave empty to skip)
DEMO_BOT_ADMIN_EMAIL=admin@weaver.com  # Admin email (must match Supabase)
```

**Docker Compose:**
```yaml
api:
  environment:
    # ... existing vars ...
    - DEMO_BOT_ADMIN_UUID=${DEMO_BOT_ADMIN_UUID:-}
    - DEMO_BOT_ADMIN_EMAIL=${DEMO_BOT_ADMIN_EMAIL:-admin@weaver.com}
```

### 3. Documentation Updates

**Created:**
- `DEMO_BOT_ADMIN_SETUP.md` - Quick start guide (5-minute setup)

**Updated:**
- `DEMO_BOT_SETUP.md` - Added detailed admin setup steps
- `DEMO_BOT_IMPLEMENTATION.md` - Updated next steps section
- `README.md` - Added admin setup to demo bot section

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Supabase Dashboard                        │
│                                                             │
│  1. Create User                                             │
│     Email: admin@weaver.com                                 │
│     Password: [secure]                                      │
│     Auto Confirm: ✅                                         │
│     ↓                                                        │
│  2. Copy User UUID                                          │
│     a1b2c3d4-e5f6-7890-abcd-ef1234567890                   │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                    .env File                                │
│                                                             │
│  DEMO_BOT_ADMIN_UUID=a1b2c3d4-e5f6-7890-abcd-ef1234567890  │
│  DEMO_BOT_ADMIN_EMAIL=admin@weaver.com                     │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│              Alembic Migration (004)                        │
│                                                             │
│  1. Create demo tenant                                      │
│  2. Create demo bot                                         │
│  3. IF DEMO_BOT_ADMIN_UUID set:                             │
│     - Validate UUID format                                  │
│     - Insert profile with:                                  │
│       • id = DEMO_BOT_ADMIN_UUID (from Supabase)           │
│       • tenant_id = demo_bot_id                            │
│       • email = DEMO_BOT_ADMIN_EMAIL                       │
│       • role = 'owner'                                      │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                    Database State                           │
│                                                             │
│  profiles table:                                            │
│  ┌──────────────┬─────────────────┬────────────┬────────┐  │
│  │      id      │      email      │ tenant_id  │  role  │  │
│  ├──────────────┼─────────────────┼────────────┼────────┤  │
│  │ a1b2c3d4-... │admin@weaver.com │ 00000000...│ owner  │  │
│  └──────────────┴─────────────────┴────────────┴────────┘  │
│                                                             │
│  Admin can now:                                             │
│  ✅ Login via Supabase auth                                 │
│  ✅ Access demo bot tenant dashboard                        │
│  ✅ Upload documents to demo bot                            │
│  ✅ Create API keys for demo bot                            │
└─────────────────────────────────────────────────────────────┘
```

### Key Constraints

1. **`profiles.id` MUST match Supabase `auth.users.id`**
   - Cannot create a profile without Supabase user
   - UUID must be copied from Supabase Dashboard

2. **Email must match**
   - `DEMO_BOT_ADMIN_EMAIL` must match Supabase user's email
   - Used for login and display

3. **Optional but recommended**
   - If variables not set, migration still succeeds
   - Admin can be created manually later

## Setup Workflow

### For Fresh Installation

1. **Create Supabase user** (Supabase Dashboard)
2. **Copy UUID** from user list
3. **Set environment variables** in `.env`
4. **Run `docker-compose up`** (migration runs automatically)
5. **Login as admin** and upload content

### For Existing Installation

1. **Create Supabase user** (Supabase Dashboard)
2. **Copy UUID** from user list
3. **Set environment variables** in `.env`
4. **Restart API**: `docker-compose restart api`
5. **Re-run migration**:
   ```bash
   docker-compose exec api alembic downgrade -1
   docker-compose exec api alembic upgrade head
   ```
6. **Login as admin** and upload content

### Without Environment Variables

Migration output:
```
ℹ DEMO_BOT_ADMIN_UUID not set. Skipping admin profile creation.
  To create an admin later:
  1. Create user in Supabase Dashboard
  2. Set DEMO_BOT_ADMIN_UUID and DEMO_BOT_ADMIN_EMAIL
  3. Re-run migration or manually insert profile
```

## Benefits

### 1. Flexible Setup
- ✅ Admin creation is optional
- ✅ Can be done during initial setup or later
- ✅ No code changes needed, just env vars

### 2. Secure by Default
- ✅ Requires Supabase user (proper authentication)
- ✅ UUID must exist in Supabase before profile creation
- ✅ Validates UUID format before insertion

### 3. Clear Feedback
- ✅ Migration prints success messages
- ✅ Warning if UUID format is invalid
- ✅ Instructions if variables not set

### 4. Idempotent
- ✅ Uses `ON CONFLICT DO NOTHING`
- ✅ Can re-run migration safely
- ✅ Downgrade removes admin profile

## Testing

### Verify Admin Creation

```bash
# Check if admin profile exists
docker-compose exec api psql $DATABASE_URL -c "
  SELECT 
    p.id,
    p.email,
    p.tenant_id,
    p.role,
    t.name as tenant_name
  FROM profiles p
  JOIN tenants t ON p.tenant_id = t.id
  WHERE p.email = 'admin@weaver.com';
"
```

Expected output:
```
              id              |       email        |             tenant_id              | role  |   tenant_name    
------------------------------+--------------------+------------------------------------+-------+------------------
 a1b2c3d4-e5f6-7890-abcd-... | admin@weaver.com   | 00000000-0000-0000-0000-000000000000 | owner | Weaver Demo Bot
```

### Test Admin Login

1. **Go to frontend**: `http://localhost:3000`
2. **Click "Sign in"**
3. **Use email/password** or Google OAuth
4. **Should land on dashboard** with demo bot tenant

### Test Document Upload

1. **Navigate to Upload tab**
2. **Upload a PDF**
3. **Should see "pending" → "processing" → "completed"**
4. **Document should appear in list**

## Troubleshooting

### Admin profile not created

**Symptoms:**
- Migration says "Skipping admin profile creation"
- Can't login as admin

**Solutions:**
1. Check `.env` file has `DEMO_BOT_ADMIN_UUID` set
2. Restart containers: `docker-compose restart api`
3. Re-run migration:
   ```bash
   docker-compose exec api alembic downgrade -1
   docker-compose exec api alembic upgrade head
   ```

### Invalid UUID format error

**Symptoms:**
- Migration prints "WARNING: Invalid DEMO_BOT_ADMIN_UUID format"

**Solutions:**
1. Verify UUID is in format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
2. Copy directly from Supabase Dashboard
3. Remove any quotes, spaces, or extra characters

### User not found when logging in

**Symptoms:**
- Can't login with admin credentials
- "User not found" error

**Solutions:**
1. Verify user exists in Supabase Dashboard
2. Check "Confirmed At" column has a timestamp
3. If not confirmed, manually confirm in Supabase Dashboard

### 403 Forbidden when uploading

**Symptoms:**
- Admin can login but can't upload documents

**Solutions:**
1. Verify `tenant_id` in profiles table is demo bot ID
2. Verify `role` is `owner` or `admin`
3. Check if admin user is in correct tenant

## Alternative: Manual Admin Creation

If migration approach doesn't work, create admin manually:

```sql
-- After creating user in Supabase
INSERT INTO profiles (id, tenant_id, email, role, created_at, updated_at)
VALUES (
    'YOUR_SUPABASE_USER_UUID',
    '00000000-0000-0000-0000-000000000000',
    'admin@weaver.com',
    'owner',
    NOW(),
    NOW()
)
ON CONFLICT (id) DO NOTHING;
```

Run via psql:
```bash
docker-compose exec api psql $DATABASE_URL -c "
  INSERT INTO profiles (id, tenant_id, email, role, created_at, updated_at)
  VALUES (
      'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
      '00000000-0000-0000-0000-000000000000',
      'admin@weaver.com',
      'owner',
      NOW(),
      NOW()
  )
  ON CONFLICT (id) DO NOTHING;
"
```

## Files Modified

- ✅ `backend/alembic/versions/004_create_demo_bot.py` - Added admin creation logic
- ✅ `docker-compose.yml` - Added environment variables
- ✅ `env.template` - Added admin config section
- ✅ `DEMO_BOT_SETUP.md` - Updated with admin setup steps
- ✅ `DEMO_BOT_IMPLEMENTATION.md` - Updated next steps
- ✅ `README.md` - Added admin setup to demo bot section
- ✅ `DEMO_BOT_ADMIN_SETUP.md` - NEW: Quick start guide

## Summary

✅ **Admin creation is now automated via migration**  
✅ **Uses environment variables for flexibility**  
✅ **Validates UUID format before insertion**  
✅ **Provides clear feedback during migration**  
✅ **Optional - migration succeeds without admin**  
✅ **Idempotent - safe to re-run**  
✅ **Secure - requires Supabase user first**  

The admin user is ready to upload demo content once the migration completes successfully! 🎉

