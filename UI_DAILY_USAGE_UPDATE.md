# UI Daily Usage Display - Implementation

## Overview

Added real-time daily usage tracking to the Analytics tab, showing users their current query usage with visual indicators.

## Changes Made

### 1. New Hook: `useDailyUsage.ts`

Created a React Query hook to fetch daily usage data:

```typescript
export const useDailyUsage = (tenantId: string) => {
  return useQuery<DailyUsage>({
    queryKey: ['daily-usage', tenantId],
    queryFn: async () => {
      const { data } = await axios.get(`/v1/tenants/${tenantId}/usage/daily`)
      return data
    },
    refetchInterval: 30000, // Auto-refresh every 30 seconds
    staleTime: 20000,
  })
}
```

**Features:**
- Auto-refreshes every 30 seconds to show real-time usage
- Cached for 20 seconds to reduce API calls
- Returns: `{ current, limit, remaining, redis_available }`

### 2. Updated Analytics Tab

Added prominent daily usage card at the top of the Analytics tab with:

**Visual Features:**
- **Color-coded alerts:**
  - 🔵 **Blue** - Normal usage (>10 queries remaining)
  - 🟡 **Yellow** - Warning (≤10 queries remaining)
  - 🔴 **Red** - Limit reached (0 queries remaining)

- **Progress bar** showing usage percentage
- **Large percentage display** for quick overview
- **Descriptive text** with remaining queries or limit message

**Layout:**
```
┌─────────────────────────────────────────────────────┐
│ ⚡ Daily Usage: 45 / 50 queries          90%        │
│    5 queries remaining today              used      │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
└─────────────────────────────────────────────────────┘
```

## User Experience

### Normal Usage (Blue)
- Shows current/total queries
- Displays remaining queries
- Blue accent color
- Encourages continued use

### Warning State (Yellow)
- Appears when ≤10 queries remaining
- Yellow warning color
- Prompts user awareness

### Limit Reached (Red)
- Red alert color
- Message: "Daily limit reached. Resets at midnight UTC."
- Progress bar at 100%
- Clear call-to-action for upgrade (future)

## Screenshots

### Normal State (30/50 queries used)
```
┌─────────────────────────────────────────────────────┐
│ ⚡ Daily Usage: 30 / 50 queries          60%        │
│    20 queries remaining today             used      │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━░░░░░░░░░░░    │
└─────────────────────────────────────────────────────┘
```

### Warning State (48/50 queries used)
```
┌─────────────────────────────────────────────────────┐
│ ⚡ Daily Usage: 48 / 50 queries          96%        │
│    2 queries remaining today              used      │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
└─────────────────────────────────────────────────────┘
```

### Limit Reached (50/50 queries used)
```
┌─────────────────────────────────────────────────────┐
│ ⚡ Daily Usage: 50 / 50 queries          100%       │
│    Daily limit reached. Resets at midnight UTC.     │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
└─────────────────────────────────────────────────────┘
```

## Technical Details

### Data Flow
```
Frontend Component
    ↓
useDailyUsage Hook
    ↓
TanStack Query
    ↓
GET /v1/tenants/{tenant_id}/usage/daily
    ↓
DailyLimitService (Backend)
    ↓
Redis (daily_queries:{tenant_id}:{date})
    ↓
Returns { current, limit, remaining, redis_available }
```

### Auto-Refresh
- **Interval:** 30 seconds
- **Why:** Show near real-time usage without overwhelming the API
- **Stale time:** 20 seconds (data considered fresh for 20s)

### Performance
- Uses React Query caching
- Only fetches when tab is active
- Minimal re-renders with proper memoization
- Graceful handling if Redis unavailable

## Files Modified

1. **`frontend/src/hooks/useDailyUsage.ts`** (NEW)
   - React Query hook for fetching daily usage

2. **`frontend/src/components/dashboard/AnalyticsTab.tsx`**
   - Added `useDailyUsage` hook
   - Added daily usage card UI
   - Added color-coded states
   - Added progress bar visualization
   - Updated loading skeleton

## Future Enhancements

### 1. Upgrade Prompts
When limit is reached, show:
```
┌─────────────────────────────────────────────────────┐
│ ⚡ Daily limit reached!                              │
│                                                      │
│ Upgrade to Pro for 5,000 queries/day                │
│ [Upgrade to Pro $79/mo] [Learn More]                │
└─────────────────────────────────────────────────────┘
```

### 2. Usage History Chart
Add a small sparkline showing usage over the past 7 days:
```
Daily Usage Trend (Last 7 days)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▂▃▅▇█▇▅ 45 queries today
```

### 3. Predictive Warning
```
⚠️ At your current pace, you'll reach your daily limit by 6 PM
Consider upgrading to avoid interruptions
```

### 4. Notifications
- Browser notification when approaching limit (5 queries left)
- Email alert when limit reached
- Slack/Discord webhook integration

### 5. Usage Analytics
Add dedicated "Usage" section showing:
- Daily usage over time
- Peak usage hours
- Most active days
- Month-to-date totals

## Testing

### Manual Testing
1. Navigate to Analytics tab
2. Verify daily usage card displays correctly
3. Make queries and watch counter update (every 30s)
4. Test with different usage levels:
   - Low: 5/50 (should be blue)
   - Medium: 30/50 (should be blue)
   - High: 48/50 (should be yellow)
   - Maxed: 50/50 (should be red)

### Test Auto-Refresh
```bash
# Watch network tab in browser dev tools
# Should see request to /usage/daily every 30 seconds
```

### Test Redis Unavailable
```bash
# Stop Redis
docker stop weaver-redis-1

# Frontend should gracefully show:
# "Daily usage unavailable"
```

## Deployment

No special deployment steps needed:
1. Frontend will auto-update on next deploy
2. Backend endpoint already exists
3. Redis already tracking usage

Just rebuild frontend:
```bash
docker-compose up -d --build frontend
```

## Monitoring

### Check Usage Data
```bash
# Via API
curl http://localhost:8000/v1/tenants/{tenant_id}/usage/daily \
  -H "Authorization: Bearer YOUR_JWT"

# Via Redis
docker exec -it weaver-redis-1 redis-cli
KEYS daily_queries:*
GET daily_queries:{tenant_id}:2025-11-12
```

### Check Frontend Requests
```bash
# Watch API logs for /usage/daily requests
docker logs -f weaver-api-1 | grep "usage/daily"
```

## Summary

✅ **Added** real-time daily usage display to Analytics tab
✅ **Color-coded** visual indicators (blue/yellow/red)
✅ **Progress bar** showing usage percentage
✅ **Auto-refresh** every 30 seconds
✅ **Graceful** handling of errors
✅ **Mobile-responsive** design

**User Benefit:** Users can now see their daily query usage at a glance and manage their quota effectively.

**Business Benefit:** Clear visibility of limits creates natural upgrade opportunities when users approach their quota.

