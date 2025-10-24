"""Tests for the AudioService."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.services.audio_service import AudioService
from src.config import config


@pytest.fixture
def mock_genai_client():
    """Create a mock Gemini client."""
    with patch('src.services.audio_service.genai.Client') as mock_client:
        yield mock_client


def test_audio_service_initialization_with_api_key(mock_genai_client):
    """Test Audio service initialization with API key."""
    service = AudioService(api_key="test_api_key")
    
    assert service.api_key == "test_api_key"
    assert service.model_name == config.gemini_model
    assert service.is_available() is True


def test_audio_service_initialization_without_api_key():
    """Test Audio service initialization without API key."""
    with patch('src.services.audio_service.config') as mock_config:
        mock_config.google_api_key = None
        mock_config.gemini_model = "gemini-2.0-flash-exp"
        
        service = AudioService()
        
        assert service.is_available() is False


def test_is_available_with_valid_key(mock_genai_client):
    """Test is_available returns True with valid API key."""
    service = AudioService(api_key="valid_key")
    assert service.is_available() is True


def test_is_available_with_empty_key():
    """Test is_available returns False with empty API key."""
    with patch('src.services.audio_service.config') as mock_config:
        mock_config.google_api_key = None
        mock_config.gemini_model = "gemini-2.0-flash-exp"
        service = AudioService(api_key="")
        assert service.is_available() is False


def test_is_available_with_none_key():
    """Test is_available returns False with None API key."""
    with patch('src.services.audio_service.config') as mock_config:
        mock_config.google_api_key = None
        mock_config.gemini_model = "gemini-2.0-flash-exp"
        service = AudioService(api_key=None)
        assert service.is_available() is False


def test_transcribe_file_without_api_key():
    """Test transcribe_file raises error when service is not available."""
    with patch('src.services.audio_service.config') as mock_config:
        mock_config.google_api_key = None
        mock_config.gemini_model = "gemini-2.0-flash-exp"
        service = AudioService(api_key=None)
        
        with pytest.raises(ValueError, match="Audio Service is not available"):
            service.transcribe_file("test.mp3")


def test_transcribe_audio_without_api_key():
    """Test transcribe_audio raises error when service is not available."""
    with patch('src.services.audio_service.config') as mock_config:
        mock_config.google_api_key = None
        mock_config.gemini_model = "gemini-2.0-flash-exp"
        service = AudioService(api_key=None)
        
        with pytest.raises(ValueError, match="Audio Service is not available"):
            service.transcribe_audio(b"audio_data")


def test_validate_audio_file_not_found():
    """Test validation fails for non-existent file."""
    service = AudioService(api_key="test_key")
    
    with pytest.raises(ValueError, match="Audio file not found"):
        service._validate_audio_file("nonexistent.mp3")


def test_validate_audio_file_unsupported_format(tmp_path):
    """Test validation fails for unsupported format."""
    service = AudioService(api_key="test_key")
    
    # Create a test file with unsupported extension
    test_file = tmp_path / "test.txt"
    test_file.write_text("test")
    
    with pytest.raises(ValueError, match="Unsupported audio format"):
        service._validate_audio_file(str(test_file))


def test_validate_audio_file_empty_file(tmp_path):
    """Test validation fails for empty file."""
    service = AudioService(api_key="test_key")
    
    # Create an empty audio file
    test_file = tmp_path / "test.mp3"
    test_file.touch()
    
    with pytest.raises(ValueError, match="Audio file is empty"):
        service._validate_audio_file(str(test_file))


def test_validate_audio_file_too_large(tmp_path):
    """Test validation fails for file exceeding size limit."""
    service = AudioService(api_key="test_key")
    
    # Create a file larger than MAX_FILE_SIZE
    test_file = tmp_path / "test.mp3"
    test_file.write_bytes(b"x" * (AudioService.MAX_FILE_SIZE + 1))
    
    with pytest.raises(ValueError, match="Audio file too large"):
        service._validate_audio_file(str(test_file))


def test_validate_audio_file_success(tmp_path):
    """Test validation succeeds for valid file."""
    service = AudioService(api_key="test_key")
    
    # Create a valid audio file
    test_file = tmp_path / "test.mp3"
    test_file.write_bytes(b"fake audio data")
    
    # Should not raise any exception
    service._validate_audio_file(str(test_file))


def test_validate_audio_data_empty():
    """Test validation fails for empty audio data."""
    service = AudioService(api_key="test_key")
    
    with pytest.raises(ValueError, match="Audio data is empty"):
        service._validate_audio_data(b"", "audio/wav")


def test_validate_audio_data_too_large():
    """Test validation fails for data exceeding size limit."""
    service = AudioService(api_key="test_key")
    
    large_data = b"x" * (AudioService.MAX_FILE_SIZE + 1)
    
    with pytest.raises(ValueError, match="Audio data too large"):
        service._validate_audio_data(large_data, "audio/wav")


def test_validate_audio_data_unsupported_mime_type():
    """Test validation fails for unsupported MIME type."""
    service = AudioService(api_key="test_key")
    
    with pytest.raises(ValueError, match="Unsupported MIME type"):
        service._validate_audio_data(b"audio data", "audio/unsupported")


def test_validate_audio_data_success():
    """Test validation succeeds for valid audio data."""
    service = AudioService(api_key="test_key")
    
    # Should not raise any exception
    service._validate_audio_data(b"fake audio data", "audio/wav")


def test_get_supported_formats():
    """Test getting supported audio formats."""
    formats = AudioService.get_supported_formats()
    
    assert isinstance(formats, dict)
    assert 'mp3' in formats
    assert 'wav' in formats
    assert 'flac' in formats
    assert 'ogg' in formats
    assert 'webm' in formats
    assert formats['mp3'] == 'audio/mp3'
    assert formats['wav'] == 'audio/wav'


def test_get_max_duration_seconds():
    """Test getting maximum audio duration."""
    max_duration = AudioService.get_max_duration_seconds()
    
    assert isinstance(max_duration, int)
    assert max_duration == config.max_audio_duration


def test_estimate_tokens_from_duration():
    """Test token estimation from audio duration."""
    # Gemini uses 32 tokens per second
    tokens = AudioService.estimate_tokens_from_duration(10.0)
    assert tokens == 320
    
    tokens = AudioService.estimate_tokens_from_duration(60.0)
    assert tokens == 1920


def test_get_error_message_rate_limit():
    """Test error message for rate limit errors."""
    from google.api_core import exceptions as google_exceptions
    
    service = AudioService(api_key="test_key")
    error = google_exceptions.ResourceExhausted("Rate limit exceeded")
    
    message = service.get_error_message(error)
    
    assert "rate limit" in message.lower()
    assert "wait" in message.lower()


def test_get_error_message_authentication():
    """Test error message for authentication errors."""
    from google.api_core import exceptions as google_exceptions
    
    service = AudioService(api_key="test_key")
    error = google_exceptions.Unauthenticated("Invalid API key")
    
    message = service.get_error_message(error)
    
    assert "authentication" in message.lower()
    assert "GOOGLE_API_KEY" in message


def test_get_error_message_timeout():
    """Test error message for timeout errors."""
    from google.api_core import exceptions as google_exceptions
    
    service = AudioService(api_key="test_key")
    error = google_exceptions.DeadlineExceeded("Request timed out")
    
    message = service.get_error_message(error)
    
    assert "timed out" in message.lower()
    assert "connection" in message.lower()


def test_get_error_message_generic():
    """Test error message for generic errors."""
    service = AudioService(api_key="test_key")
    error = Exception("Something went wrong")
    
    message = service.get_error_message(error)
    
    assert "unexpected error" in message.lower()
    assert "Something went wrong" in message


def test_generate_with_file_path(mock_genai_client, tmp_path):
    """Test generate method with file_path parameter."""
    service = AudioService(api_key="test_key")
    
    # Create a valid test file
    test_file = tmp_path / "test.mp3"
    test_file.write_bytes(b"fake audio data")
    
    # Mock the client methods
    mock_client_instance = MagicMock()
    mock_genai_client.return_value = mock_client_instance
    service.client = mock_client_instance
    
    mock_response = MagicMock()
    mock_response.text = "Transcribed text"
    mock_client_instance.models.generate_content.return_value = mock_response
    mock_client_instance.files.upload.return_value = MagicMock()
    
    result = service.generate("Transcribe this", file_path=str(test_file))
    
    assert result == "Transcribed text"


def test_generate_with_audio_data(mock_genai_client):
    """Test generate method with audio_data parameter."""
    service = AudioService(api_key="test_key")
    
    # Mock the client methods
    mock_client_instance = MagicMock()
    mock_genai_client.return_value = mock_client_instance
    service.client = mock_client_instance
    
    mock_response = MagicMock()
    mock_response.text = "Transcribed text"
    mock_client_instance.models.generate_content.return_value = mock_response
    
    result = service.generate("Transcribe this", audio_data=b"fake audio", mime_type="audio/wav")
    
    assert result == "Transcribed text"


def test_generate_without_audio_parameters():
    """Test generate method raises error without audio parameters."""
    service = AudioService(api_key="test_key")
    
    with pytest.raises(ValueError, match="requires either 'file_path' or 'audio_data'"):
        service.generate("Transcribe this")
