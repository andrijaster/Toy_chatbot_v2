#!/bin/bash
# Setup script for Interactive Storytelling Assistant

echo "🌟 Setting up Interactive Storytelling Assistant..."

# Check if Python 3.11 is installed
if ! command -v python3.11 &> /dev/null; then
    echo "❌ Python 3.11 is not installed. Please install Python 3.11 first."
    echo "   On Ubuntu/Debian: sudo apt install python3.11 python3.11-venv"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment with Python 3.11..."
    python3.11 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create data directory if it doesn't exist
mkdir -p data

echo "✅ Setup complete!"
echo ""
echo "🚀 To run the application:"
echo "   source venv/bin/activate"
echo "   python main.py --web    # For web interface"
echo "   python main.py --cli    # For command line"
echo ""
echo "🌟 Happy storytelling!"