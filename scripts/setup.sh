#!/bin/bash

set -e

echo "🧩 Weaver Setup Script"
echo "======================"
echo ""

if [ ! -f backend/.env ]; then
    echo "📝 Creating backend/.env from template..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please edit backend/.env with your actual credentials"
fi

if [ ! -f frontend/.env.local ]; then
    echo "📝 Creating frontend/.env.local from template..."
    cp frontend/.env.example frontend/.env.local
    echo "⚠️  Please edit frontend/.env.local with your actual credentials"
fi

echo ""
echo "🐳 Starting Docker services..."
docker-compose up -d postgres redis

echo ""
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 5

echo ""
echo "📊 Running database migrations..."
docker-compose exec -T postgres psql -U weaver -d weaver < backend/app/db/models.sql

echo ""
echo "🐍 Installing Python dependencies..."
cd backend
pip install -r requirements.txt
cd ..

echo ""
echo "📦 Installing Node.js dependencies..."
cd frontend
npm install
cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the services:"
echo "  1. Backend API:  cd backend && uvicorn app.main:app --reload"
echo "  2. Celery Worker: celery -A worker.celery.celery_app worker --loglevel=info"
echo "  3. Frontend:     cd frontend && npm run dev"
echo ""
echo "Visit http://localhost:3000 to access the dashboard"

