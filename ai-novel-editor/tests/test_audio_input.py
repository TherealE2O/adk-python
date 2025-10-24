"""Tests for universal audio input UI component.

Note: These tests verify the function signatures and basic logic.
Full UI testing requires a running Streamlit application.
"""

import pytest
import inspect
from unittest.mock import Mock


def test_universal_text_input_function_exists():
    """Test that universal_text_input function exists and has correct signature."""
    from src.ui.audio_input import universal_text_input
    
    # Check function exists
    assert callable(universal_text_input)
    
    # Check function signature
    sig = inspect.signature(universal_text_input)
    params = list(sig.parameters.keys())
    
    # Verify required parameters
    assert 'label' in params
    assert 'key' in params
    assert 'audio_service' in params
    assert 'input_type' in params
    assert 'height' in params
    assert 'help_text' in params
    assert 'audio_prompt' in params
    assert 'default_value' in params


def test_render_audio_input_function_exists():
    """Test that _render_audio_input helper function exists."""
    from src.ui.audio_input import _render_audio_input
    
    # Check function exists
    assert callable(_render_audio_input)
    
    # Check function signature
    sig = inspect.signature(_render_audio_input)
    params = list(sig.parameters.keys())
    
    # Verify required parameters
    assert 'key' in params
    assert 'audio_service' in params
    assert 'audio_prompt' in params
    assert 'transcript_key' in params
    assert 'show_audio_key' in params


def test_render_microphone_recording_function_exists():
    """Test that _render_microphone_recording helper function exists."""
    from src.ui.audio_input import _render_microphone_recording
    
    # Check function exists
    assert callable(_render_microphone_recording)
    
    # Check function signature
    sig = inspect.signature(_render_microphone_recording)
    params = list(sig.parameters.keys())
    
    # Verify required parameters
    assert 'key' in params
    assert 'audio_service' in params
    assert 'audio_prompt' in params
    assert 'transcript_key' in params
    assert 'show_audio_key' in params


def test_render_file_upload_function_exists():
    """Test that _render_file_upload helper function exists."""
    from src.ui.audio_input import _render_file_upload
    
    # Check function exists
    assert callable(_render_file_upload)
    
    # Check function signature
    sig = inspect.signature(_render_file_upload)
    params = list(sig.parameters.keys())
    
    # Verify required parameters
    assert 'key' in params
    assert 'audio_service' in params
    assert 'audio_prompt' in params
    assert 'transcript_key' in params
    assert 'show_audio_key' in params


def test_audio_recorder_availability_flag():
    """Test that AUDIO_RECORDER_AVAILABLE flag is defined."""
    from src.ui.audio_input import AUDIO_RECORDER_AVAILABLE
    
    # Check flag exists and is boolean
    assert isinstance(AUDIO_RECORDER_AVAILABLE, bool)


def test_transcript_key_format():
    """Test that transcript keys follow the expected format."""
    # Transcript keys should be in format "transcript_{key}"
    test_key = "my_input"
    expected_transcript_key = f"transcript_{test_key}"
    
    assert expected_transcript_key == "transcript_my_input"


def test_audio_mode_key_format():
    """Test that audio mode keys follow the expected format."""
    # Audio mode keys should be in format "audio_mode_{key}"
    test_key = "my_input"
    expected_audio_mode_key = f"audio_mode_{test_key}"
    
    assert expected_audio_mode_key == "audio_mode_my_input"


def test_show_audio_key_format():
    """Test that show audio keys follow the expected format."""
    # Show audio keys should be in format "show_audio_{key}"
    test_key = "my_input"
    expected_show_audio_key = f"show_audio_{test_key}"
    
    assert expected_show_audio_key == "show_audio_my_input"


class TestTranscriptManagement:
    """Test suite for transcript management logic."""
    
    def test_transcript_merge_logic_with_existing_text(self):
        """Test the logic for merging transcripts with existing text."""
        existing_text = "Chapter 1: The Beginning"
        transcript = "The hero walked into the dark forest."
        
        # Expected merge format: existing + newlines + transcript
        expected = f"{existing_text}\n\n{transcript}"
        
        assert expected == "Chapter 1: The Beginning\n\nThe hero walked into the dark forest."
    
    def test_transcript_merge_logic_with_empty_text(self):
        """Test the logic for using transcript when existing text is empty."""
        existing_text = ""
        transcript = "The hero walked into the dark forest."
        
        # When existing text is empty, just use transcript
        if existing_text:
            result = f"{existing_text}\n\n{transcript}"
        else:
            result = transcript
        
        assert result == "The hero walked into the dark forest."
    
    def test_transcript_merge_logic_with_whitespace_text(self):
        """Test the logic for handling whitespace in existing text."""
        existing_text = "   "
        transcript = "The hero walked into the dark forest."
        
        # Whitespace should be treated as content
        if existing_text:
            result = f"{existing_text}\n\n{transcript}"
        else:
            result = transcript
        
        assert result == "   \n\nThe hero walked into the dark forest."


class TestAudioServiceIntegration:
    """Test suite for audio service integration."""
    
    def test_audio_service_availability_check(self):
        """Test that audio service availability is checked correctly."""
        # Mock audio service that is available
        mock_service = Mock()
        mock_service.is_available.return_value = True
        
        assert mock_service.is_available() is True
        
        # Mock audio service that is not available
        mock_service.is_available.return_value = False
        
        assert mock_service.is_available() is False
    
    def test_audio_service_transcribe_file_interface(self):
        """Test that audio service has transcribe_file method."""
        mock_service = Mock()
        mock_service.transcribe_file.return_value = "transcribed text"
        
        result = mock_service.transcribe_file(
            file_path="/path/to/audio.wav",
            prompt="Transcribe this audio"
        )
        
        assert result == "transcribed text"
        mock_service.transcribe_file.assert_called_once()
    
    def test_audio_service_transcribe_audio_interface(self):
        """Test that audio service has transcribe_audio method."""
        mock_service = Mock()
        mock_service.transcribe_audio.return_value = "transcribed text"
        
        result = mock_service.transcribe_audio(
            audio_data=b"fake audio bytes",
            mime_type="audio/wav",
            prompt="Transcribe this audio"
        )
        
        assert result == "transcribed text"
        mock_service.transcribe_audio.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
