# Installation Guide - AI Novel Editor

## Prerequisites

- **Python**: 3.9 or higher
- **pip**: Latest version recommended
- **Git**: For cloning the repository (optional)

## Quick Installation

### Option 1: Using the Startup Script (Recommended)

The easiest way to get started:

```bash
cd ai-novel-editor
./run.sh
```

The script will:
1. Create a virtual environment
2. Install all required dependencies
3. Check for `.env` file
4. Launch the application

### Option 2: Manual Installation

For more control over the installation process:

```bash
# 1. Navigate to the project directory
cd ai-novel-editor

# 2. Create a virtual environment
python3 -m venv venv

# 3. Activate the virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 4. Upgrade pip
pip install --upgrade pip

# 5. Install dependencies
pip install -r requirements.txt

# 6. Set up environment variables
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY (see below)

# 7. Run the application
streamlit run app.py
```

## Installation Options

### Basic Installation (Minimal)

For basic functionality without AI features:

```bash
pip install -r requirements.txt
```

**Includes:**
- Pydantic (data validation)
- Python-dotenv (environment management)
- Streamlit (web UI)
- Pytest (testing)

**What works:**
- Project management
- Chapter creation and editing
- Truth knowledge base (manual entry)
- All UI features

**What doesn't work:**
- AI-powered editing (improve, expand, rephrase)
- Automatic question generation
- AI suggestions

### Full Installation (Recommended)

For complete functionality including AI features:

```bash
pip install -r requirements-dev.txt
```

**Includes everything from basic installation plus:**
- Google Gemini API client
- Development tools (pytest, black, mypy)
- Code quality tools

**What works:**
- Everything from basic installation
- AI-powered editing
- Automatic question generation
- AI suggestions and planning

### Custom Installation

Install only what you need:

```bash
# Basic installation
pip install -r requirements.txt

# Add Google AI support
pip install google-genai>=0.3.0

# Add development tools
pip install pytest pytest-cov black isort mypy

# Add visualization tools (future feature)
pip install streamlit-agraph plotly networkx
```

## Environment Configuration

### 1. Create .env File

```bash
cp .env.example .env
```

### 2. Get Google AI API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key

### 3. Configure .env

Edit `.env` and add your API key:

```bash
# Required for AI features
GOOGLE_API_KEY=your_api_key_here

# Optional: Specify model (default: gemini-2.0-flash-exp)
GEMINI_MODEL=gemini-2.0-flash-exp
```

## Verification

### Test Installation

Run the test suite to verify everything is working:

```bash
# Activate virtual environment first
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run tests
pytest tests/ -v
```

Expected output:
```
✅ test_character_creation PASSED
✅ test_plot_event_creation PASSED
✅ test_setting_creation PASSED
✅ test_question_node PASSED
✅ test_question_tree PASSED
✅ test_truth_knowledge_base PASSED
✅ test_chapter PASSED
✅ test_project PASSED
```

### Test Application Launch

```bash
streamlit run app.py
```

The application should open in your browser at `http://localhost:8501`

## Troubleshooting

### Common Issues

#### 1. "python3: command not found"

**Solution**: Install Python 3.9 or higher
- **Ubuntu/Debian**: `sudo apt-get install python3.9`
- **macOS**: `brew install python@3.9`
- **Windows**: Download from [python.org](https://www.python.org/downloads/)

#### 2. "pip: command not found"

**Solution**: Install pip
```bash
python3 -m ensurepip --upgrade
```

#### 3. "ModuleNotFoundError: No module named 'pydantic'"

**Solution**: Ensure virtual environment is activated and dependencies are installed
```bash
source venv/bin/activate
pip install -r requirements.txt
```

#### 4. "GOOGLE_API_KEY not found"

**Solution**: 
1. Ensure `.env` file exists in the project root
2. Add your API key: `GOOGLE_API_KEY=your_key_here`
3. Restart the application

#### 5. "Permission denied: ./run.sh"

**Solution**: Make the script executable
```bash
chmod +x run.sh
```

#### 6. Virtual environment activation fails on Windows

**Solution**: Use PowerShell or enable script execution
```powershell
# PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\Activate.ps1
```

### Platform-Specific Notes

#### Linux

```bash
# Install system dependencies (if needed)
sudo apt-get update
sudo apt-get install python3.9 python3.9-venv python3-pip

# Continue with standard installation
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### macOS

```bash
# Install Python via Homebrew (if needed)
brew install python@3.9

# Continue with standard installation
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Windows

```powershell
# Using PowerShell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Upgrading

### Update Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Update all packages
pip install --upgrade -r requirements.txt

# Or update specific package
pip install --upgrade streamlit
```

### Update Application

```bash
# If using git
git pull origin main

# Reinstall dependencies (in case requirements changed)
pip install -r requirements.txt
```

## Uninstallation

### Remove Virtual Environment

```bash
# Deactivate if active
deactivate

# Remove virtual environment directory
rm -rf venv
```

### Remove Application

```bash
# Remove entire project directory
cd ..
rm -rf ai-novel-editor
```

## Docker Installation (Alternative)

For containerized deployment:

```dockerfile
# Dockerfile (create this file)
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

Build and run:

```bash
docker build -t ai-novel-editor .
docker run -p 8501:8501 -v $(pwd)/data:/app/data ai-novel-editor
```

## Development Setup

For contributing or development:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks (optional)
pip install pre-commit
pre-commit install

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html

# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/
pylint src/
```

## Next Steps

After successful installation:

1. Read [QUICKSTART.md](QUICKSTART.md) for a 5-minute tutorial
2. Check [README.md](README.md) for feature documentation
3. Review [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
4. Start creating your first novel project!

## Getting Help

If you encounter issues:

1. Check this installation guide
2. Review the [Troubleshooting](#troubleshooting) section
3. Ensure all prerequisites are met
4. Check Python and pip versions
5. Verify virtual environment is activated
6. Review error messages carefully

## System Requirements

### Minimum Requirements
- **CPU**: 1 GHz or faster
- **RAM**: 2 GB
- **Disk**: 500 MB free space
- **OS**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: 3.9+

### Recommended Requirements
- **CPU**: 2 GHz dual-core or better
- **RAM**: 4 GB or more
- **Disk**: 1 GB free space
- **Internet**: For AI features (Google Gemini API)

---

**Installation complete? Start writing your novel!** 📖✨

See [QUICKSTART.md](QUICKSTART.md) for your first steps.
