# Interactive Storytelling Assistant for Kids 🌟

A magical storytelling chatbot designed specifically for children aged 6-9 years old. This interactive assistant creates engaging, safe, and educational story adventures where children can participate and guide the narrative.

## 🎯 Features

- **Age-Appropriate Content**: Specifically designed for 6-9 year olds with appropriate vocabulary and themes
- **Interactive Story Creation**: Children choose how their story begins and guide the adventure
- **Educational Focus**: Stories naturally teach valuable lessons about friendship, problem-solving, science, and more
- **Personalized Learning**: Each story adapts to the child's interests and choices
- **Safety Guardrails**: Automatic content filtering to ensure all interactions remain child-friendly
- **Smart Database**: Efficient conversation storage with session management
- **Web Interface**: Beautiful Gradio-based web UI for easy interaction
- **CLI Interface**: Command-line option for terminal-based storytelling
- **Modular Architecture**: Clean, organized codebase for easy maintenance

## 📁 Project Structure

```
chatbot_toy/
├── src/
│   └── storytelling/
│       ├── __init__.py       # Package initialization
│       ├── core.py           # Main graph implementation and workflow
│       ├── helper.py         # All prompts and messaging templates
│       ├── model.py          # Pydantic models for structured output
│       ├── schema.py         # Graph state definitions and constants
│       └── database.py       # Database handling with sessions
├── scripts/
│   └── setup.sh             # Setup and installation script
├── tests/                   # Test files (future)
├── docs/                    # Documentation (future)
├── data/                    # Data storage directory
├── venv/                    # Virtual environment
├── main.py                  # Main entry point
├── gradio_app.py           # Web interface using Gradio
├── requirements.txt        # Project dependencies
├── .env                    # Environment variables (OpenAI API key)
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation

#### Option 1: Automated Setup (Recommended)
```bash
# Clone or download the project
cd chatbot_toy

# Run the setup script
./scripts/setup.sh

# Activate the virtual environment
source venv/bin/activate
```

#### Option 2: Manual Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env  # Edit with your OpenAI API key
```

### Configuration

Create a `.env` file in the root directory:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### Running the Application

#### Web Interface (Recommended)
```bash
python main.py --web
# or simply
python main.py
```
Then open your browser to `http://localhost:7860`

#### Command Line Interface
```bash
python main.py --cli
```

#### Direct Access
```bash
# Web interface directly
python gradio_app.py

# CLI directly
python -m src.storytelling.core
```

## 🏗️ Architecture Overview

### Core Components

- **Graph Workflow**: Uses LangGraph for managing conversation flow
- **Safety System**: Multi-layer content filtering with strike system
- **Database Layer**: SQLite with session management and efficient storage
- **Prompt Engineering**: Detailed, age-appropriate prompts for engaging storytelling
- **Modular Design**: Separated concerns into dedicated modules

### Key Improvements

1. **Organized Structure**: Proper package organization with `src/` directory
2. **Enhanced Prompts**: Detailed, engaging prompts specifically for 6-9 year olds
3. **Smart Database**: Improved conversation storage with sessions and indexing
4. **Dual Interface**: Both web and command-line interfaces
5. **Better Safety**: Enhanced content filtering with detailed guidelines
6. **Easy Setup**: Automated installation and setup scripts

## 🎭 How It Works

1. **Story Choice**: Child chooses what type of story they want (nature, friendship, problem-solving, etc.)
2. **Interactive Beginning**: AI creates a personalized story opening based on the child's choice
3. **User Participation**: Child guides the story direction through their responses and choices
4. **Educational Integration**: Learning opportunities are naturally woven into the adventure
5. **Safety Check**: All input is automatically screened for appropriateness
6. **Story Generation**: AI creates the next part of the story with educational elements
7. **Database Storage**: All conversations are saved with session management

## 🛡️ Safety Features

- **Content Filtering**: Automatic detection of inappropriate themes
- **Positive Redirection**: Gentle guidance toward appropriate story elements
- **Strike System**: Automatic session termination after repeated inappropriate attempts
- **Age-Appropriate Language**: Vocabulary and themes suitable for 6-9 year olds

## 🎨 Story Themes

The assistant focuses on:
- Magical adventures with talking animals
- Friendship and kindness
- Problem-solving and creativity
- Nature exploration
- Learning through play
- Celebrating differences and uniqueness

## 📊 Database Schema

### Sessions Table
- `session_id`: Unique identifier for each story session
- `created_at`: Session start time
- `updated_at`: Last activity time
- `total_messages`: Number of messages in session
- `status`: Session status (active, completed, terminated, etc.)

### Messages Table
- `id`: Auto-incrementing message ID
- `session_id`: Reference to session
- `message_index`: Order of message in conversation
- `timestamp`: When message was created
- `role`: 'user' or 'ai'
- `content`: Message content

## 🔧 Configuration

Key constants can be modified in `src/storytelling/schema.py`:
- `STRIKE_LIMIT`: Number of unsafe attempts before termination (default: 3)
- `DB_FILE`: Database filename (default: "story_sessions.db")

## 🧪 Development

### Project Structure Philosophy
- `src/`: All source code organized in packages
- `scripts/`: Utility scripts for setup and maintenance
- `tests/`: Unit and integration tests (future)
- `docs/`: Documentation files (future)
- `data/`: Runtime data storage

### Adding New Features
1. Core logic goes in `src/storytelling/`
2. Use relative imports within the package
3. Update `main.py` for new entry points
4. Add tests in `tests/` directory

## 🤝 Contributing

This project is designed to be easily extensible. Key areas for enhancement:
- Additional story themes and characters
- More sophisticated safety filtering
- Enhanced UI features
- Multi-language support
- Voice interaction capabilities
- Unit and integration tests

## 📝 License

This project is designed for educational and entertainment purposes for children.

---

*Created with ❤️ for young storytellers everywhere!* 🌈✨