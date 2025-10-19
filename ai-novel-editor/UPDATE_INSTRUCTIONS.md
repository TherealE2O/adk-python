# Update Instructions - Fix Audio Error

## Quick Fix (If You See the Error)

You're seeing this error:
```
AttributeError: 'list' object has no attribute 'lower'
```

This means you're running an older version of the app. Here's how to fix it:

### Option 1: Quick Patch (5 seconds)

Open `app.py` and find this line (around line 214):
```python
type=list(supported_formats.keys()).lower(),
```

Change it to:
```python
type=['wav', 'mp3', 'aiff', 'aac', 'ogg', 'flac'],
```

Save and restart the app.

### Option 2: Update to Latest Version (Recommended)

The latest version has **universal audio input** - you can use voice EVERYWHERE!

#### Step 1: Backup Your Data
```bash
# Backup your projects
cp -r data/projects data/projects.backup
```

#### Step 2: Update Files

**If using Git:**
```bash
git stash  # Save your local changes
git pull origin main  # Get latest version
git stash pop  # Restore your changes (if any)
```

**If not using Git:**
1. Download the latest `app.py` from the repository
2. Download `src/ui/audio_input.py` (new file)
3. Replace your old files

#### Step 3: Restart
```bash
streamlit run app.py
```

## What's New in Latest Version

### 🎤 Universal Audio Input

Every text field now has a 🎤 Audio button:

- **Project Creation**: Title, description, author, genre
- **World-Building**: All questions
- **Chapter Editor**: Title, content, text selection
- **Everywhere**: Any text input or text area

### How It Works

1. Click the 🎤 Audio button next to any text field
2. Upload your audio file
3. Gemini transcribes automatically
4. Transcript fills the field
5. Edit if needed and submit

### No More Mode Switching

- ❌ Old: Switch between "Text" and "Audio Upload" modes
- ✅ New: Audio button available on every field

## Verification

After updating, you should see:

1. ✅ No more "Input Mode" selector
2. ✅ 🎤 Audio buttons next to all text fields
3. ✅ Message: "🎤 Audio input available - Click the 🎤 Audio button next to any text field"
4. ✅ No errors when uploading audio

## Troubleshooting

### Still seeing the error?

1. Make sure you saved the file
2. Restart Streamlit (Ctrl+C, then `streamlit run app.py`)
3. Clear browser cache (Ctrl+Shift+R)
4. Check you're editing the right `app.py` file

### Audio button not showing?

1. Check that `GOOGLE_API_KEY` is set in `.env`
2. Verify `src/ui/audio_input.py` exists
3. Check the import at the top of `app.py`:
   ```python
   from src.ui.audio_input import universal_text_input
   ```

### Need the old version?

If you need to revert:
```bash
git checkout HEAD~1 app.py  # Go back one version
```

## Benefits of Updating

### Before (Old Version)
- ❌ Audio only in Q&A
- ❌ Mode switching required
- ❌ Bug with file types
- ❌ Limited audio support

### After (New Version)
- ✅ Audio everywhere
- ✅ No mode switching
- ✅ Bug fixed
- ✅ Universal audio support
- ✅ Better UX
- ✅ Context-aware transcription

## Files Changed

If you want to manually update, these files changed:

1. **app.py** - Main application
   - Removed audio mode selector
   - Added universal_text_input everywhere
   - Fixed file uploader bug

2. **src/ui/audio_input.py** - NEW FILE
   - Universal audio input component
   - Handles all audio transcription
   - Context-aware prompts

3. **README.md** - Updated documentation
4. **UNIVERSAL_AUDIO.md** - NEW: Complete audio guide

## Support

If you need help:

1. Read [UNIVERSAL_AUDIO.md](UNIVERSAL_AUDIO.md) for full documentation
2. Check [FIX_AUDIO_ERROR.md](FIX_AUDIO_ERROR.md) for detailed fix steps
3. Run `python test_universal_audio.py` to verify setup

## Summary

**Quick Fix**: Change line 214 to use `type=['wav', 'mp3', ...]`

**Better Fix**: Update to latest version for universal audio input everywhere!

🎤 Happy writing! 📖✨
