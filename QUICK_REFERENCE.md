# Quick Reference Card

## 🚀 Start the App

```bash
# Development (hot-reload)
./start-dev.sh

# Production
./start.sh

# Stop
./stop.sh
```

## 📁 Project Structure

```
frontend/src/
├── components/ui/       # Reusable UI (Button, Card, Tabs, Input)
├── components/dashboard/# Feature components (Upload, APIKeys, Analytics)
├── pages/              # Routes (Login, AuthCallback, Dashboard)
├── hooks/              # React Query hooks (useDocuments, useAPIKeys)
├── store/              # Zustand stores (authStore)
├── lib/                # Utils (supabase, axios, utils)
└── types/              # TypeScript types
```

## 🔧 Common Commands

```bash
# Install dependencies
cd frontend && npm install

# Run dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## 🌐 Environment Variables

```bash
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_SITE_URL=http://localhost:3000
```

## 📦 Tech Stack

- **React 18** + **TypeScript**
- **Vite 5** (build tool)
- **React Router v6** (routing)
- **Zustand** (auth state)
- **TanStack Query** (server state)
- **Axios** (HTTP client)
- **Tailwind CSS** (styling)
- **shadcn/ui** (components)

## 🎣 Custom Hooks

```typescript
// Documents
import { useDocuments, useUploadDocument } from '@/hooks/useDocuments'
const { data: documents } = useDocuments(tenantId)
const uploadMutation = useUploadDocument(tenantId)

// API Keys
import { useAPIKeys, useCreateAPIKey, useRevokeAPIKey } from '@/hooks/useAPIKeys'
const { data: keys } = useAPIKeys(tenantId)
const createMutation = useCreateAPIKey(tenantId)
const revokeMutation = useRevokeAPIKey(tenantId)

// Auth
import { useAuthStore } from '@/store/authStore'
const { user, session, loading, signOut } = useAuthStore()
```

## 🎨 UI Components

```typescript
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'

<Button variant="destructive" size="lg">Delete</Button>
<Card><CardHeader><CardTitle>Title</CardTitle></CardHeader></Card>
```

## 🔐 Auth Flow

1. User clicks "Sign in with Google"
2. Redirected to Google OAuth
3. Callback to `/auth/callback`
4. Backend creates profile/tenant/bot
5. Redirected to `/dashboard`
6. Session persisted in Supabase

## 📤 Upload Flow

1. User selects file
2. `useUploadDocument` mutation
3. File uploaded to GCS
4. Celery worker processes document
5. Status polling (5s) via `useDocuments`
6. Status: pending → processing → completed

## 🔑 API Key Flow

1. User clicks "Create New API Key"
2. `useCreateAPIKey` mutation
3. Key displayed once (copy to clipboard)
4. Key stored in database (hashed)
5. User can revoke via `useRevokeAPIKey`

## 🧪 Testing Checklist

- [ ] OAuth login works
- [ ] Document upload works
- [ ] Status updates automatically
- [ ] API key creation works
- [ ] Copy to clipboard works
- [ ] API key revocation works
- [ ] Sign out works
- [ ] Hot-reload works (dev mode)

## 📚 Documentation

- `MIGRATION_COMPLETE.md` - Overview
- `MIGRATION_NOTES.md` - Technical details
- `FRONTEND_GUIDE.md` - Developer guide
- `TESTING_CHECKLIST.md` - Full testing guide

## 🐛 Debugging

```typescript
// React Query Devtools
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
<ReactQueryDevtools initialIsOpen={false} />

// Browser console
console.log('User:', useAuthStore.getState().user)
console.log('Session:', useAuthStore.getState().session)

// Docker logs
docker-compose logs -f api
docker-compose logs -f worker
docker-compose logs -f frontend
```

## 🔗 URLs

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

## 💡 Pro Tips

1. Use `./start-dev.sh` for development (instant hot-reload)
2. Check browser console for errors
3. Use React Query Devtools for debugging queries
4. Install Redux DevTools for Zustand state inspection
5. Use `cn()` utility for conditional Tailwind classes
6. Keep components small and focused
7. Extract logic into custom hooks
8. Always handle loading and error states

## 🆘 Common Issues

**Issue**: Hot-reload not working  
**Fix**: Ensure you're using `./start-dev.sh` and `docker-compose.dev.yml`

**Issue**: Environment variables not available  
**Fix**: Prefix with `VITE_` and rebuild

**Issue**: 404 on refresh  
**Fix**: Nginx config handles SPA routing (already configured)

**Issue**: Auth not persisting  
**Fix**: Check Supabase session in browser storage

**Issue**: Queries not refetching  
**Fix**: Check `queryKey` and `enabled` options in React Query

## 📞 Quick Links

- [Vite Docs](https://vitejs.dev/)
- [React Router](https://reactrouter.com/)
- [TanStack Query](https://tanstack.com/query/latest)
- [Zustand](https://docs.pmnd.rs/zustand/)
- [Tailwind CSS](https://tailwindcss.com/)
- [shadcn/ui](https://ui.shadcn.com/)

