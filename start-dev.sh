#!/bin/bash
set -e

echo "🚀 Starting Weaver in DEVELOPMENT mode..."
echo "   - Backend: Hot-reload enabled (volume mounted)"
echo "   - Worker: Hot-reload enabled (volume mounted)"
echo "   - Frontend: Hot-reload enabled (Vite dev server)"
echo ""

# Start services with dev override
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

echo ""
echo "✅ Development environment started!"
echo "   - Frontend: http://localhost:3000"
echo "   - API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"

