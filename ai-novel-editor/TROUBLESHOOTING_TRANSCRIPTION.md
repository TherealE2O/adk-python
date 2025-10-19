# Troubleshooting: "Failed to transcribe" Error

## Common Causes & Solutions

### 1. API Key Issues

**Problem**: GOOGLE_API_KEY not set or invalid

**Check**:
```bash
# In your .env file
cat .env | grep GOOGLE_API_KEY
```

**Solutions**:
1. Verify API key is set in `.env` file
2. Check key is valid at [Google AI Studio](https://makersuite.google.com/app/apikey)
3. Ensure no extra spaces or quotes around the key
4. Restart the app after setting the key

**Correct format in .env**:
```
GOOGLE_API_KEY=AIzaSyD...your_actual_key_here
```

**NOT**:
```
GOOGLE_API_KEY="AIzaSyD..."  # Remove quotes
GOOGLE_API_KEY = AIzaSyD...  # Remove spaces around =
```

---

### 2. Audio Format Issues

**Problem**: Audio format not compatible

**Solutions**:

**For Recording**:
- Browser should record in WAV automatically
- If fails, try uploading a file instead
- Check browser console for errors (F12)

**For Upload**:
- Use supported formats: WAV, MP3, AIFF, AAC, OGG, FLAC
- Avoid: WMA, M4A, or other formats
- Convert if needed using online tools

---

### 3. File Size Issues

**Problem**: Audio file too large

**Check**:
- Files over 20 MB may fail for inline upload
- Very long recordings (>10 min) may timeout

**Solutions**:
1. Keep recordings under 5 minutes
2. Break long content into chunks
3. Compress audio files before upload
4. Use MP3 format for smaller size

---

### 4. Network Issues

**Problem**: Internet connection problems

**Check**:
```bash
# Test internet connection
ping google.com

# Test API access
curl -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"test"}]}]}' \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=YOUR_API_KEY"
```

**Solutions**:
1. Check internet connection is stable
2. Try again in a few seconds
3. Check if firewall is blocking API calls
4. Verify no VPN issues

---

### 5. Audio Quality Issues

**Problem**: Audio is corrupted or unreadable

**Solutions**:

**For Recording**:
1. Check microphone is working
2. Test in another app first
3. Grant browser microphone permission
4. Try different browser

**For Upload**:
1. Play audio file to verify it works
2. Re-record if corrupted
3. Try different audio file
4. Convert to WAV or MP3

---

### 6. Temporary File Issues

**Problem**: Can't save or process temporary files

**Check**:
```bash
# Check temp directory exists and is writable
ls -la /tmp
```

**Solutions**:
1. Ensure app has write permissions
2. Check disk space is available
3. Restart the app
4. Clear temp files manually

---

### 7. API Rate Limits

**Problem**: Too many requests to Gemini API

**Symptoms**:
- Works sometimes, fails other times
- Error after multiple transcriptions

**Solutions**:
1. Wait a few seconds between requests
2. Check API quota at Google AI Studio
3. Upgrade API plan if needed
4. Reduce transcription frequency

---

## Quick Diagnostic Steps

### Step 1: Verify API Key
```bash
cd ai-novel-editor
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
key = os.getenv('GOOGLE_API_KEY')
if key:
    print(f'✅ API key found: {key[:10]}...')
else:
    print('❌ API key not found')
"
```

### Step 2: Test Audio Service
```bash
python test_audio.py
```

### Step 3: Test with Simple Audio
1. Record a 5-second test: "This is a test"
2. Try to transcribe
3. If fails, try uploading a known-good audio file

### Step 4: Check Logs
Look at terminal output for detailed error messages:
```
Error transcribing audio: [detailed error here]
```

---

## Specific Error Messages

### "Failed to save audio file"

**Cause**: Can't write to disk

**Fix**:
```bash
# Create audio directory
mkdir -p data/audio
chmod 777 data/audio
```

### "Could not request results from speech recognition service"

**Cause**: Network or API issue

**Fix**:
1. Check internet connection
2. Verify API key is valid
3. Try again in a few seconds

### "Error: 'NoneType' object has no attribute..."

**Cause**: Audio service not initialized

**Fix**:
1. Restart the app
2. Check GOOGLE_API_KEY is set
3. Verify imports are correct

---

## Testing Checklist

Run through this checklist:

- [ ] GOOGLE_API_KEY is set in .env
- [ ] API key is valid (test at Google AI Studio)
- [ ] Internet connection is working
- [ ] Audio file is in supported format
- [ ] Audio file is under 20 MB
- [ ] Microphone permission granted (for recording)
- [ ] Browser is up to date
- [ ] App has been restarted recently
- [ ] Disk space is available
- [ ] No firewall blocking API calls

---

## Alternative Solutions

### If Recording Fails

**Use Upload Instead**:
1. Record on your phone or computer
2. Transfer file to computer
3. Use Upload tab instead of Record tab

### If Upload Fails

**Try Recording Instead**:
1. Use Record tab
2. Speak directly into microphone
3. Keep recording short (under 2 min)

### If Both Fail

**Use Text Input**:
1. Type your content manually
2. Or use external transcription service
3. Copy/paste the transcript

---

## Debug Mode

### Enable Detailed Logging

Add to your code temporarily:

```python
# In src/services/audio_service.py
def transcribe_audio_file(self, file_path, prompt):
    print(f"DEBUG: Transcribing file: {file_path}")
    print(f"DEBUG: File exists: {os.path.exists(file_path)}")
    print(f"DEBUG: File size: {os.path.getsize(file_path)} bytes")
    print(f"DEBUG: API key set: {bool(self.api_key)}")
    
    try:
        # ... existing code ...
    except Exception as e:
        print(f"DEBUG: Full error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
```

### Check Browser Console

1. Press F12 to open developer tools
2. Go to Console tab
3. Look for errors when recording
4. Check Network tab for API calls

---

## Getting Help

### Information to Provide

When asking for help, include:

1. **Error message**: Full text from terminal
2. **Steps to reproduce**: What you did before error
3. **Environment**: OS, browser, Python version
4. **Audio details**: Format, size, duration
5. **API key status**: Is it set? (don't share the actual key)

### Where to Get Help

1. Check this troubleshooting guide
2. Review [MICROPHONE_RECORDING.md](MICROPHONE_RECORDING.md)
3. Check [UNIVERSAL_AUDIO.md](UNIVERSAL_AUDIO.md)
4. Look at terminal output for clues
5. Test with different audio files

---

## Prevention Tips

### Best Practices

1. **Keep recordings short** (under 2 minutes)
2. **Use good audio quality** (clear speech, low noise)
3. **Test before long sessions** (do a quick test first)
4. **Save work frequently** (don't rely on one long recording)
5. **Have backup method** (can always type if audio fails)

### Regular Maintenance

1. **Restart app daily** (clears any issues)
2. **Clear temp files** (rm -rf data/audio/*)
3. **Update dependencies** (pip install -U -r requirements.txt)
4. **Check API quota** (at Google AI Studio)

---

## Quick Fixes Summary

| Issue | Quick Fix |
|-------|-----------|
| No API key | Set GOOGLE_API_KEY in .env |
| Invalid key | Get new key from Google AI Studio |
| Network error | Check internet, try again |
| File too large | Keep under 5 minutes |
| Wrong format | Use WAV or MP3 |
| Mic not working | Check browser permissions |
| Upload fails | Try Record instead |
| Record fails | Try Upload instead |
| Both fail | Use text input |

---

## Still Not Working?

### Last Resort Steps

1. **Restart everything**:
   ```bash
   # Stop app (Ctrl+C)
   # Restart
   streamlit run app.py
   ```

2. **Clear cache**:
   ```bash
   rm -rf .streamlit/cache
   rm -rf data/audio/*
   ```

3. **Reinstall dependencies**:
   ```bash
   pip uninstall audio-recorder-streamlit google-genai
   pip install -r requirements.txt
   ```

4. **Use text input temporarily**:
   - Type your content manually
   - Fix audio issues later
   - Don't let it block your writing!

---

**Remember**: Audio is a convenience feature. You can always type your content if audio isn't working!

🎤 Good luck! 📖✨
