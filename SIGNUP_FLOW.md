# User Signup Flow Documentation

## Overview

Weaver uses a **hybrid authentication approach**:
- **Frontend → Supabase**: OAuth (Google login) handled directly by Supabase
- **Backend**: Verifies JWT and manages tenant/user/bot data in the application database

## Complete Signup Flow

```
┌─────────────┐
│   User      │
│ clicks      │
│ "Sign in    │
│ with Google"│
└──────┬──────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│ Frontend: supabase.auth.signInWithOAuth({ provider: ... })│
└──────┬───────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│ Supabase: Redirects to Google OAuth                      │
└──────┬───────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│ Google: User authorizes                                   │
└──────┬───────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│ Redirect: /auth/callback?code=...                        │
└──────┬───────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│ Frontend: Exchange code for session                       │
│ supabase.auth.exchangeCodeForSession(code)               │
└──────┬───────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│ Frontend: Call backend to complete signup                │
│ POST /v1/auth/complete-signup                            │
│ Authorization: Bearer <JWT from Supabase>                │
└──────┬───────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│ Backend: Verify JWT with Supabase                        │
│ - Extract user_id and email from JWT                     │
│ - Check if user exists in our database                   │
└──────┬───────────────────────────────────────────────────┘
       │
       ├─── User exists? ───┐
       │                    │
       ▼ NO                 ▼ YES
┌──────────────────┐  ┌──────────────────┐
│ Create:          │  │ Return:          │
│ 1. Tenant        │  │ - tenant_id      │
│ 2. User          │  │ - user_id        │
│ 3. Bot (trigger) │  │ - email          │
│                  │  │ - role           │
│ Return data      │  │ is_new_user=false│
│ is_new_user=true │  └──────────────────┘
└──────────────────┘
       │
       └──────────────┬──────────────┘
                      │
                      ▼
           ┌──────────────────┐
           │ Redirect to      │
           │ /dashboard       │
           └──────────────────┘
                      │
                      ▼
           ┌──────────────────┐
           │ Dashboard loads  │
           │ GET /users/me    │
           │ (gets tenant_id) │
           └──────────────────┘
```

## Architecture Components

### Frontend (Next.js)

**Files:**
- `app/page.tsx` - Landing page with Google OAuth button
- `app/auth/callback/route.ts` - OAuth callback handler
- `app/dashboard/page.tsx` - Dashboard (fetches user data)

**Flow:**
1. User clicks "Sign in with Google"
2. Supabase handles OAuth flow
3. Callback route exchanges code for session
4. Calls `POST /v1/auth/complete-signup` to create tenant/user/bot
5. Redirects to dashboard
6. Dashboard calls `GET /v1/users/me` to get tenant_id

### Backend (FastAPI)

**Files:**
- `app/api/v1/routes.py` - Signup endpoints
- `app/auth/oauth.py` - JWT verification
- `app/db/repositories.py` - Database operations
- `app/db/models.py` - SQLAlchemy ORM models

**Endpoints:**

#### `POST /v1/auth/complete-signup`
Creates tenant, user, and bot for first-time OAuth users.

**Request:**
```http
POST /v1/auth/complete-signup
Authorization: Bearer <Supabase JWT>
```

**Response:**
```json
{
  "tenant_id": "uuid",
  "user_id": "uuid",
  "email": "user@example.com",
  "role": "owner",
  "is_new_user": true,
  "message": "Account created successfully!"
}
```

**Logic:**
1. Verify JWT with Supabase
2. Check if user exists in database
3. If new user:
   - Create tenant (name from email)
   - Create user record
   - Bot auto-created via database trigger
4. If existing user:
   - Return existing data with `is_new_user: false`

#### `GET /v1/users/me`
Returns current user information.

**Request:**
```http
GET /v1/users/me
Authorization: Bearer <Supabase JWT>
```

**Response:**
```json
{
  "user_id": "uuid",
  "tenant_id": "uuid",
  "email": "user@example.com",
  "role": "owner"
}
```

## Database Schema

### Tables Created on Signup

**1. `tenants`**
```sql
id UUID PRIMARY KEY
name VARCHAR(255)
plan_tier VARCHAR(50) DEFAULT 'free'
storage_used_bytes BIGINT DEFAULT 0
created_at TIMESTAMP
updated_at TIMESTAMP
```

**2. `users`**
```sql
id UUID PRIMARY KEY  -- Same as Supabase user ID
tenant_id UUID REFERENCES tenants(id)
email VARCHAR(255) UNIQUE
role VARCHAR(50) DEFAULT 'member'
created_at TIMESTAMP
updated_at TIMESTAMP
```

**3. `bots`** (auto-created via trigger)
```sql
id UUID PRIMARY KEY  -- Same as tenant_id
tenant_id UUID UNIQUE REFERENCES tenants(id)
name VARCHAR(255)
config_json JSONB DEFAULT {}
created_at TIMESTAMP
updated_at TIMESTAMP
```

### Database Trigger

The `bots` table is automatically populated via a PostgreSQL trigger:

```sql
CREATE FUNCTION create_bot_for_tenant()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO bots (id, tenant_id, name, config_json)
    VALUES (NEW.id, NEW.id, NEW.name || ' Bot', '{"temperature": 0.2, "top_k": 8}')
    ON CONFLICT (tenant_id) DO NOTHING;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER create_bot_on_tenant_insert 
AFTER INSERT ON tenants 
FOR EACH ROW EXECUTE FUNCTION create_bot_for_tenant();
```

## Key Design Decisions

### ✅ Why Frontend → Supabase Direct?

**Pros:**
- Supabase handles OAuth complexity (redirects, tokens, security)
- No need to implement OAuth flow in backend
- Frontend gets JWT directly
- Reduced backend complexity
- Standard pattern for Supabase + custom backend

**What Backend Does:**
- Verifies JWT tokens
- Manages application-specific data (tenants, bots)
- Enforces business logic

### ✅ One Bot Per Tenant

- `bot_id = tenant_id` (simplifies architecture)
- Bot auto-created via database trigger
- No bot CRUD endpoints needed
- Tenant is the namespace for all data

### ✅ Idempotent Signup

The `POST /v1/auth/complete-signup` endpoint is **idempotent**:
- Can be called multiple times safely
- Returns existing data if user already exists
- No errors on duplicate calls

## Error Handling

### Frontend Fallback

The dashboard has a fallback in case the callback doesn't complete signup:

```typescript
try {
  const response = await axios.get(`${API_URL}/v1/users/me`)
  setTenantId(response.data.tenant_id)
} catch (error) {
  if (error.response?.status === 404) {
    // User not found - complete signup now
    const signupResponse = await axios.post(
      `${API_URL}/v1/auth/complete-signup`,
      {},
      { headers: { Authorization: `Bearer ${session.access_token}` } }
    )
    setTenantId(signupResponse.data.tenant_id)
  }
}
```

### Backend Error Handling

- JWT verification failures → 401 Unauthorized
- Database errors → 500 Internal Server Error
- Duplicate user creation → Returns existing data (idempotent)

## Testing the Flow

### Manual Test

1. **Start services:**
   ```bash
   ./start.sh
   ```

2. **Open frontend:**
   ```
   http://localhost:3000
   ```

3. **Click "Sign in with Google"**

4. **Authorize with Google**

5. **Check logs:**
   ```bash
   # Backend logs
   docker-compose logs -f api
   
   # Should see:
   # - POST /v1/auth/complete-signup
   # - Tenant created
   # - User created
   # - Bot created (via trigger)
   ```

6. **Verify database:**
   ```bash
   docker-compose exec postgres psql -U weaver -d weaver
   
   SELECT * FROM tenants;
   SELECT * FROM users;
   SELECT * FROM bots;
   ```

### API Test

```bash
# 1. Get JWT from Supabase (after OAuth)
TOKEN="<your-jwt-token>"

# 2. Complete signup
curl -X POST http://localhost:8000/v1/auth/complete-signup \
  -H "Authorization: Bearer $TOKEN"

# 3. Get user info
curl http://localhost:8000/v1/users/me \
  -H "Authorization: Bearer $TOKEN"
```

## Security Considerations

### ✅ JWT Verification

- All requests verify JWT with Supabase
- JWT contains user_id and email (signed by Supabase)
- Backend validates signature using `SUPABASE_JWT_SECRET`

### ✅ Tenant Isolation

- All API endpoints require `tenant_id`
- Backend verifies user belongs to tenant
- Database queries filter by `tenant_id`

### ✅ No Password Storage

- Passwords managed by Supabase
- Backend never sees passwords
- OAuth tokens handled by Supabase

## Environment Variables

### Backend

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_JWT_SECRET=your_jwt_secret
DATABASE_URL=postgresql+asyncpg://...
```

### Frontend

```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Troubleshooting

### User Not Found (404)

**Symptom:** Dashboard shows error after OAuth

**Fix:** The dashboard now has automatic fallback to call `/auth/complete-signup`

### Tenant Not Created

**Symptom:** Signup succeeds but no tenant in database

**Check:**
1. Database trigger exists: `\df create_bot_for_tenant` in psql
2. Backend logs for errors
3. Database connection

### OAuth Redirect Fails

**Symptom:** Google OAuth doesn't redirect back

**Check:**
1. Supabase OAuth callback URL: `http://localhost:3000/auth/callback`
2. Google OAuth credentials in Supabase
3. Frontend environment variables

## Future Enhancements

- [ ] Email verification flow
- [ ] Invite team members
- [ ] Multi-tenant user support (one user, multiple tenants)
- [ ] Custom tenant names during signup
- [ ] Onboarding wizard
- [ ] Welcome email

## Summary

✅ **Frontend** calls Supabase directly for OAuth  
✅ **Backend** verifies JWT and manages application data  
✅ **Signup** creates tenant → user → bot (via trigger)  
✅ **Idempotent** - safe to call multiple times  
✅ **Secure** - JWT verification, tenant isolation  
✅ **Simple** - Standard Supabase + custom backend pattern  

The missing piece has been implemented! 🎉

