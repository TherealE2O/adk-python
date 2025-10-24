"""Universal audio input component for Streamlit with Gemini 2.5 integration."""

from __future__ import annotations

import streamlit as st
from typing import Optional
import tempfile
import os

try:
    from audio_recorder_streamlit import audio_recorder
    AUDIO_RECORDER_AVAILABLE = True
except ImportError:
    AUDIO_RECORDER_AVAILABLE = False


def universal_text_input(
    label: str,
    key: str,
    audio_service,
    input_type: str = "text_area",
    height: Optional[int] = None,
    help_text: Optional[str] = None,
    audio_prompt: Optional[str] = None,
    default_value: str = ""
) -> str:
    """Universal text input with audio option (upload or record).
    
    Provides a unified interface for text input that supports:
    - Standard text input (text_input or text_area)
    - Audio file upload with transcription
    - Microphone recording with transcription (if audio-recorder-streamlit is installed)
    
    Args:
        label: Label for the input field
        key: Unique key for the widget (used for session state management)
        audio_service: Audio service instance with transcribe methods
        input_type: Type of input widget ('text_input' or 'text_area')
        height: Height for text_area (optional)
        help_text: Optional help text to display
        audio_prompt: Optional custom prompt for audio transcription
        default_value: Default value for the input field

    Returns:
        str: The input text (from typing or audio transcription)
    """
    # Initialize session state keys
    text_key = f"text_{key}"
    show_audio_key = f"show_audio_{key}"
    pending_transcript_key = f"pending_transcript_{key}"
    
    # Initialize text value in session state if not present
    if text_key not in st.session_state:
        st.session_state[text_key] = default_value
    
    # Check for pending transcript and merge it
    if pending_transcript_key in st.session_state:
        transcript = st.session_state.pop(pending_transcript_key)
        if transcript and transcript.strip():
            # Merge transcript with existing text
            if st.session_state[text_key]:
                st.session_state[text_key] = f"{st.session_state[text_key]}\n\n{transcript}"
            else:
                st.session_state[text_key] = transcript
    
    # Check if audio service is available
    audio_available = hasattr(audio_service, 'transcribe_audio') or hasattr(audio_service, 'transcribe_file')
    
    # Create header with audio toggle button
    if audio_available:
        col1, col2 = st.columns([5, 1])
        
        with col1:
            st.write(f"**{label}**")
        
        with col2:
            # Audio mode toggle
            if st.button("🎤", key=f"audio_toggle_{key}", help="Record or upload audio"):
                st.session_state[show_audio_key] = not st.session_state.get(show_audio_key, False)
        
        # Show audio input options if toggled
        if st.session_state.get(show_audio_key, False):
            st.divider()
            _render_audio_interface(
                key=key,
                audio_service=audio_service,
                audio_prompt=audio_prompt,
                pending_transcript_key=pending_transcript_key,
                show_audio_key=show_audio_key
            )
            st.divider()
    
    # Render the text input widget
    if input_type == "text_area":
        text_area_kwargs = {
            "label": label,
            "value": st.session_state[text_key],
            "key": text_key,
            "help": help_text,
            "label_visibility": "collapsed" if audio_available else "visible"
        }
        if height is not None:
            text_area_kwargs["height"] = height
        return st.text_area(**text_area_kwargs)
    else:
        return st.text_input(
            label=label,
            value=st.session_state[text_key],
            key=text_key,
            help=help_text,
            label_visibility="collapsed" if audio_available else "visible"
        )


def _render_audio_interface(
    key: str,
    audio_service,
    audio_prompt: Optional[str],
    pending_transcript_key: str,
    show_audio_key: str
) -> None:
    """Render audio input interface with tabs for upload and recording."""
    
    # Create tabs for different audio input methods
    if AUDIO_RECORDER_AVAILABLE:
        tab1, tab2 = st.tabs(["🎙️ Record", "📁 Upload File"])
        
        with tab1:
            _render_microphone_recording(
                key=key,
                audio_service=audio_service,
                audio_prompt=audio_prompt,
                pending_transcript_key=pending_transcript_key,
                show_audio_key=show_audio_key
            )
        
        with tab2:
            _render_file_upload(
                key=key,
                audio_service=audio_service,
                audio_prompt=audio_prompt,
                pending_transcript_key=pending_transcript_key,
                show_audio_key=show_audio_key
            )
    else:
        st.info("💡 Install `audio-recorder-streamlit` for microphone recording: `pip install audio-recorder-streamlit`")
        _render_file_upload(
            key=key,
            audio_service=audio_service,
            audio_prompt=audio_prompt,
            pending_transcript_key=pending_transcript_key,
            show_audio_key=show_audio_key
        )


def _render_microphone_recording(
    key: str,
    audio_service,
    audio_prompt: Optional[str],
    pending_transcript_key: str,
    show_audio_key: str
) -> None:
    """Render microphone recording interface with proper state management."""
    
    # Session state keys - each must be unique per component
    stored_audio_key = f"stored_audio_{key}"
    is_processing_key = f"is_processing_{key}"
    
    # Initialize state
    if stored_audio_key not in st.session_state:
        st.session_state[stored_audio_key] = None
    if is_processing_key not in st.session_state:
        st.session_state[is_processing_key] = False
    
    # Instructions
    st.caption("🎙️ Click the microphone icon below to start/stop recording")
    
    # The audio recorder component
    # This will return bytes when you stop recording, and None otherwise
    current_audio = audio_recorder(
        text="",
        recording_color="#e74c3c",
        neutral_color="#3498db", 
        icon_name="microphone",
        icon_size="2x",
        key=f"recorder_widget_{key}"
    )
    
    # When we get audio bytes from the recorder, save them to session state
    if current_audio is not None:
        # Only store if it's different from what we already have
        if st.session_state[stored_audio_key] != current_audio:
            if len(current_audio) > 5000:  # Minimum audio size check
                st.session_state[stored_audio_key] = current_audio
            else:
                st.warning("⚠️ Recording too short. Please speak for at least 1 second.")
    
    # Now check our stored audio and show controls
    # This is the key - we check stored_audio_key, not current_audio
    if st.session_state[stored_audio_key] is not None:
        
        # Only show controls if we're not currently processing
        if not st.session_state[is_processing_key]:
            st.success("✅ Recording complete!")
            
            # Show audio preview
            st.audio(st.session_state[stored_audio_key], format="audio/wav")
            
            # Control buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📤 Transcribe", key=f"btn_transcribe_{key}", use_container_width=True, type="primary"):
                    st.session_state[is_processing_key] = True
                    st.rerun()
            
            with col2:
                if st.button("🔄 New Recording", key=f"btn_new_{key}", use_container_width=True):
                    st.session_state[stored_audio_key] = None
                    st.rerun()
            
            with col3:
                if st.button("❌ Cancel", key=f"btn_cancel_{key}", use_container_width=True):
                    st.session_state[stored_audio_key] = None
                    st.session_state[show_audio_key] = False
                    st.rerun()
        
        # Handle transcription
        if st.session_state[is_processing_key]:
            with st.spinner("🎧 Transcribing your audio..."):
                try:
                    audio_data = st.session_state[stored_audio_key]
                    
                    # Try transcribe_audio first
                    if hasattr(audio_service, 'transcribe_audio'):
                        transcript = audio_service.transcribe_audio(
                            audio_data=audio_data,
                            mime_type="audio/wav",
                            prompt=audio_prompt or "Transcribe this audio clearly and accurately."
                        )
                    else:
                        # Fallback to file-based transcription
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                            tmp_file.write(audio_data)
                            temp_path = tmp_file.name
                        
                        try:
                            transcript = audio_service.transcribe_file(
                                file_path=temp_path,
                                prompt=audio_prompt or "Transcribe this audio clearly and accurately."
                            )
                        finally:
                            if os.path.exists(temp_path):
                                os.unlink(temp_path)
                    
                    # Check if we got a valid transcript
                    if transcript and transcript.strip():
                        # Success! Store the transcript and clean up
                        st.session_state[pending_transcript_key] = transcript
                        st.session_state[stored_audio_key] = None
                        st.session_state[is_processing_key] = False
                        st.session_state[show_audio_key] = False
                        st.success("✅ Transcription complete!")
                        st.rerun()
                    else:
                        st.error("❌ No speech detected in the recording.")
                        st.session_state[stored_audio_key] = None
                        st.session_state[is_processing_key] = False
                        
                except Exception as e:
                    st.error(f"❌ Transcription error: {str(e)}")
                    st.info("💡 Check your API key and internet connection.")
                    st.session_state[stored_audio_key] = None
                    st.session_state[is_processing_key] = False


def _render_file_upload(
    key: str,
    audio_service,
    audio_prompt: Optional[str],
    pending_transcript_key: str,
    show_audio_key: str
) -> None:
    """Render file upload interface."""
    
    st.caption("📁 Upload an audio file to transcribe")
    
    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=['wav', 'mp3', 'aiff', 'aac', 'ogg', 'flac', 'm4a', 'webm'],
        key=f"upload_{key}",
        help="Supported formats: WAV, MP3, AIFF, AAC, OGG, FLAC, M4A, WebM",
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        # Show preview
        st.audio(uploaded_file, format=f"audio/{uploaded_file.name.split('.')[-1]}")
        
        if st.button("✅ Transcribe", key=f"transcribe_upload_{key}", use_container_width=True):
            with st.spinner("🎧 Transcribing audio file..."):
                try:
                    # Save uploaded file to temp location
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        temp_path = tmp_file.name
                    
                    try:
                        # Transcribe using the audio service
                        if hasattr(audio_service, 'transcribe_file'):
                            transcript = audio_service.transcribe_file(
                                file_path=temp_path,
                                prompt=audio_prompt or "Transcribe this audio clearly and accurately."
                            )
                        elif hasattr(audio_service, 'transcribe_audio'):
                            # Read file and use transcribe_audio
                            with open(temp_path, 'rb') as f:
                                audio_data = f.read()
                            transcript = audio_service.transcribe_audio(
                                audio_data=audio_data,
                                mime_type=uploaded_file.type,
                                prompt=audio_prompt or "Transcribe this audio clearly and accurately."
                            )
                        else:
                            raise AttributeError("Audio service must have 'transcribe_file' or 'transcribe_audio' method")
                        
                        if transcript and transcript.strip():
                            # Store transcript to be merged
                            st.session_state[pending_transcript_key] = transcript
                            st.session_state[show_audio_key] = False
                            st.success("✅ Audio transcribed successfully!")
                            st.rerun()
                        else:
                            st.error("❌ No speech detected in the audio file.")
                            
                    finally:
                        if os.path.exists(temp_path):
                            os.unlink(temp_path)
                            
                except Exception as e:
                    st.error(f"❌ Transcription failed: {str(e)}")
                    st.info("💡 Make sure your audio service is properly configured.")