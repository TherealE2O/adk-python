# AI Novel Writing Editor

An AI-assisted text editor for novel writing built with Python and Google's Agent Development Kit (ADK). The application guides users through an interactive Q&A process to establish story facts, then uses this "Truth" to ground all AI-powered writing and editing features.

## Features

### ✨ NEW: Full AI Integration with Google Gemini

All AI features are now **fully implemented and working**:
- ✅ AI-powered text editing (improve, expand, rephrase)
- ✅ AI chapter planning and suggestions
- ✅ AI question generation for world-building
- ✅ AI entity extraction from answers
- ✅ **Universal audio input - record with mic or upload files EVERYWHERE** (NEW!)
- ✅ Context-grounded in your story's "Truth"

See [AI_FEATURES.md](AI_FEATURES.md), [UNIVERSAL_AUDIO.md](UNIVERSAL_AUDIO.md), [MICROPHONE_RECORDING.md](MICROPHONE_RECORDING.md), and [MINDMAP_FEATURES.md](MINDMAP_FEATURES.md) for complete documentation.

### Module 1: Project Manager & Story Inception
- **Project Management**: Create, open, and manage multiple novel projects
- **Interactive World-Building**: AI-powered Q&A to establish story foundations
- **Universal Audio Input**: 🎤 Use voice input **anywhere you can type** (powered by Gemini)
  - Project creation form
  - All Q&A questions
  - Chapter editor
  - Text selection for AI editing
- **Dynamic Question Tree**: Branching questions based on user answers
  - **Four view modes**: Mind Map (NEW!), Tree View, Category View, Timeline View
  - **Interactive Mind Map**: Visual graph with zoom, pan, and click navigation
  - Visual navigation of question structure
  - User-controlled navigation (jump between branches, go backwards)
  - Cross-branch analysis and automatic question generation
  - Persistent state tracking

### Module 2: AI-Assisted Text Editor
- **Chapter-Based Writing**: Organize your novel by chapters
- **Context-Grounded Editing**: AI actions (improve, expand, rephrase) grounded in:
  - "The Truth" (established plot, characters, settings)
  - Context from previous chapters
- **Generative Writing Assistance**: Auto-suggestions and paragraph generation
- **Chapter-Level Planning**: AI suggestions for next chapters and outlines

### Module 3: "The Truth" Knowledge Base Viewers
- **Character Sheets**: Automatically generated character profiles
- **Timeline Viewer**: Chronological view of plot events
- **Setting & World-Building Viewer**: Locations, magic systems, organizations
- **Global Search**: Find any fact across the entire knowledge base

## Tech Stack

- **Language**: Python 3.9+
- **AI Framework**: Google Agent Development Kit (ADK)
- **LLM**: Google Gemini (via google-genai)
- **UI**: Streamlit
- **Data Models**: Pydantic
- **Storage**: JSON-based file storage

## Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd ai-novel-editor
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Google AI API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

## Getting Your Google AI API Key (Required for AI Features)

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and paste it into your `.env` file

**Note**: The application works without an API key, but AI features (editing, suggestions, question generation) require it.

## Usage

1. **Start the application**:
   ```bash
   streamlit run app.py
   ```

2. **Create a new project**:
   - Enter project details (title, description, author, genre)
   - Click "Create Project"

3. **World-Building Q&A**:
   - Answer the initial question: "What is your story about?"
   - Navigate through the branching question tree
   - Answer questions in any order
   - Click "Start Writing" when ready

4. **Writing & Editing**:
   - Create chapters and write your novel
   - Use AI editing tools (improve, expand, rephrase)
   - View character sheets, timeline, and settings
   - AI maintains consistency with established "Truth"

## Project Structure

```
ai-novel-editor/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── pyproject.toml        # Project configuration
├── .env.example          # Environment variables template
├── README.md             # This file
├── src/
│   ├── agents/           # AI agents
│   │   ├── worldbuilding_agent.py
│   │   └── editing_agent.py
│   ├── models/           # Data models
│   │   ├── truth.py      # Truth knowledge base models
│   │   └── project.py    # Project and chapter models
│   ├── services/         # Business logic
│   │   ├── storage.py    # File storage service
│   │   └── project_manager.py
│   └── ui/               # UI components
├── data/
│   ├── projects/         # User projects (auto-created)
│   └── examples/         # Example projects
├── tests/                # Unit tests
└── config/               # Configuration files
```

## Key Concepts

### The Truth
The "Truth" is the established knowledge base for your story, including:
- **Characters**: Names, traits, backstories, relationships
- **Plot Events**: Timeline of story events
- **Settings**: Locations, world-building elements, magic systems

All AI operations are grounded in this Truth to maintain consistency.

### Question Tree
A branching structure of questions that:
- Adapts based on your answers
- Generates follow-up questions automatically
- Allows non-linear navigation
- Tracks answered vs. pending questions

### Grounded AI Editing
All AI editing operations consider:
1. The established Truth
2. Content from previous chapters
3. User's explicit instructions

This ensures consistency and prevents the AI from contradicting established facts.

## Development

### Running Tests
```bash
pytest tests/
```

### Code Style
The project follows Google Python Style Guide:
- 2-space indentation
- Maximum 80 character line length
- snake_case for functions and variables
- CamelCase for classes

## Limitations & Future Enhancements

### Current Limitations
- Voice AI is not yet fully implemented (text-based Q&A for now)
- AI editing features require Google Gemini API integration
- No collaborative editing support
- Limited export formats

### Planned Enhancements
- Full voice AI integration with speech recognition
- Real-time collaboration
- Export to various formats (PDF, EPUB, DOCX)
- Advanced visualization for question tree
- Memory/RAG integration for larger contexts
- Multi-agent orchestration for complex editing tasks

## Troubleshooting

### "GOOGLE_API_KEY not found"
- Ensure you've created a `.env` file from `.env.example`
- Add your Google AI API key to the `.env` file
- Restart the application

### "Module not found" errors
- Ensure you've activated your virtual environment
- Run `pip install -r requirements.txt` again

### Storage issues
- The `data/projects` directory is created automatically
- Ensure you have write permissions in the project directory

## License

This project is provided as-is for educational and development purposes.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues, questions, or suggestions, please open an issue on the project repository.

---

**Happy Writing! 📖✨**
