# UI Components

This directory contains reusable UI components for the AI Novel Editor.

## Universal Audio Input

The `universal_text_input()` function provides a unified interface for text input with optional audio transcription support.

### Features

- **Text Input**: Standard Streamlit text_input or text_area widgets
- **Audio Upload**: Upload pre-recorded audio files for transcription
- **Microphone Recording**: Record audio directly in the browser (requires `audio-recorder-streamlit`)
- **Transcript Management**: Automatic merging of transcripts with existing text
- **Session State**: Transcripts are stored in session state for persistence
- **Visual Feedback**: Loading spinners and success/error messages

### Usage

```python
from src.ui.audio_input import universal_text_input
from src.services.audio_service import AudioService

# Initialize audio service
audio_service = AudioService()

# Use in your Streamlit app
user_input = universal_text_input(
    label="Story Description",
    key="story_desc",
    audio_service=audio_service,
    input_type="text_area",  # or "text_input"
    height=200,
    help_text="Describe your story idea",
    audio_prompt="Transcribe the story description",
    default_value=""
)
```

### Parameters

- **label** (str): Label for the input field
- **key** (str): Unique key for the widget (used for session state)
- **audio_service** (AudioService): AudioService instance for transcription
- **input_type** (str): Type of widget - "text_area" or "text_input" (default: "text_area")
- **height** (int, optional): Height for text_area widget
- **help_text** (str, optional): Help text to display
- **audio_prompt** (str, optional): Custom prompt for audio transcription
- **default_value** (str): Default value for the input field (default: "")

### Returns

- **str**: The input text (from typing or audio transcription)

### Audio Modes

The component supports three input modes:

1. **Text Mode** (default): Standard text input
2. **Upload Mode**: Upload pre-recorded audio files (WAV, MP3, AIFF, AAC, OGG, FLAC)
3. **Record Mode**: Record audio directly in browser (requires `audio-recorder-streamlit` package)

### Transcript Management

Transcripts are automatically managed through session state:

- **Storage**: Transcripts are stored with key format `transcript_{key}`
- **Merging**: New transcripts are merged with existing text using double newlines
- **Clearing**: Users can clear transcripts before applying them
- **Preview**: Transcripts are shown in a preview area before use

### Session State Keys

The component uses the following session state keys:

- `transcript_{key}`: Stores the transcribed text
- `audio_mode_{key}`: Stores the selected audio mode
- `show_audio_{key}`: Controls visibility of audio input UI

### Example: Multiple Inputs

```python
# Chapter title (short text)
title = universal_text_input(
    label="Chapter Title",
    key="chapter_title",
    audio_service=audio_service,
    input_type="text_input"
)

# Chapter content (long text)
content = universal_text_input(
    label="Chapter Content",
    key="chapter_content",
    audio_service=audio_service,
    input_type="text_area",
    height=400
)

# Story notes (with custom prompt)
notes = universal_text_input(
    label="Story Notes",
    key="story_notes",
    audio_service=audio_service,
    input_type="text_area",
    audio_prompt="Transcribe the story notes and ideas"
)
```

### Requirements

- **Required**: `streamlit`, `google-genai` (for AudioService)
- **Optional**: `audio-recorder-streamlit` (for microphone recording)

### Error Handling

The component handles errors gracefully:

- Missing API key: Shows error message with setup instructions
- Invalid audio file: Shows validation error
- Transcription failure: Shows error with troubleshooting tips
- Network issues: Shows retry option

### Visual Feedback

- **Loading**: Spinner with "🎧 Transcribing..." message
- **Success**: Green checkmark with "✅ Transcribed successfully!"
- **Error**: Red X with detailed error message
- **Preview**: Disabled text area showing transcript before use
