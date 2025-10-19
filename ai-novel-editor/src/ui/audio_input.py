"""Universal audio input component for Streamlit."""

from __future__ import annotations

import streamlit as st
from typing import Optional


def audio_input_widget(
    label: str,
    key: str,
    audio_service,
    help_text: Optional[str] = None,
    prompt: Optional[str] = None
) -> Optional[str]:
  """Render an audio input widget with file upload.
  
  Args:
    label: Label for the audio input.
    key: Unique key for the widget.
    audio_service: AudioService instance.
    help_text: Optional help text to display.
    prompt: Optional custom prompt for transcription.
    
  Returns:
    Transcribed text if audio was uploaded, None otherwise.
  """
  if not audio_service.is_available():
    return None
  
  # Create a container for the audio input
  with st.expander(f"🎤 {label}", expanded=False):
    st.caption("Upload an audio file to transcribe")
    
    if help_text:
      st.info(help_text)
    
    # File uploader
    uploaded_audio = st.file_uploader(
        "Choose an audio file",
        type=['wav', 'mp3', 'aiff', 'aac', 'ogg', 'flac'],
        key=f"audio_{key}",
        help="Supported: WAV, MP3, AIFF, AAC, OGG, FLAC"
    )
    
    if uploaded_audio:
      with st.spinner("🎧 Transcribing audio..."):
        # Save the uploaded file
        audio_path = audio_service.save_uploaded_audio(uploaded_audio)
        
        if audio_path:
          # Transcribe using Gemini
          default_prompt = "Generate a detailed transcript of the speech."
          transcript = audio_service.transcribe_audio_file(
              audio_path,
              prompt=prompt or default_prompt
          )
          
          if transcript:
            st.success("✅ Audio transcribed!")
            st.write("**Transcript:**")
            st.write(transcript)
            return transcript
          else:
            st.error("Failed to transcribe audio. Please try again.")
        else:
          st.error("Failed to save audio file.")
    
    return None


def audio_button_inline(
    text_area_key: str,
    audio_service,
    button_label: str = "🎤 Use Audio",
    prompt: Optional[str] = None
) -> Optional[str]:
  """Render an inline audio button that transcribes and fills a text area.
  
  Args:
    text_area_key: Key of the text area to fill.
    audio_service: AudioService instance.
    button_label: Label for the button.
    prompt: Optional custom prompt for transcription.
    
  Returns:
    Transcribed text if audio was uploaded, None otherwise.
  """
  if not audio_service.is_available():
    return None
  
  col1, col2 = st.columns([3, 1])
  
  with col2:
    if st.button(button_label, key=f"audio_btn_{text_area_key}"):
      st.session_state[f"show_audio_upload_{text_area_key}"] = True
  
  # Show audio upload if button was clicked
  if st.session_state.get(f"show_audio_upload_{text_area_key}", False):
    uploaded_audio = st.file_uploader(
        "Upload audio file",
        type=['wav', 'mp3', 'aiff', 'aac', 'ogg', 'flac'],
        key=f"audio_upload_{text_area_key}"
    )
    
    if uploaded_audio:
      with st.spinner("🎧 Transcribing..."):
        audio_path = audio_service.save_uploaded_audio(uploaded_audio)
        
        if audio_path:
          default_prompt = "Generate a detailed transcript of the speech."
          transcript = audio_service.transcribe_audio_file(
              audio_path,
              prompt=prompt or default_prompt
          )
          
          if transcript:
            st.success("✅ Transcribed!")
            # Reset the upload state
            st.session_state[f"show_audio_upload_{text_area_key}"] = False
            return transcript
          else:
            st.error("Failed to transcribe.")
        else:
          st.error("Failed to save audio.")
  
  return None


def universal_text_input(
    label: str,
    key: str,
    audio_service,
    input_type: str = "text_area",
    height: int = 150,
    help_text: Optional[str] = None,
    audio_prompt: Optional[str] = None,
    default_value: str = ""
) -> str:
  """Universal text input with audio option.
  
  Args:
    label: Label for the input.
    key: Unique key for the widget.
    audio_service: AudioService instance.
    input_type: Type of input ('text_area', 'text_input').
    height: Height for text_area.
    help_text: Optional help text.
    audio_prompt: Optional custom prompt for audio transcription.
    default_value: Default value for the input.
    
  Returns:
    The input text (from typing or audio).
  """
  # Check if we have a transcription in session state
  transcript_key = f"transcript_{key}"
  if transcript_key in st.session_state:
    default_value = st.session_state[transcript_key]
  
  # Show audio option if available
  if audio_service.is_available():
    col1, col2 = st.columns([4, 1])
    
    with col1:
      st.write(f"**{label}**")
    
    with col2:
      if st.button("🎤 Audio", key=f"audio_toggle_{key}", help="Use audio input"):
        st.session_state[f"show_audio_{key}"] = not st.session_state.get(f"show_audio_{key}", False)
    
    # Show audio upload if toggled
    if st.session_state.get(f"show_audio_{key}", False):
      uploaded_audio = st.file_uploader(
          "Upload audio file",
          type=['wav', 'mp3', 'aiff', 'aac', 'ogg', 'flac'],
          key=f"audio_file_{key}"
      )
      
      if uploaded_audio:
        with st.spinner("🎧 Transcribing..."):
          audio_path = audio_service.save_uploaded_audio(uploaded_audio)
          
          if audio_path:
            transcript = audio_service.transcribe_audio_file(
                audio_path,
                prompt=audio_prompt or "Generate a detailed transcript."
            )
            
            if transcript:
              st.success("✅ Transcribed!")
              st.session_state[transcript_key] = transcript
              st.session_state[f"show_audio_{key}"] = False
              st.rerun()
  
  # Render the text input
  if input_type == "text_area":
    value = st.text_area(
        label if not audio_service.is_available() else "",
        value=default_value,
        height=height,
        key=f"text_{key}",
        help=help_text,
        label_visibility="collapsed" if audio_service.is_available() else "visible"
    )
  else:
    value = st.text_input(
        label if not audio_service.is_available() else "",
        value=default_value,
        key=f"text_{key}",
        help=help_text,
        label_visibility="collapsed" if audio_service.is_available() else "visible"
    )
  
  return value
