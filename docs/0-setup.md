# Project Setup

## Quick Start

```bash
# 1. Clone and enter project
git clone <repo-url>
cd Toy_chatbot_v2

# 2. Run setup script
./scripts/setup.sh

# 3. Configure environment
cp .env_example .env
# Edit .env and add your OpenAI API key

# 4. Run application
source .venv/bin/activate  # or source venv/bin/activate
python main.py --web       # Web interface on localhost:7860
python main.py --cli       # Command line interface
```

## Requirements

- Python 3.12+
- OpenAI API key
- uv package manager (auto-installed by setup script)

## Manual Setup

### With uv (recommended)
```bash
uv venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt -e ".[dev]"
```

### With pip (fallback)
```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Development Workflow

```bash
# Start feature
git checkout development
git pull origin development
git checkout -b feature/your-feature

# Code with quality checks
ruff check . && ruff format . && mypy src/

# Commit and merge
git add .
git commit -m "feat: your change"
git push -u origin feature/your-feature
git checkout development
git merge feature/your-feature
```

## Docker Alternative

```bash
docker-compose up --build
```

## Troubleshooting

- **uv not found**: Script auto-installs, or visit [uv installation](https://docs.astral.sh/uv/getting-started/installation/)
- **Python 3.12 missing**: `sudo apt install python3.12 python3.12-venv` (Ubuntu/Debian)
- **OpenAI errors**: Check `.env` file has valid `OPENAI_API_KEY`