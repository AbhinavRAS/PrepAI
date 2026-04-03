#!/bin/bash

echo "🚀 Deploying AI Smart Interview Agent to Production..."

# Build and start containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Deployment successful!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:8000"
    echo "📊 API Docs: http://localhost:8000/docs"
else
    echo "❌ Deployment failed. Check logs with: docker-compose logs"
    exit 1
fi

# Initialize database
echo "🗄️ Initializing database..."
docker-compose exec backend python -c "from app.database import init_db, seed_questions; init_db(); seed_questions()"

echo "🎉 Deployment complete!"