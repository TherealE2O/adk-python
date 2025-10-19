# Quick Start: Audio Features

Get started with audio input in 3 simple steps!

## Step 1: Setup (1 minute)

1. **Get your Google AI API key**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Click "Create API Key"
   - Copy the key

2. **Add to .env file**
   ```bash
   cd ai-novel-editor
   cp .env.example .env
   # Edit .env and add your key:
   GOOGLE_API_KEY=your_actual_key_here
   ```

3. **Install dependencies** (if not already done)
   ```bash
   pip install -r requirements.txt
   ```

## Step 2: Run the App (30 seconds)

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Step 3: Use Audio Input (2 minutes)

### Create a Project
1. Click "Create New Project"
2. Enter a title (e.g., "My Fantasy Novel")
3. Click "Create Project"

### Answer with Audio
1. On the world-building page, select **"🎤 Audio Upload"** mode
2. Click "Choose an audio file"
3. Select your audio recording (MP3, WAV, etc.)
4. Wait 2-5 seconds for transcription
5. Review the transcript
6. Click "Start World Building"

### Continue with Follow-up Questions
1. Navigate the question tree (Tree View, Category, or Timeline)
2. Select a question to answer
3. Upload another audio file or switch to text mode
4. Submit your answer
5. Repeat!

## Recording Audio

### On Your Phone
1. Use Voice Memos (iPhone) or Voice Recorder (Android)
2. Record your answer (30 seconds to 5 minutes recommended)
3. Transfer to your computer or use cloud storage
4. Upload in the app

### On Your Computer
- **Windows**: Voice Recorder app
- **Mac**: QuickTime Player → File → New Audio Recording
- **Linux**: GNOME Sound Recorder or Audacity

### Tips for Best Results
- 🎤 Speak clearly at a normal pace
- 🔇 Use a quiet environment
- ⏱️ Keep recordings under 10 minutes for faster processing
- 📝 Describe your ideas naturally - Gemini understands context!

## Supported Audio Formats

✅ **WAV** - Best quality, larger files  
✅ **MP3** - Good quality, smaller files (recommended)  
✅ **AIFF** - Apple format  
✅ **AAC** - Modern compressed format  
✅ **OGG** - Open source format  
✅ **FLAC** - Lossless compression  

## Example Workflow

### Initial Story Description (2 minutes)
```
1. Record on your phone: "My story is about a young wizard 
   who discovers she has the power to control time..."
2. Upload the audio file
3. Gemini transcribes it
4. Click "Start World Building"
```

### Character Development (1 minute per question)
```
1. Question: "What is the main character's name and background?"
2. Record: "Her name is Elena, she's 16 years old, grew up 
   in a small village..."
3. Upload and submit
4. Gemini generates follow-up questions about Elena
```

### Plot Details (1 minute per question)
```
1. Question: "What is the central conflict?"
2. Record: "Elena must prevent a dark sorcerer from 
   destroying the timeline..."
3. Upload and submit
4. Continue building your story!
```

## Troubleshooting

### "Audio service not available"
**Fix**: Check that GOOGLE_API_KEY is set in your .env file

### "Failed to transcribe audio"
**Fix**: 
- Ensure file is in supported format (MP3, WAV, etc.)
- Check file size (should be under 20MB)
- Verify internet connection

### "No such file or directory"
**Fix**: Make sure you're in the `ai-novel-editor` directory

## What's Next?

After building your story with audio:

1. **View Your Truth**
   - Click "👥 View Characters" to see character sheets
   - Click "📅 View Timeline" to see plot events
   - Click "🗺️ View Settings" to see world-building

2. **Start Writing**
   - Click "🚀 Start Writing" when ready
   - Use the chapter editor
   - Apply AI editing tools (improve, expand, rephrase)

3. **Continue Building**
   - Return to world-building anytime
   - Add more details with audio or text
   - Refine your story's foundation

## Advanced Features

### Analyze Audio Content
```python
from src.services.audio_service import AudioService

audio_service = AudioService()

# Extract story elements
analysis = audio_service.analyze_audio(
    "story_idea.mp3",
    prompt="List all characters, plot points, and settings mentioned."
)
```

### Transcribe Specific Segments
```python
# Get transcript from 2:30 to 5:00
segment = audio_service.transcribe_with_timestamps(
    "long_recording.mp3",
    start_time="02:30",
    end_time="05:00"
)
```

## Need Help?

- 📖 Read [AUDIO_FEATURES.md](AUDIO_FEATURES.md) for detailed documentation
- 🐛 Check [GitHub Issues](https://github.com/google/adk-python/issues)
- 💬 Ask questions in discussions

## Summary

✅ **Setup**: Get API key, add to .env (1 minute)  
✅ **Run**: `streamlit run app.py` (30 seconds)  
✅ **Use**: Upload audio files, get transcripts (2 minutes)  

**Total time to get started: ~4 minutes!**

Happy writing! 📖✨
