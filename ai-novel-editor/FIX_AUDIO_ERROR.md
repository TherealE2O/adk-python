# Fix for Audio Upload Error

## Error Message
```
AttributeError: 'list' object has no attribute 'lower'
File "app.py", line 214, in show_worldbuilding
    type=list(supported_formats.keys()).lower(),
```

## Problem

The old audio upload code has a bug where it tries to call `.lower()` on a list instead of on individual strings.

## Quick Fix

Find this line in `app.py` (around line 214):

```python
type=list(supported_formats.keys()).lower(),
```

Replace it with:

```python
type=['wav', 'mp3', 'aiff', 'aac', 'ogg', 'flac'],
```

## Better Solution: Update to Latest Version

The latest version uses universal audio input everywhere. To update:

1. **Backup your current file**:
   ```bash
   cp app.py app.py.backup
   ```

2. **Pull the latest changes**:
   ```bash
   git pull origin main
   ```

3. **Or manually update**:
   - The new version doesn't have the old audio mode selector
   - It uses `universal_text_input()` component everywhere
   - Every text field has a 🎤 Audio button

## What Changed

### Old Approach (Buggy)
```python
if st.session_state.audio_mode == 'upload':
    uploaded_audio = st.file_uploader(
        "Choose an audio file",
        type=list(supported_formats.keys()).lower(),  # BUG HERE
        key="initial_audio_upload"
    )
```

### New Approach (Fixed)
```python
initial_answer = universal_text_input(
    "What is your story about?",
    "initial_story_answer",
    audio_service,
    input_type="text_area",
    height=150,
    help_text="Describe your story idea. You can type or use audio.",
    audio_prompt="Generate a detailed transcript of this story description."
)
```

## Manual Fix Steps

If you can't pull the latest version, here's how to fix it manually:

### Step 1: Fix the immediate error

Find line 214 (or search for `type=list(supported_formats.keys()).lower()`):

**Before**:
```python
type=list(supported_formats.keys()).lower(),
```

**After**:
```python
type=['wav', 'mp3', 'aiff', 'aac', 'ogg', 'flac'],
```

### Step 2: Apply the same fix to all file uploaders

Search for all instances of `st.file_uploader` with `type=` parameter and ensure they use a list of lowercase strings:

```python
# Correct format
type=['wav', 'mp3', 'aiff', 'aac', 'ogg', 'flac']

# NOT this
type=list(supported_formats.keys()).lower()  # WRONG
```

## Verification

After fixing, test by:

1. Start the app: `streamlit run app.py`
2. Create a new project
3. Go to world-building
4. Try to upload an audio file
5. Should work without errors

## Need Help?

If you're still having issues:

1. Check that you're using the latest version
2. Make sure all file uploaders use the correct format
3. Restart the Streamlit app after making changes
4. Clear browser cache if needed

## Prevention

To avoid this in the future:

1. Always use explicit file type lists:
   ```python
   type=['wav', 'mp3', 'aiff', 'aac', 'ogg', 'flac']
   ```

2. Don't call `.lower()` on lists:
   ```python
   # WRONG
   type=some_list.lower()
   
   # RIGHT
   type=[item.lower() for item in some_list]
   ```

3. Or use the new universal audio input component which handles this correctly.
