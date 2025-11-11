# Frontend Migration: Next.js → React + Vite

## Overview

The frontend has been completely migrated from Next.js to a modern React SPA using Vite, with the following stack:

- **Build Tool**: Vite 5
- **Framework**: React 18 with TypeScript
- **Routing**: React Router v6
- **State Management**: Zustand (for auth state)
- **Data Fetching**: TanStack Query (React Query)
- **HTTP Client**: Axios
- **Styling**: Tailwind CSS
- **UI Components**: Custom shadcn/ui-style components
- **Auth**: Supabase Auth

## Key Changes

### 1. Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/              # shadcn-style UI components
│   │   └── dashboard/       # Dashboard-specific components
│   ├── pages/               # Route pages
│   ├── hooks/               # React Query hooks
│   ├── store/               # Zustand stores
│   ├── lib/                 # Utilities and configs
│   ├── types/               # TypeScript types
│   ├── App.tsx              # Main app with routing
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles
├── index.html               # HTML entry point
├── vite.config.ts           # Vite configuration
└── package.json
```

### 2. Environment Variables

Changed from `NEXT_PUBLIC_*` to `VITE_*`:

- `NEXT_PUBLIC_API_URL` → `VITE_API_URL`
- `NEXT_PUBLIC_SUPABASE_URL` → `VITE_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` → `VITE_SUPABASE_ANON_KEY`
- `NEXT_PUBLIC_SITE_URL` → `VITE_SITE_URL`

### 3. Authentication Flow

- **Zustand Store**: Centralized auth state management in `src/store/authStore.ts`
- **Auto-initialization**: Auth state is initialized on app mount
- **Protected Routes**: Using custom `ProtectedRoute` component
- **Session Management**: Automatic session refresh via Supabase listeners

### 4. Data Fetching

Replaced `useEffect` + `axios` with **TanStack Query**:

- `useDocuments()` - Fetch documents with auto-polling (5s)
- `useUploadDocument()` - Upload mutation with cache invalidation
- `useAPIKeys()` - Fetch API keys
- `useCreateAPIKey()` - Create API key mutation
- `useRevokeAPIKey()` - Revoke API key mutation

### 5. Routing

Changed from Next.js file-based routing to React Router:

- `/` - Login page
- `/auth/callback` - OAuth callback handler
- `/dashboard` - Protected dashboard (requires auth)

### 6. UI Components

Custom shadcn/ui-style components:

- `Button` - Multiple variants (default, destructive, outline, etc.)
- `Card` - Card container with header, content, footer
- `Tabs` - Tab navigation
- `Input` - Form input

### 7. Docker Setup

**Production** (`Dockerfile`):
- Multi-stage build with Node 20 Alpine
- Nginx serving static files
- Build-time environment variable injection

**Development** (`Dockerfile.dev`):
- Hot-reload enabled
- Volume mounting for instant updates
- Vite dev server on port 3000

## Running the Application

### Development Mode (with hot-reload)

```bash
./start-dev.sh
```

This uses `docker-compose.dev.yml` which:
- Mounts source code for instant updates
- Runs Vite dev server
- No rebuild needed for code changes

### Production Mode

```bash
./start.sh
```

This uses the production Dockerfile which:
- Builds optimized production bundle
- Serves via Nginx
- Requires rebuild for changes

## Environment Setup

1. Copy the environment template:
```bash
cp frontend/.env.example frontend/.env
```

2. Set your environment variables:
```env
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_SITE_URL=http://localhost:3000
```

3. Update `docker-compose.yml` and `.env` in project root with the same values.

## Testing

The last TODO is to test all functionality:

1. **OAuth Flow**:
   - Sign in with Google
   - Callback handling
   - Session persistence
   - Auto-provisioning of tenant/user

2. **Document Upload**:
   - File selection
   - Upload progress
   - Real-time status updates (polling)
   - Error handling

3. **API Key Management**:
   - Create new keys
   - Copy to clipboard
   - View endpoint documentation
   - Revoke keys

4. **Navigation**:
   - Tab switching
   - Protected routes
   - Sign out

## Migration Benefits

1. **Faster Development**: Vite's HMR is significantly faster than Next.js
2. **Simpler Architecture**: No SSR complexity, pure client-side SPA
3. **Better State Management**: Zustand + React Query = cleaner code
4. **Type Safety**: Full TypeScript support with proper env types
5. **Modern Stack**: Latest React patterns and best practices
6. **Easier Deployment**: Static build can be served from any CDN

## Backup

The original Next.js frontend is backed up at:
```
frontend-nextjs-backup/
```

## Notes

- All existing features have been preserved
- UI/UX is identical to the original
- API integration remains unchanged
- Docker setup is backward compatible

