# Quick Start Guide - AI Novel Editor

Get up and running with the AI Novel Editor in 5 minutes!

## Prerequisites

- Python 3.9 or higher
- Google AI API Key ([Get one here](https://makersuite.google.com/app/apikey))

## Installation

### Option 1: Using the startup script (Recommended)

```bash
cd ai-novel-editor
./run.sh
```

The script will:
- Create a virtual environment
- Install dependencies
- Check for .env file
- Launch the application

### Option 2: Manual setup

```bash
# Navigate to project directory
cd ai-novel-editor

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Run the application
streamlit run app.py
```

## First Steps

### 1. Create Your First Project

1. Launch the application
2. On the Project Manager screen, fill in:
   - **Project Title**: "My First Novel"
   - **Description**: Brief description of your story
   - **Author**: Your name
   - **Genre**: e.g., "Fantasy", "Sci-Fi", "Mystery"
3. Click "Create Project"

### 2. World-Building Q&A

1. Answer the initial question: "What is your story about?"
   - Example: "A young wizard discovers they're the chosen one destined to defeat an ancient evil"

2. The AI will generate follow-up questions based on your answer
   - Questions about characters
   - Questions about plot events
   - Questions about settings

3. Navigate the question tree:
   - Select any pending question from the dropdown
   - Answer in as much or as little detail as you want
   - Jump between different branches anytime
   - Click "Start Writing" when ready

### 3. Start Writing

1. Click "Start Writing" to enter the editor
2. Add your first chapter:
   - Enter a chapter title in the sidebar
   - Click "Add Chapter"
3. Write your content in the text area
4. Click "Save Chapter" to save your work

### 4. Use AI Editing Tools

1. Write or select some text
2. Use the AI tools:
   - **Improve**: Enhance prose quality
   - **Expand**: Add more detail
   - **Rephrase**: Alternative phrasing

All AI edits are grounded in your established "Truth" and previous chapters!

### 5. View Your Truth

Click the sidebar buttons to view:
- **👥 View Characters**: See all character sheets
- **📅 View Timeline**: Chronological plot events
- **🗺️ View Settings**: Locations and world-building

## Example Workflow

```
1. Create Project: "The Last Mage"
   ↓
2. Answer: "A story about the last mage in a world where magic is dying"
   ↓
3. AI Generates Questions:
   - "What is the main character's name and background?"
   - "What caused magic to start dying?"
   - "Where does the story take place?"
   ↓
4. Answer Questions (in any order)
   ↓
5. Truth is Built:
   - Character: Elara, last mage, age 25
   - Plot: Magic fading due to ancient curse
   - Setting: Kingdom of Aethel
   ↓
6. Start Writing Chapter 1
   ↓
7. Use AI to improve/expand text
   (AI maintains consistency with Truth)
```

## Tips for Best Results

### World-Building Phase
- **Be specific**: More detail = better AI understanding
- **Answer naturally**: Write as if explaining to a friend
- **Don't worry about perfection**: You can always add more later
- **Jump around**: Answer questions in whatever order makes sense

### Writing Phase
- **Save frequently**: Click "Save Chapter" often
- **Use AI sparingly**: Let it assist, not write for you
- **Review AI suggestions**: Always review before accepting
- **Build incrementally**: Write in small chunks, then expand

### Truth Management
- **Review regularly**: Check character sheets and timeline
- **Stay consistent**: The AI will help, but you're in control
- **Update as needed**: Truth can evolve as your story develops

## Keyboard Shortcuts

- **Ctrl/Cmd + S**: Save chapter (when in text area)
- **Ctrl/Cmd + Enter**: Submit forms

## Troubleshooting

### "GOOGLE_API_KEY not found"
- Make sure you created `.env` from `.env.example`
- Add your API key: `GOOGLE_API_KEY=your_key_here`
- Restart the application

### Application won't start
- Check Python version: `python --version` (need 3.9+)
- Reinstall dependencies: `pip install -r requirements.txt`
- Check for error messages in terminal

### Changes not saving
- Click "Save Chapter" button
- Check file permissions in `data/projects` directory
- Ensure you have disk space available

### AI features not working
- Verify API key is correct
- Check internet connection
- Ensure you have API quota remaining

## Next Steps

- Read the full [README.md](README.md) for detailed features
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- Explore example projects (if available)
- Join the community for tips and support

## Getting Help

- Check the documentation files
- Review error messages carefully
- Ensure all prerequisites are met
- Try the example workflow above

---

**Happy Writing! 📖✨**

Start creating your masterpiece today!
