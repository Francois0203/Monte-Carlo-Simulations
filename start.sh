#!/bin/bash

# Monte Carlo Simulations - Startup Script

echo "🎰 Starting Monte Carlo Simulations..."
echo ""

# Check if backend dependencies are installed
if [ ! -d "backend/env" ] && [ ! -d "backend/venv" ]; then
    echo "📦 Installing backend dependencies..."
    cd backend
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
fi

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

echo ""
echo "🚀 Starting backend server..."
cd backend
if [ -d "venv" ]; then
    source venv/bin/activate
else
    source env/bin/activate
fi
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

echo "⏳ Waiting for backend to start..."
sleep 3

echo "🚀 Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ All services started!"
echo ""
echo "📍 Access points:"
echo "   Frontend:  http://localhost:5173"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for Ctrl+C
trap "echo ''; echo '🛑 Shutting down...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
