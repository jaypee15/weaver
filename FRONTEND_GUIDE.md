# Frontend Developer Guide

## Tech Stack

- **React 18** - UI library
- **Vite 5** - Build tool and dev server
- **TypeScript** - Type safety
- **React Router v6** - Client-side routing
- **Zustand** - Lightweight state management
- **TanStack Query** - Server state management
- **Axios** - HTTP client
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - Accessible component patterns
- **Supabase** - Authentication

## Project Structure

```
src/
├── components/
│   ├── ui/                    # Reusable UI components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── tabs.tsx
│   │   └── input.tsx
│   └── dashboard/             # Feature-specific components
│       ├── UploadTab.tsx
│       ├── APIKeysTab.tsx
│       └── AnalyticsTab.tsx
├── pages/                     # Route pages
│   ├── Login.tsx
│   ├── AuthCallback.tsx
│   └── Dashboard.tsx
├── hooks/                     # Custom React hooks
│   ├── useDocuments.ts        # Document queries & mutations
│   └── useAPIKeys.ts          # API key queries & mutations
├── store/                     # Zustand stores
│   └── authStore.ts           # Authentication state
├── lib/                       # Utilities and configs
│   ├── supabase.ts            # Supabase client
│   ├── axios.ts               # Axios instance
│   └── utils.ts               # Helper functions
├── types/                     # TypeScript types
│   └── index.ts
├── App.tsx                    # Main app with routing
├── main.tsx                   # Entry point
└── index.css                  # Global styles
```

## Key Concepts

### 1. Authentication (Zustand)

The auth store (`src/store/authStore.ts`) manages:
- Supabase session
- User profile from backend
- Auto-initialization on app mount
- Session persistence

```typescript
import { useAuthStore } from '@/store/authStore'

function MyComponent() {
  const { user, session, loading, signOut } = useAuthStore()
  
  // user contains: { id, email, tenant_id, role }
  // session is the Supabase session
}
```

### 2. Data Fetching (TanStack Query)

All API calls use React Query hooks:

```typescript
import { useDocuments, useUploadDocument } from '@/hooks/useDocuments'

function UploadTab({ tenantId }) {
  // Queries
  const { data: documents, isLoading } = useDocuments(tenantId)
  
  // Mutations
  const uploadMutation = useUploadDocument(tenantId)
  
  const handleUpload = async (file: File) => {
    await uploadMutation.mutateAsync(file)
    // Cache is automatically invalidated and refetched
  }
}
```

Benefits:
- Automatic caching
- Background refetching
- Optimistic updates
- Error handling
- Loading states

### 3. Routing (React Router)

Routes are defined in `App.tsx`:

```typescript
<Routes>
  <Route path="/" element={<Login />} />
  <Route path="/auth/callback" element={<AuthCallback />} />
  <Route path="/dashboard" element={
    <ProtectedRoute>
      <Dashboard />
    </ProtectedRoute>
  } />
</Routes>
```

Protected routes check for authentication before rendering.

### 4. Styling (Tailwind + shadcn/ui)

Use Tailwind utility classes:

```tsx
<div className="flex items-center gap-4 p-6 bg-white rounded-lg shadow">
  <Button variant="destructive" size="lg">
    Delete
  </Button>
</div>
```

Custom components follow shadcn/ui patterns for consistency.

### 5. Environment Variables

All env vars must be prefixed with `VITE_`:

```typescript
// ✅ Correct
const apiUrl = import.meta.env.VITE_API_URL

// ❌ Wrong
const apiUrl = process.env.API_URL
```

## Development Workflow

### Local Development (without Docker)

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Create `.env`:
```bash
cp .env.example .env
# Edit .env with your values
```

3. Start dev server:
```bash
npm run dev
```

4. Open http://localhost:3000

### Docker Development (with hot-reload)

```bash
# From project root
./start-dev.sh
```

Changes to `src/` files will automatically reload.

### Production Build

```bash
npm run build
npm run preview  # Test production build locally
```

## Adding New Features

### 1. New API Endpoint

Create a custom hook in `src/hooks/`:

```typescript
// src/hooks/useMyFeature.ts
import { useQuery, useMutation } from '@tanstack/react-query'
import { apiClient } from '@/lib/axios'
import { useAuthStore } from '@/store/authStore'

export function useMyData(tenantId: string) {
  const session = useAuthStore((state) => state.session)
  
  return useQuery({
    queryKey: ['myData', tenantId],
    queryFn: async () => {
      const response = await apiClient.get(`/v1/tenants/${tenantId}/my-endpoint`, {
        headers: { Authorization: `Bearer ${session?.access_token}` }
      })
      return response.data
    },
    enabled: !!tenantId && !!session,
  })
}
```

### 2. New UI Component

Follow shadcn/ui patterns in `src/components/ui/`:

```typescript
// src/components/ui/badge.tsx
import * as React from 'react'
import { cn } from '@/lib/utils'

interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'success' | 'warning' | 'error'
}

export function Badge({ className, variant = 'default', ...props }: BadgeProps) {
  return (
    <div
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold',
        {
          'bg-gray-100 text-gray-800': variant === 'default',
          'bg-green-100 text-green-800': variant === 'success',
          'bg-yellow-100 text-yellow-800': variant === 'warning',
          'bg-red-100 text-red-800': variant === 'error',
        },
        className
      )}
      {...props}
    />
  )
}
```

### 3. New Page/Route

1. Create page component in `src/pages/`
2. Add route in `App.tsx`
3. Add navigation link where needed

## Common Patterns

### Loading States

```typescript
const { data, isLoading, error } = useMyQuery()

if (isLoading) return <div>Loading...</div>
if (error) return <div>Error: {error.message}</div>
return <div>{data}</div>
```

### Form Handling

```typescript
const [value, setValue] = useState('')
const mutation = useMyMutation()

const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault()
  try {
    await mutation.mutateAsync(value)
    setValue('') // Reset form
  } catch (error) {
    console.error(error)
  }
}
```

### Conditional Rendering

```typescript
{user?.role === 'admin' && (
  <Button>Admin Only</Button>
)}

{documents.length === 0 ? (
  <p>No documents yet</p>
) : (
  <DocumentList documents={documents} />
)}
```

## Debugging

### React Query Devtools

Add to `App.tsx` for debugging queries:

```typescript
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}
```

### Zustand Devtools

Install Redux DevTools extension to inspect Zustand state.

## Best Practices

1. **Use TypeScript**: Define types for all props and API responses
2. **Extract components**: Keep components small and focused
3. **Use custom hooks**: Encapsulate logic in reusable hooks
4. **Handle errors**: Always handle loading and error states
5. **Optimize queries**: Use proper `queryKey` and `enabled` options
6. **Avoid prop drilling**: Use Zustand for global state
7. **Keep styles consistent**: Use Tailwind utilities and design tokens
8. **Test responsiveness**: Mobile-first approach

## Resources

- [Vite Docs](https://vitejs.dev/)
- [React Router Docs](https://reactrouter.com/)
- [TanStack Query Docs](https://tanstack.com/query/latest)
- [Zustand Docs](https://docs.pmnd.rs/zustand/getting-started/introduction)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [shadcn/ui](https://ui.shadcn.com/)

