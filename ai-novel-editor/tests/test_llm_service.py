"""Tests for the LLMService."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.services.llm_service import LLMService
from src.config import config


@pytest.fixture
def mock_genai_client():
    """Create a mock Gemini client."""
    with patch('src.services.llm_service.genai.Client') as mock_client:
        yield mock_client


def test_llm_service_initialization_with_api_key(mock_genai_client):
    """Test LLM service initialization with API key."""
    service = LLMService(api_key="test_api_key")
    
    assert service.api_key == "test_api_key"
    assert service.model_name == config.gemini_model
    assert service.is_available() is True


def test_llm_service_initialization_without_api_key():
    """Test LLM service initialization without API key."""
    with patch('src.services.llm_service.config') as mock_config:
        mock_config.google_api_key = None
        mock_config.gemini_model = "gemini-2.0-flash-exp"
        
        service = LLMService()
        
        assert service.is_available() is False


def test_is_available_with_valid_key(mock_genai_client):
    """Test is_available returns True with valid API key."""
    service = LLMService(api_key="valid_key")
    assert service.is_available() is True


def test_is_available_with_empty_key():
    """Test is_available returns False with empty API key."""
    with patch('src.services.llm_service.config') as mock_config:
        mock_config.google_api_key = None
        mock_config.gemini_model = "gemini-2.0-flash-exp"
        service = LLMService(api_key="")
        assert service.is_available() is False


def test_is_available_with_none_key():
    """Test is_available returns False with None API key."""
    with patch('src.services.llm_service.config') as mock_config:
        mock_config.google_api_key = None
        mock_config.gemini_model = "gemini-2.0-flash-exp"
        service = LLMService(api_key=None)
        assert service.is_available() is False


def test_generate_text_without_api_key():
    """Test generate_text raises error when service is not available."""
    with patch('src.services.llm_service.config') as mock_config:
        mock_config.google_api_key = None
        mock_config.gemini_model = "gemini-2.0-flash-exp"
        service = LLMService(api_key=None)
        
        with pytest.raises(ValueError, match="LLM Service is not available"):
            service.generate_text("Test prompt")


def test_generate_with_json_schema_without_api_key():
    """Test generate_with_json_schema raises error when service is not available."""
    with patch('src.services.llm_service.config') as mock_config:
        mock_config.google_api_key = None
        mock_config.gemini_model = "gemini-2.0-flash-exp"
        service = LLMService(api_key=None)
        
        with pytest.raises(ValueError, match="LLM Service is not available"):
            service.generate_with_json_schema("Test prompt", {"type": "object"})


def test_count_tokens():
    """Test token counting approximation."""
    service = LLMService(api_key="test_key")
    
    # Simple approximation: ~4 characters per token
    text = "This is a test string"
    token_count = service.count_tokens(text)
    
    assert token_count == len(text) // 4


def test_build_prompt_with_context():
    """Test building prompt with context."""
    service = LLMService(api_key="test_key")
    
    prompt = "Generate a story"
    context = {
        "characters": "Hero, Villain",
        "setting": "Medieval castle"
    }
    
    full_prompt = service._build_prompt_with_context(prompt, context)
    
    assert "CHARACTERS:" in full_prompt
    assert "Hero, Villain" in full_prompt
    assert "SETTING:" in full_prompt
    assert "Medieval castle" in full_prompt
    assert "Generate a story" in full_prompt


def test_build_prompt_without_context():
    """Test building prompt without context."""
    service = LLMService(api_key="test_key")
    
    prompt = "Generate a story"
    full_prompt = service._build_prompt_with_context(prompt, None)
    
    assert full_prompt == prompt


def test_get_error_message_rate_limit():
    """Test error message for rate limit errors."""
    from google.api_core import exceptions as google_exceptions
    
    service = LLMService(api_key="test_key")
    error = google_exceptions.ResourceExhausted("Rate limit exceeded")
    
    message = service.get_error_message(error)
    
    assert "rate limit" in message.lower()
    assert "wait" in message.lower()


def test_get_error_message_authentication():
    """Test error message for authentication errors."""
    from google.api_core import exceptions as google_exceptions
    
    service = LLMService(api_key="test_key")
    error = google_exceptions.Unauthenticated("Invalid API key")
    
    message = service.get_error_message(error)
    
    assert "authentication" in message.lower()
    assert "GOOGLE_API_KEY" in message


def test_get_error_message_timeout():
    """Test error message for timeout errors."""
    from google.api_core import exceptions as google_exceptions
    
    service = LLMService(api_key="test_key")
    error = google_exceptions.DeadlineExceeded("Request timed out")
    
    message = service.get_error_message(error)
    
    assert "timed out" in message.lower()
    assert "connection" in message.lower()


def test_get_error_message_generic():
    """Test error message for generic errors."""
    service = LLMService(api_key="test_key")
    error = Exception("Something went wrong")
    
    message = service.get_error_message(error)
    
    assert "unexpected error" in message.lower()
    assert "Something went wrong" in message
