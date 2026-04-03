#!/bin/bash

echo "🚀 Starting AI Smart Interview Agent in Development Mode..."

# Start backend
echo "🔧 Starting backend..."
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start frontend
echo "🌐 Starting frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ Services started!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📊 API Docs: http://localhost:8000/docs"

# Wait for user input to stop
echo "Press Ctrl+C to stop all services"
trap "kill $BACKEND_PID $FRONTEND_PID" INT
wait