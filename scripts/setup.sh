#!/bin/bash
# Setup script for Interactive Storytelling Assistant

echo "🌟 Setting up Interactive Storytelling Assistant..."

# Check if uv is installed, if not try to install it
if ! command -v uv &> /dev/null; then
    echo "📦 uv not found, attempting to install..."
    if command -v curl &> /dev/null; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$PATH"
    elif command -v pip &> /dev/null; then
        pip install uv
    else
        echo "❌ Cannot install uv. Please install uv manually:"
        echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
        echo "   Or visit: https://docs.astral.sh/uv/getting-started/installation/"
        exit 1
    fi
fi

# Check if uv is working
if ! command -v uv &> /dev/null; then
    echo "❌ uv installation failed. Falling back to pip setup..."
    
    # Fallback to pip setup
    if ! command -v python3.12 &> /dev/null; then
        echo "❌ Python 3.12 is not installed. Please install Python 3.12 first."
        echo "   On Ubuntu/Debian: sudo apt install python3.12 python3.12-venv"
        exit 1
    fi
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment with Python 3.12..."
        python3.12 -m venv venv
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
    
    VENV_PATH="venv"
    ACTIVATE_CMD="source venv/bin/activate"
else
    echo "✅ uv found, using uv for setup..."
    
    # Create virtual environment with uv
    if [ ! -d ".venv" ]; then
        echo "📦 Creating virtual environment with uv..."
        uv venv --python 3.12
    fi
    
    # Install dependencies with uv
    echo "📚 Installing dependencies with uv..."
    uv pip install -r requirements.txt
    
    VENV_PATH=".venv"
    ACTIVATE_CMD="source .venv/bin/activate"
fi

# Create data directory if it doesn't exist
mkdir -p data

echo "✅ Setup complete!"
echo ""
echo "🚀 To run the application:"
echo "   $ACTIVATE_CMD"
echo "   python main.py --web    # For web interface"
echo "   python main.py --cli    # For command line"
echo ""
echo "💡 Using uv for faster package management:"
echo "   uv add package_name     # Add new dependency"
echo "   uv pip install -r requirements.txt  # Install all deps"
echo ""
echo "🌟 Happy storytelling!"