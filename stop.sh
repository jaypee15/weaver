#!/bin/bash

echo "🛑 Stopping Weaver Platform..."
echo ""

docker-compose down

echo ""
echo "✅ All services stopped!"
echo ""
echo "To remove all data (including database):"
echo "  docker-compose down -v"

