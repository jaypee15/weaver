#!/bin/bash

set -e

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                              ║"
echo "║                        🚀 Starting Weaver Platform 🚀                       ║"
echo "║                                                                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⚠️  IMPORTANT: Please edit .env with your actual credentials:"
    echo "   - GOOGLE_API_KEY (required for Gemini)"
    echo "   - SUPABASE_URL and SUPABASE_KEY (required for OAuth)"
    echo "   - GCS_BUCKET_NAME and GCS_PROJECT_ID (required for storage)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    read -p "Press Enter to continue after editing .env, or Ctrl+C to exit..."
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

echo "🐳 Starting Docker Compose services..."
echo ""

# Build and start all services
docker-compose up --build -d

echo ""
echo "⏳ Waiting for services to be ready..."
echo ""

# Wait for API to be healthy
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API is ready!"
        break
    fi
    attempt=$((attempt + 1))
    echo "   Waiting for API... (attempt $attempt/$max_attempts)"
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ API failed to start. Check logs with: docker-compose logs api"
    exit 1
fi

# Wait for frontend
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Frontend is ready!"
        break
    fi
    attempt=$((attempt + 1))
    echo "   Waiting for Frontend... (attempt $attempt/$max_attempts)"
    sleep 2
done

echo ""
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                              ║"
echo "║                     ✅ Weaver is now running! ✅                             ║"
echo "║                                                                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📍 Access Points:"
echo "   • Dashboard:  http://localhost:3000"
echo "   • API:        http://localhost:8000"
echo "   • API Docs:   http://localhost:8000/docs"
echo "   • Metrics:    http://localhost:8000/metrics"
echo ""
echo "📊 Services Status:"
docker-compose ps
echo ""
echo "📝 Useful Commands:"
echo "   • View logs:        docker-compose logs -f"
echo "   • View API logs:    docker-compose logs -f api"
echo "   • View worker logs: docker-compose logs -f worker"
echo "   • Stop services:    docker-compose down"
echo "   • Restart:          docker-compose restart"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

