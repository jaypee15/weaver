#!/bin/bash
set -e

echo "🚀 Starting Weaver Backend..."

if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "📊 Running database migrations with Alembic..."
    alembic upgrade head
    
    if [ $? -eq 0 ]; then
        echo "✅ Migrations applied successfully"
    else
        echo "❌ Migration failed!"
        exit 1
    fi
    
    echo "✅ Migrations complete!"
fi

echo "🌐 Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000

