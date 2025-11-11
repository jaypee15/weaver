# Testing Checklist for React Migration

## Pre-Testing Setup

- [ ] Ensure `.env` file is configured with all required variables:
  - `DATABASE_URL`
  - `SUPABASE_URL`
  - `SUPABASE_KEY`
  - `GOOGLE_API_KEY`
  - `GCS_BUCKET_NAME`
  - `GCS_ACCESS_KEY`
  - `GCS_SECRET_KEY`
  - `API_URL`
  - `SITE_URL`

- [ ] Start the application:
  ```bash
  ./start-dev.sh  # For development with hot-reload
  # OR
  ./start.sh      # For production build
  ```

- [ ] Verify all services are running:
  - Frontend: http://localhost:3000
  - Backend API: http://localhost:8000
  - API Docs: http://localhost:8000/docs

## 1. OAuth Authentication Flow

### Login Page
- [ ] Navigate to http://localhost:3000
- [ ] Verify Weaver branding and UI displays correctly
- [ ] Click "Sign in with Google" button
- [ ] Redirected to Google OAuth consent screen

### OAuth Callback
- [ ] After Google authentication, redirected to `/auth/callback`
- [ ] See "Completing sign in..." loading message
- [ ] Automatically redirected to `/dashboard`
- [ ] No errors in browser console

### Session Persistence
- [ ] Refresh the dashboard page
- [ ] User remains logged in (no redirect to login)
- [ ] User email displays in navigation bar
- [ ] Tenant data is loaded correctly

### First-Time User
- [ ] Sign in with a new Google account (not in database)
- [ ] Backend creates new profile, tenant, and bot automatically
- [ ] User is redirected to dashboard successfully
- [ ] Tenant ID is assigned and visible in API calls

## 2. Document Upload Flow

### Upload Interface
- [ ] Navigate to "Upload Documents" tab
- [ ] See file input and upload button
- [ ] See "Upload PDF, DOCX, TXT, or HTML files" instructions

### File Selection
- [ ] Click file input
- [ ] Select a test document (PDF, DOCX, TXT, or HTML)
- [ ] File name and size display correctly
- [ ] Upload button becomes enabled

### Upload Process
- [ ] Click "Upload" button
- [ ] Button shows "Uploading..." state
- [ ] Success message appears: "Document uploaded successfully! Processing in background..."
- [ ] File input is cleared
- [ ] Document appears in "Your Documents" list with "pending" status

### Status Updates (Polling)
- [ ] Document status changes from "pending" to "processing"
- [ ] Processing status shows spinner icon
- [ ] Status updates automatically every 5 seconds (no manual refresh needed)
- [ ] After processing completes, status changes to "completed"
- [ ] Completed status shows checkmark icon
- [ ] Success message: "Ready for querying! Your bot can now answer questions about this document."

### Document List
- [ ] All uploaded documents are visible
- [ ] Each document shows:
  - Filename
  - File size (in MB)
  - Upload date and time
  - Current status badge
- [ ] Documents are sorted by upload date (newest first)

### Error Handling
- [ ] Try uploading an invalid file type
- [ ] Error message displays clearly
- [ ] Try uploading a file > 200MB
- [ ] Appropriate error message shown

## 3. API Key Management

### API Keys Tab
- [ ] Navigate to "API Keys" tab
- [ ] See "Bot API Endpoint" information box
- [ ] Endpoint URL is correct: `POST {API_URL}/v1/tenants/{tenantId}/query`
- [ ] Example curl command is shown

### Create API Key
- [ ] Click "Create New API Key" button
- [ ] New key is generated and displayed
- [ ] Key is shown in yellow warning box
- [ ] Warning message: "save this, it won't be shown again"

### Copy API Key
- [ ] Click copy button next to the new key
- [ ] Button shows "Copied!" with checkmark
- [ ] Key is in clipboard (test by pasting)
- [ ] After 2 seconds, button returns to copy icon

### API Key List
- [ ] New key appears in "Your API Keys" list
- [ ] Key shows:
  - Name (auto-generated timestamp)
  - Created date
  - Rate limit (60 rpm)
- [ ] After using the key, "Last used" date appears

### Revoke API Key
- [ ] Click "Revoke" button on an API key
- [ ] Confirmation dialog appears (if implemented)
- [ ] Key status changes to "Revoked"
- [ ] Revoke button becomes disabled and shows "Revoked"
- [ ] Revoked key cannot be used for API calls

### Permissions
- [ ] Only users with "owner" or "admin" role can:
  - Create API keys
  - View API keys
  - Revoke API keys
- [ ] Regular users see "Admin or owner access required" error

## 4. Navigation & UI

### Tab Navigation
- [ ] Click "Upload Documents" tab - content changes
- [ ] Click "API Keys" tab - content changes
- [ ] Click "Analytics" tab - shows "Coming Soon" message
- [ ] Active tab is highlighted correctly
- [ ] Tab icons display properly

### Sign Out
- [ ] Click "Sign Out" button in navigation
- [ ] User is signed out
- [ ] Redirected to login page
- [ ] Session is cleared (no auto-login on refresh)

### Responsive Design
- [ ] Test on mobile viewport (< 768px)
- [ ] Test on tablet viewport (768px - 1024px)
- [ ] Test on desktop viewport (> 1024px)
- [ ] All elements are readable and accessible
- [ ] No horizontal scrolling

## 5. Real-time Features

### Document Status Polling
- [ ] Upload a document
- [ ] Open browser DevTools → Network tab
- [ ] See GET requests to `/v1/tenants/{tenantId}/docs` every 5 seconds
- [ ] Status updates appear without manual refresh
- [ ] Polling stops when navigating away from Upload tab

### Background Processing
- [ ] Upload multiple documents
- [ ] Navigate to API Keys tab
- [ ] Return to Upload Documents tab
- [ ] Document statuses have updated during absence

## 6. Error Handling

### Network Errors
- [ ] Stop the backend API (`docker stop weaver-api`)
- [ ] Try to upload a document
- [ ] Appropriate error message displays
- [ ] Try to create an API key
- [ ] Error is handled gracefully

### Authentication Errors
- [ ] Manually delete Supabase session from browser storage
- [ ] Refresh the page
- [ ] Redirected to login page
- [ ] No infinite redirect loops

### Invalid Data
- [ ] Try to access `/dashboard` without authentication
- [ ] Redirected to login page
- [ ] Try to access non-existent route (e.g., `/invalid`)
- [ ] Redirected to login or 404 page

## 7. Performance

### Initial Load
- [ ] Clear browser cache
- [ ] Navigate to http://localhost:3000
- [ ] Page loads in < 3 seconds
- [ ] No console errors or warnings

### Hot Reload (Dev Mode)
- [ ] Edit a component file (e.g., change button text)
- [ ] Save the file
- [ ] Page updates instantly without full reload
- [ ] State is preserved (if using Vite's HMR properly)

### Production Build
- [ ] Run `./start.sh` (production mode)
- [ ] Verify bundle size is optimized
- [ ] Check Lighthouse score (> 90 for Performance)

## 8. Browser Compatibility

Test in multiple browsers:
- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari
- [ ] Edge

## 9. API Integration

### Query Endpoint (via curl)
```bash
# Get an API key from the dashboard, then test:
curl -X POST http://localhost:8000/v1/tenants/{TENANT_ID}/query \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is this document about?"}'
```

- [ ] Response is returned successfully
- [ ] Response contains relevant answer
- [ ] Rate limiting works (test with > 60 requests/minute)

## 10. Console & Logs

### Browser Console
- [ ] No errors in browser console during normal usage
- [ ] No warnings about missing dependencies
- [ ] No memory leaks (check with Performance tab)

### Backend Logs
```bash
docker-compose logs -f api
docker-compose logs -f worker
```

- [ ] No errors during document processing
- [ ] Successful embedding generation logs
- [ ] No database connection errors

## Issues Found

Document any issues here:

| Issue | Severity | Steps to Reproduce | Status |
|-------|----------|-------------------|--------|
| Example: Button not clickable on mobile | Medium | 1. Open on iPhone, 2. Click upload | Fixed |

## Sign-off

- [ ] All critical features tested and working
- [ ] No blocking bugs found
- [ ] Performance is acceptable
- [ ] Ready for deployment

**Tested by**: _______________  
**Date**: _______________  
**Environment**: Development / Production  
**Browser(s)**: _______________

