#!/bin/bash
set -e

echo "🔄 Starting Weaver Worker..."

# Worker tuning knobs (with sensible defaults)
CONCURRENCY=${WORKER_CONCURRENCY:-4}
MAX_TASKS_PER_CHILD=${WORKER_MAX_TASKS_PER_CHILD:-10}
SOFT_TIME_LIMIT=${WORKER_SOFT_TIME_LIMIT:-240}
TIME_LIMIT=${WORKER_TIME_LIMIT:-300}
WORKER_POOL=${WORKER_POOL:-prefork}

# Avoid libpq/asyncpg probing ~/.postgresql client cert/key paths
unset PGSSLKEY
unset PGSSLCERT
unset PGSSLROOTCERT
unset PGSYSCONFDIR
# Ensure it doesn't default to /root as HOME
export HOME=/tmp

# Start health check server in background (for Cloud Run)
echo "🏥 Starting health check server on port ${PORT:-8080}..."
python3 /app/health_server.py &
HEALTH_PID=$!

# Trap signals to ensure graceful shutdown
trap "echo '🛑 Shutting down...'; kill $HEALTH_PID 2>/dev/null; exit 0" SIGTERM SIGINT

echo "🔨 Starting Celery worker..."
exec celery -A app.workers.tasks worker \
  --loglevel=info \
  --pool="${WORKER_POOL}" \
  --concurrency="${CONCURRENCY}" \
  --uid=nobody --gid=nogroup \
  --max-tasks-per-child="${MAX_TASKS_PER_CHILD}" \
  --soft-time-limit="${SOFT_TIME_LIMIT}" \
  --time-limit="${TIME_LIMIT}" \
  --without-gossip --without-mingle --without-heartbeat


