#!/bin/bash

echo "🚀 Setting up AI Smart Interview Agent..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

# Backend Setup
echo "📦 Setting up backend..."
cd backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from app.database import init_db, seed_questions; init_db(); seed_questions()"

echo "✅ Backend setup complete!"

# Frontend Setup
echo "📦 Setting up frontend..."
cd ../frontend

# Install dependencies
npm install

echo "✅ Frontend setup complete!"

# Create uploads directory
mkdir -p ../backend/uploads/audio
mkdir -p ../backend/uploads/frames
mkdir -p ../backend/uploads/videos

echo "🎉 Setup complete! Run the following commands to start the application:"
echo "Backend: cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo "Frontend: cd frontend && npm run dev"