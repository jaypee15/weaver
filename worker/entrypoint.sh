#!/bin/bash
set -e

echo "🔄 Starting Weaver Worker..."

echo "⏳ Waiting for Redis to be ready..."
while ! redis-cli -h "${REDIS_HOST:-redis}" -p "${REDIS_PORT:-6379}" ping > /dev/null 2>&1; do
    echo "Waiting for Redis..."
    sleep 2
done

echo "✅ Redis is ready!"

echo "🔨 Starting Celery worker..."
exec celery -A worker.celery.celery_app worker --loglevel=info --concurrency=4


