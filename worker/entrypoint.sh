#!/bin/bash
set -e

echo "🔄 Starting Weaver Worker..."

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
  --concurrency=4 \
  --uid=nobody --gid=nogroup \
  --without-gossip --without-mingle --without-heartbeat


