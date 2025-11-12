# Demo Bot Admin Setup - Quick Reference

This guide shows you how to create an admin user for managing the demo bot content.

## Why Do You Need an Admin?

The demo bot needs documents to answer questions. To upload these documents, you need a user account that:
1. Exists in Supabase (for authentication)
2. Is linked to the demo bot tenant in your database
3. Has "owner" role permissions

## Setup Steps (5 Minutes)

### Step 1: Create User in Supabase Dashboard

1. **Open Supabase Dashboard**
   - Go to your Supabase project: `https://app.supabase.com/project/YOUR_PROJECT`

2. **Navigate to Authentication**
   - Click **"Authentication"** in the left sidebar
   - Click **"Users"** tab

3. **Add New User**
   - Click the **"Add user"** button
   - Fill in the form:
     ```
     Email: admin@weaver.com
     Password: [Choose a secure password]
     Auto Confirm User: ✅ (Enable this!)
     ```
   - Click **"Create user"**

4. **Copy the User UUID**
   - Find the new user in the list
   - Look for the **"ID"** column (UUID format)
   - Example: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`
   - **Copy this UUID** - you'll need it in the next step

### Step 2: Configure Environment Variables

1. **Open your `.env` file** in the project root

2. **Add these lines** (or update if they exist):
   ```bash
   # Demo Bot Admin User
   DEMO_BOT_ADMIN_UUID=a1b2c3d4-e5f6-7890-abcd-ef1234567890  # Replace with your UUID
   DEMO_BOT_ADMIN_EMAIL=admin@weaver.com  # Must match Supabase email
   ```

3. **Save the file**

### Step 3: Run Migration

1. **Restart the API service** to pick up the new environment variables:
   ```bash
   docker-compose restart api
   ```

2. **Run the migration**:
   ```bash
   docker-compose exec api alembic upgrade head
   ```

3. **Verify success** - you should see:
   ```
   ✓ Created admin profile for admin@weaver.com (UUID: a1b2c3d4-...)
   ```

   If you see this instead:
   ```
   ℹ DEMO_BOT_ADMIN_UUID not set. Skipping admin profile creation.
   ```
   Then the environment variables weren't loaded. Try:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### Step 4: Login as Admin

1. **Open the frontend**:
   ```
   http://localhost:3000
   ```

2. **Click "Sign in with Google"** or use email/password login

3. **Enter admin credentials**:
   - Email: `admin@weaver.com`
   - Password: [the password you set in Supabase]

4. **You should land on the dashboard** with the demo bot tenant

### Step 5: Upload Demo Documents

1. **Go to the "Upload" tab**

2. **Upload 3-5 PDF documents** about:
   - What is Weaver? (Platform overview)
   - How RAG works (Technical explanation)
   - API documentation (Integration guide)
   - FAQ (Common questions)
   - Use cases (Example applications)

3. **Wait for processing** - documents will show "completed" status when ready

4. **Test the demo bot** in the API Keys tab

## Verification Checklist

- [ ] Admin user exists in Supabase Dashboard
- [ ] Admin UUID copied correctly
- [ ] `.env` file updated with UUID and email
- [ ] API service restarted
- [ ] Migration run successfully
- [ ] Success message: "Created admin profile for..."
- [ ] Can login as admin via frontend
- [ ] Dashboard shows demo bot tenant ID (`00000000-0000-0000-0000-000000000000`)
- [ ] Can upload documents successfully
- [ ] Documents show "completed" status
- [ ] Demo bot responds to queries

## Troubleshooting

### "User not found" when logging in

**Problem:** Can't login with admin credentials

**Solutions:**
1. Verify user exists in Supabase Dashboard → Authentication → Users
2. Check "Confirmed At" column - should have a timestamp (not blank)
3. If blank, click the user → "Send confirmation email" or manually confirm

### "Admin profile not created" in migration

**Problem:** Migration says "Skipping admin profile creation"

**Solutions:**
1. Check `.env` file has `DEMO_BOT_ADMIN_UUID` set
2. Verify UUID format is correct (no extra spaces, quotes, etc.)
3. Restart containers: `docker-compose down && docker-compose up -d`
4. Re-run migration: `docker-compose exec api alembic downgrade -1 && docker-compose exec api alembic upgrade head`

### "Tenant ID mismatch" when trying to upload

**Problem:** 403 Forbidden when uploading to demo bot tenant

**Solutions:**
1. Verify admin profile exists in database:
   ```bash
   docker-compose exec api psql $DATABASE_URL -c "
     SELECT id, email, tenant_id, role 
     FROM profiles 
     WHERE email = 'admin@weaver.com';
   "
   ```
2. Check that `tenant_id` is `00000000-0000-0000-0000-000000000000`
3. Check that `role` is `owner` or `admin`

### UUID format error in migration

**Problem:** Migration fails with "Invalid DEMO_BOT_ADMIN_UUID format"

**Solutions:**
1. Verify UUID is in correct format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
2. No extra quotes, spaces, or characters
3. Copy directly from Supabase Dashboard

## Database Verification

Check if the admin profile was created correctly:

```bash
# Check if profile exists
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

## Alternative: Manual Profile Creation

If the migration approach doesn't work, you can manually create the profile:

1. **Create user in Supabase** (as in Step 1)

2. **Manually insert profile**:
   ```sql
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

3. **Run via psql**:
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

## Security Notes

- ✅ Admin can only upload to demo bot tenant
- ✅ Admin cannot access other users' data
- ✅ Admin role is for content management only
- ✅ Use a strong password for the admin account
- ⚠️ In production, use a non-obvious email (not `admin@...`)
- ⚠️ Consider creating multiple admin users with separate emails

## Next Steps After Setup

1. **Upload quality demo content** (3-5 well-written PDFs)
2. **Test queries** as a regular user to verify responses
3. **Monitor performance** in the Analytics tab
4. **Update content** periodically to keep it relevant
5. **Share the demo bot** with new users for onboarding

---

**Need Help?**
- See `DEMO_BOT_SETUP.md` for comprehensive documentation
- Check `DEMO_BOT_IMPLEMENTATION.md` for technical details
- Review `DEMO_BOT_TEST_PLAN.md` for testing checklist

