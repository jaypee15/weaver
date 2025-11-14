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

echo "🔨 Starting Celery worker..."
exec celery -A worker.celery.celery_app worker --loglevel=info --concurrency=4 --uid=nobody --gid=nogroup


