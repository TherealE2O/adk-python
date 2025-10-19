#!/bin/bash

# AI Novel Editor - Startup Script

echo "🚀 Starting AI Novel Editor..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
  echo "📦 Creating virtual environment..."
  python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
  echo "⚠️  No .env file found. Creating from template..."
  cp .env.example .env
  echo "⚠️  Please edit .env and add your GOOGLE_API_KEY before running again."
  exit 1
fi

# Create data directories
mkdir -p data/projects
mkdir -p data/examples

# Run the application
echo "✨ Launching AI Novel Editor..."
streamlit run app.py

