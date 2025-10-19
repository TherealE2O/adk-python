# Requirements Guide - AI Novel Editor

## Overview

This document explains the dependency structure and installation options for the AI Novel Editor.

## File Structure

```
ai-novel-editor/
├── requirements.txt          # Core dependencies (minimal installation)
├── requirements-dev.txt      # Development dependencies (full installation)
├── pyproject.toml           # Project metadata and optional dependencies
└── .env.example             # Environment configuration template
```

## Core Dependencies (requirements.txt)

### What's Included

The `requirements.txt` file contains only the **essential dependencies** needed to run the application:

```
pydantic>=2.0.0,<3.0.0       # Data validation and settings
python-dotenv>=1.0.0         # Environment variable management
streamlit>=1.30.0,<2.0.0     # Web UI framework
pytest>=7.0.0,<8.0.0         # Testing framework
```

### What Works with Core Dependencies

✅ **Fully Functional:**
- Project creation and management
- Chapter creation and editing
- Manual Truth knowledge base entry
- Character, plot, and setting management
- Timeline and setting viewers
- Global search functionality
- All UI features
- File storage and persistence

❌ **Not Available:**
- AI-powered editing (improve, expand, rephrase)
- Automatic question generation
- AI suggestions and planning
- Voice AI features

### Installation

```bash
pip install -r requirements.txt
```

**Use this when:**
- You want minimal dependencies
- You don't need AI features yet
- You're testing the application structure
- You have limited bandwidth/storage

## Development Dependencies (requirements-dev.txt)

### What's Included

The `requirements-dev.txt` file includes everything from `requirements.txt` plus:

```
# Development & Testing Tools
pytest>=7.0.0,<8.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
black>=23.0.0
isort>=5.12.0
flake8>=6.0.0
mypy>=1.0.0
pylint>=2.17.0

# Google AI Integration
google-genai>=0.3.0
```

### What Works with Development Dependencies

✅ **Everything from core dependencies plus:**
- AI-powered editing features
- Automatic question generation
- AI suggestions and planning
- Code formatting and linting
- Type checking
- Test coverage reporting

### Installation

```bash
pip install -r requirements-dev.txt
```

**Use this when:**
- You want full AI functionality
- You're developing or contributing
- You need code quality tools
- You want the complete experience

## Optional Dependencies (pyproject.toml)

The `pyproject.toml` file defines optional dependency groups that can be installed as needed:

### Available Groups

#### 1. AI Features
```bash
pip install -e ".[ai]"
```
Includes: `google-genai`, `google-generativeai`

#### 2. Voice AI
```bash
pip install -e ".[voice]"
```
Includes: `pyaudio`, `speechrecognition`, `pyttsx3`

#### 3. Database Backend
```bash
pip install -e ".[database]"
```
Includes: `sqlalchemy`, `aiosqlite`

#### 4. Advanced Visualization
```bash
pip install -e ".[viz]"
```
Includes: `streamlit-agraph`, `plotly`, `networkx`

#### 5. Export Features
```bash
pip install -e ".[export]"
```
Includes: `reportlab`, `python-docx`, `ebooklib`

#### 6. All Optional Features
```bash
pip install -e ".[all]"
```
Includes everything above

## Dependency Rationale

### Why These Core Dependencies?

#### Pydantic (Required)
- **Purpose**: Data validation and settings management
- **Why**: Ensures data integrity for Truth knowledge base
- **Used in**: All data models (Character, PlotEvent, Setting, Project, Chapter)
- **Size**: ~2 MB
- **Alternatives**: dataclasses (no validation), attrs (less features)

#### Python-dotenv (Required)
- **Purpose**: Environment variable management
- **Why**: Secure API key storage
- **Used in**: app.py for loading GOOGLE_API_KEY
- **Size**: <100 KB
- **Alternatives**: Manual os.environ (less convenient)

#### Streamlit (Required)
- **Purpose**: Web UI framework
- **Why**: Rapid development, Python-native, interactive
- **Used in**: app.py for entire UI
- **Size**: ~50 MB
- **Alternatives**: Flask+HTML (more code), Gradio (less flexible)

#### Pytest (Required for testing)
- **Purpose**: Testing framework
- **Why**: Industry standard, easy to use
- **Used in**: tests/ directory
- **Size**: ~1 MB
- **Alternatives**: unittest (less features), nose (deprecated)

### Why Google-genai is Optional?

The `google-genai` package is **optional** because:

1. **Application works without it**: Core functionality (project management, manual editing) doesn't require AI
2. **Large dependency**: Adds ~100+ MB of dependencies
3. **Requires API key**: Not everyone has immediate access
4. **Development flexibility**: Developers can test structure without AI
5. **Gradual adoption**: Users can start simple, add AI later

## Version Constraints Explained

### Semantic Versioning

We use semantic versioning constraints:

```
pydantic>=2.0.0,<3.0.0
```

- `>=2.0.0`: Minimum version (features we need)
- `<3.0.0`: Maximum version (avoid breaking changes)

### Why Version Constraints?

1. **Stability**: Prevent breaking changes from major updates
2. **Security**: Allow patch updates (bug fixes, security)
3. **Compatibility**: Ensure dependencies work together
4. **Reproducibility**: Same versions = same behavior

## Installation Scenarios

### Scenario 1: Quick Test

**Goal**: Test the application quickly

```bash
pip install pydantic python-dotenv streamlit
streamlit run app.py
```

**Result**: Basic functionality, no AI features

### Scenario 2: Full Local Use

**Goal**: Use all features locally

```bash
pip install -r requirements-dev.txt
# Add GOOGLE_API_KEY to .env
streamlit run app.py
```

**Result**: Complete functionality including AI

### Scenario 3: Production Deployment

**Goal**: Deploy to production server

```bash
# Use pinned versions for reproducibility
pip install pydantic==2.5.0 python-dotenv==1.0.0 streamlit==1.30.0
pip install google-genai==0.3.0
```

**Result**: Stable, reproducible deployment

### Scenario 4: Development

**Goal**: Contribute to the project

```bash
pip install -r requirements-dev.txt
pip install pre-commit black isort mypy flake8
```

**Result**: Full development environment

## Dependency Tree

```
ai-novel-editor
├── pydantic (required)
│   ├── typing-extensions
│   └── annotated-types
├── python-dotenv (required)
├── streamlit (required)
│   ├── altair
│   ├── pandas
│   ├── pillow
│   ├── tornado
│   └── [many others]
├── pytest (dev)
│   ├── pluggy
│   └── iniconfig
└── google-genai (optional)
    ├── google-auth
    ├── protobuf
    └── [many others]
```

## Troubleshooting Dependencies

### Issue: "ModuleNotFoundError"

**Solution**: Install missing dependency
```bash
pip install <missing-module>
```

### Issue: "Version conflict"

**Solution**: Use virtual environment
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "Slow installation"

**Solution**: Use pip cache
```bash
pip install --cache-dir ~/.cache/pip -r requirements.txt
```

### Issue: "Permission denied"

**Solution**: Use user installation
```bash
pip install --user -r requirements.txt
```

## Updating Dependencies

### Check for Updates

```bash
pip list --outdated
```

### Update Specific Package

```bash
pip install --upgrade pydantic
```

### Update All Packages

```bash
pip install --upgrade -r requirements.txt
```

### Freeze Current Versions

```bash
pip freeze > requirements-lock.txt
```

## Best Practices

### 1. Use Virtual Environments

Always use a virtual environment to isolate dependencies:

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### 2. Pin Versions for Production

For production, use exact versions:

```bash
pip freeze > requirements-prod.txt
```

### 3. Regular Updates

Update dependencies regularly for security:

```bash
pip install --upgrade -r requirements.txt
```

### 4. Test After Updates

Always test after updating dependencies:

```bash
pytest tests/ -v
```

## FAQ

### Q: Why not include google-genai in requirements.txt?

**A**: To keep the core installation minimal and allow users to choose when to add AI features.

### Q: Can I use a different LLM provider?

**A**: Yes! The architecture supports it. You'd need to:
1. Install the provider's SDK
2. Modify the agent classes to use the new provider
3. Update environment configuration

### Q: Do I need all the optional dependencies?

**A**: No. Install only what you need:
- Basic use: Just `requirements.txt`
- AI features: Add `google-genai`
- Development: Use `requirements-dev.txt`

### Q: How do I contribute without AI features?

**A**: You can develop and test the core functionality (models, services, UI) without AI. Just use `requirements.txt`.

### Q: What if I want to use Anthropic Claude instead of Gemini?

**A**: Install `anthropic` package and modify the agent classes to use Claude's API. The architecture is model-agnostic.

## Summary

| File | Purpose | When to Use |
|------|---------|-------------|
| `requirements.txt` | Core dependencies | Basic installation, testing structure |
| `requirements-dev.txt` | Full dependencies | Development, full functionality |
| `pyproject.toml` | Project metadata | Package installation, optional features |
| `.env.example` | Configuration template | Environment setup |

**Recommendation**: Start with `requirements.txt`, add `google-genai` when ready for AI features.

---

**Need help?** See [INSTALL.md](INSTALL.md) for detailed installation instructions.
