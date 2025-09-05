#!/bin/bash

# TestSpecAI Development Setup Script for Linux/Mac
# This script sets up the development environment for TestSpecAI

echo "🚀 Setting up TestSpecAI Development Environment..."

# Check if Python is installed
echo "📋 Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo "✅ Python found: $PYTHON_VERSION"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1)
    echo "✅ Python found: $PYTHON_VERSION"
    PYTHON_CMD="python"
else
    echo "❌ Python not found. Please install Python 3.11+ from https://python.org"
    exit 1
fi

# Check if Node.js is installed
echo "📋 Checking Node.js installation..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version 2>&1)
    echo "✅ Node.js found: $NODE_VERSION"
else
    echo "❌ Node.js not found. Please install Node.js 18+ from https://nodejs.org"
    exit 1
fi

# Setup Backend
echo "🐍 Setting up Backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    $PYTHON_CMD -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp env.example .env
fi

cd ..

# Setup Frontend
echo "⚛️ Setting up Frontend..."
cd frontend

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp env.example .env
fi

cd ..

echo "🎉 Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Start the backend server: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "2. Start the frontend server: cd frontend && npm run dev"
echo "3. Open http://localhost:3000 in your browser"
