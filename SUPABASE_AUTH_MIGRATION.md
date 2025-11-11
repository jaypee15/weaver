# Supabase Auth Migration (gotrue → supabase_auth)

## ⚠️ Deprecation Notice

The `gotrue` package has been deprecated as of **August 7, 2025** and will no longer receive updates. Supabase has replaced it with `supabase_auth` to align with their JavaScript library naming conventions.

## ✅ What We Did

### Updated Dependencies

**Before:**
```txt
supabase==2.3.4
gotrue==2.12.0  # Deprecated!
```

**After:**
```txt
supabase==2.12.1  # Latest version uses supabase_auth internally
```

### Why This Works

1. **We don't directly import `gotrue`** - It was only a transitive dependency of the `supabase` package
2. **Latest `supabase` package (v2.12.1)** uses `supabase_auth` internally
3. **No code changes needed** - Our code only imports from `supabase`, not `gotrue`

## 🔍 Verification

We verified that our codebase doesn't directly use `gotrue`:

```bash
# No direct imports found
grep -r "from gotrue import" backend/
grep -r "import gotrue" backend/
# Result: No matches
```

Our code only uses:
```python
from supabase import create_client, Client
```

## 📦 Package Update

The `supabase==2.12.1` package automatically uses `supabase_auth` as its dependency instead of `gotrue`.

### To Update

```bash
# In your Docker container or local environment
pip install --upgrade supabase==2.12.1
```

Or rebuild Docker images:
```bash
./stop.sh
./start.sh
```

## 🧪 Testing

After updating, verify everything works:

```bash
# 1. Start services
./start.sh

# 2. Test OAuth flow
# Open http://localhost:3000
# Click "Sign in with Google"
# Should work without issues

# 3. Check backend logs
docker-compose logs -f api
# Should see no errors related to gotrue or supabase_auth
```

## 📝 What Changed in supabase-py

### Version History

- **v2.3.4 and earlier**: Used `gotrue` package
- **v2.4.0+**: Transitioned to `supabase_auth` package
- **v2.12.1 (current)**: Fully uses `supabase_auth`

### Breaking Changes

**None for us!** Since we only import from `supabase`, the internal dependency change is transparent.

## 🔧 If You Were Using gotrue Directly

If you had code like this (we don't):

```python
# ❌ Old (deprecated)
from gotrue import User, Session
```

You would need to change it to:

```python
# ✅ New
from supabase_auth import User, Session
```

But since we only use:

```python
# ✅ Our code (no changes needed)
from supabase import create_client, Client

supabase = create_client(url, key)
user = supabase.auth.get_user(token)
```

**No changes are required!**

## 📊 Impact Summary

| Aspect | Impact | Action Required |
|--------|--------|-----------------|
| **Direct imports** | ✅ None | No changes needed |
| **Transitive dependency** | ✅ Handled by supabase package | Update supabase version |
| **Code changes** | ✅ None | No refactoring needed |
| **Testing** | ⚠️ Recommended | Test OAuth flow |
| **Documentation** | ✅ Updated | This document |

## 🚀 Deployment

### Local Development

```bash
# Rebuild containers with new dependencies
./stop.sh
./start.sh
```

### Production

Update your `requirements.txt` in production:

```txt
supabase==2.12.1
```

Then redeploy:

```bash
# Build new image
docker build -t gcr.io/PROJECT_ID/weaver-api:latest -f infra/docker/Dockerfile --target api .

# Push to registry
docker push gcr.io/PROJECT_ID/weaver-api:latest

# Deploy to Cloud Run
gcloud run services replace infra/deploy/cloudrun.yaml
```

## 🔗 References

- [Supabase Changelog - gotrue deprecation](https://supabase.com/changelog)
- [PyPI - gotrue deprecation notice](https://pypi.org/project/gotrue/)
- [PyPI - supabase_auth](https://pypi.org/project/supabase-auth/)
- [GitHub - supabase-py](https://github.com/supabase/supabase-py)

## ✅ Checklist

- [x] Updated `requirements.txt` to `supabase==2.12.1`
- [x] Removed explicit `gotrue==2.12.0` dependency
- [x] Verified no direct `gotrue` imports in codebase
- [x] Documented migration in this file
- [ ] Test OAuth flow after update
- [ ] Deploy to production

## 💡 Key Takeaway

**Since we only use the `supabase` package and don't directly import `gotrue`, updating to `supabase==2.12.1` automatically handles the migration to `supabase_auth` with zero code changes required!** 🎉

