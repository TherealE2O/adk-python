"""Audio Service for transcription using Google Gemini Audio API.

This module provides audio transcription capabilities using Gemini's native
audio understanding, with proper error handling and retry logic.
"""

import time
import logging
from pathlib import Path
from typing import Optional
from google import genai
from google.genai import types
from google.api_core import exceptions as google_exceptions

from .base import AIService
from ..config import config


logger = logging.getLogger(__name__)


class AudioService(AIService):
    """Service for audio transcription using Google Gemini Audio API.
    
    Provides methods for transcribing audio from files and byte data,
    with support for multiple audio formats and proper error handling.
    """
    
    # Supported audio formats with their MIME types
    SUPPORTED_FORMATS = {
        'mp3': 'audio/mp3',
        'wav': 'audio/wav',
        'flac': 'audio/flac',
        'ogg': 'audio/ogg',
        'webm': 'audio/webm',
        'aiff': 'audio/aiff',
        'aac': 'audio/aac',
    }
    
    # Maximum file size (20 MB)
    MAX_FILE_SIZE = 20 * 1024 * 1024
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Audio service.
        
        Args:
            api_key: Google API key. If None, uses config.google_api_key
        """
        self.api_key = api_key or config.google_api_key
        self.model_name = config.gemini_model
        self.client: Optional[genai.Client] = None
        
        if self.is_available():
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info(f"Audio Service initialized with model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                self.client = None
    
    def is_available(self) -> bool:
        """Check if the Audio service is available.
        
        Returns:
            bool: True if API key is configured and client can be initialized
        """
        return bool(self.api_key and self.api_key.strip())
  
    def transcribe_file(
        self,
        file_path: str,
        prompt: str = "Generate a transcript of the speech."
    ) -> str:
        """Transcribe an audio file using Gemini.
        
        Args:
            file_path: Path to the audio file
            prompt: Custom prompt for transcription
            
        Returns:
            str: Transcribed text
            
        Raises:
            ValueError: If service is not available or file validation fails
            RuntimeError: If transcription fails after retries
        """
        if not self.is_available() or not self.client:
            raise ValueError("Audio Service is not available. Please configure GOOGLE_API_KEY.")
        
        # Validate file
        self._validate_audio_file(file_path)
        
        # Transcribe with retry logic
        return self._transcribe_file_with_retry(file_path, prompt)
    
    def transcribe_audio(
        self,
        audio_data: bytes,
        mime_type: str = "audio/wav",
        prompt: str = "Generate a transcript of the speech."
    ) -> str:
        """Transcribe audio data from bytes using Gemini.
        
        Args:
            audio_data: Audio data as bytes
            mime_type: MIME type of the audio (e.g., 'audio/wav', 'audio/mp3')
            prompt: Custom prompt for transcription
            
        Returns:
            str: Transcribed text
            
        Raises:
            ValueError: If service is not available or data validation fails
            RuntimeError: If transcription fails after retries
        """
        if not self.is_available() or not self.client:
            raise ValueError("Audio Service is not available. Please configure GOOGLE_API_KEY.")
        
        # Validate audio data
        self._validate_audio_data(audio_data, mime_type)
        
        # Transcribe with retry logic
        return self._transcribe_bytes_with_retry(audio_data, mime_type, prompt)
  
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate content using the AI service (implements AIService interface).
        
        This method is provided for interface compatibility but audio transcription
        requires audio data, so use transcribe_file() or transcribe_audio() instead.
        
        Args:
            prompt: The input prompt (not used for audio)
            **kwargs: Additional parameters (should include 'file_path' or 'audio_data')
            
        Returns:
            str: Transcribed text
            
        Raises:
            ValueError: If required audio parameters are missing
        """
        if 'file_path' in kwargs:
            return self.transcribe_file(kwargs['file_path'], prompt)
        elif 'audio_data' in kwargs:
            mime_type = kwargs.get('mime_type', 'audio/wav')
            return self.transcribe_audio(kwargs['audio_data'], mime_type, prompt)
        else:
            raise ValueError(
                "Audio transcription requires either 'file_path' or 'audio_data' parameter"
            )
  
    def _validate_audio_file(self, file_path: str) -> None:
        """Validate an audio file.
        
        Args:
            file_path: Path to the audio file
            
        Raises:
            ValueError: If file validation fails
        """
        path = Path(file_path)
        
        # Check if file exists
        if not path.exists():
            raise ValueError(f"Audio file not found: {file_path}")
        
        # Check if file is empty
        file_size = path.stat().st_size
        if file_size == 0:
            raise ValueError(f"Audio file is empty: {file_path}")
        
        # Check file size limit
        if file_size > self.MAX_FILE_SIZE:
            size_mb = file_size / (1024 * 1024)
            raise ValueError(
                f"Audio file too large: {size_mb:.1f} MB. "
                f"Maximum size is {self.MAX_FILE_SIZE / (1024 * 1024):.0f} MB."
            )
        
        # Check file format
        extension = path.suffix.lower().lstrip('.')
        if extension not in self.SUPPORTED_FORMATS:
            supported = ', '.join(self.SUPPORTED_FORMATS.keys())
            raise ValueError(
                f"Unsupported audio format: {extension}. "
                f"Supported formats: {supported}"
            )
        
        logger.info(f"Audio file validated: {file_path} ({file_size / 1024:.1f} KB)")
    
    def _validate_audio_data(self, audio_data: bytes, mime_type: str) -> None:
        """Validate audio data.
        
        Args:
            audio_data: Audio data as bytes
            mime_type: MIME type of the audio
            
        Raises:
            ValueError: If data validation fails
        """
        # Check if data is empty
        if not audio_data or len(audio_data) == 0:
            raise ValueError("Audio data is empty")
        
        # Check data size limit
        if len(audio_data) > self.MAX_FILE_SIZE:
            size_mb = len(audio_data) / (1024 * 1024)
            raise ValueError(
                f"Audio data too large: {size_mb:.1f} MB. "
                f"Maximum size is {self.MAX_FILE_SIZE / (1024 * 1024):.0f} MB."
            )
        
        # Check MIME type
        if mime_type not in self.SUPPORTED_FORMATS.values():
            supported = ', '.join(self.SUPPORTED_FORMATS.values())
            raise ValueError(
                f"Unsupported MIME type: {mime_type}. "
                f"Supported types: {supported}"
            )
        
        logger.info(f"Audio data validated: {len(audio_data) / 1024:.1f} KB, {mime_type}")
    
    def _transcribe_file_with_retry(
        self,
        file_path: str,
        prompt: str,
        max_retries: int = 3
    ) -> str:
        """Transcribe an audio file with retry logic.
        
        Args:
            file_path: Path to the audio file
            prompt: Transcription prompt
            max_retries: Maximum number of retry attempts
            
        Returns:
            str: Transcribed text
            
        Raises:
            RuntimeError: If all retries fail
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Uploading audio file: {file_path}")
                audio_file = self.client.files.upload(file=file_path)
                
                logger.info(f"Transcribing audio with Gemini...")
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[prompt, audio_file]
                )
                
                if response and response.text:
                    logger.info(f"Transcription successful ({len(response.text)} characters)")
                    return response.text
                else:
                    raise RuntimeError("Empty response from API")
                    
            except google_exceptions.ResourceExhausted as e:
                # Rate limit error - retry with exponential backoff
                last_error = e
                wait_time = (2 ** attempt) * 1
                logger.warning(
                    f"Rate limit hit (attempt {attempt + 1}/{max_retries}). "
                    f"Retrying in {wait_time}s..."
                )
                time.sleep(wait_time)
                
            except google_exceptions.Unauthenticated as e:
                # Authentication error - don't retry
                logger.error(f"Authentication failed: {e}")
                raise ValueError(
                    "Invalid API key. Please check your GOOGLE_API_KEY configuration."
                ) from e
                
            except google_exceptions.DeadlineExceeded as e:
                # Timeout error - retry
                last_error = e
                logger.warning(
                    f"Request timeout (attempt {attempt + 1}/{max_retries}). Retrying..."
                )
                time.sleep(1)
                
            except Exception as e:
                # Other errors - log and raise
                logger.error(f"Unexpected error during transcription: {e}")
                raise RuntimeError(f"Failed to transcribe audio: {str(e)}") from e
        
        # All retries exhausted
        error_msg = self.get_error_message(last_error)
        logger.error(f"All retries exhausted. Last error: {error_msg}")
        raise RuntimeError(
            f"Failed to transcribe audio after {max_retries} attempts: {error_msg}"
        )
    
    def _transcribe_bytes_with_retry(
        self,
        audio_data: bytes,
        mime_type: str,
        prompt: str,
        max_retries: int = 3
    ) -> str:
        """Transcribe audio bytes with retry logic.
        
        Args:
            audio_data: Audio data as bytes
            mime_type: MIME type of the audio
            prompt: Transcription prompt
            max_retries: Maximum number of retry attempts
            
        Returns:
            str: Transcribed text
            
        Raises:
            RuntimeError: If all retries fail
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Create audio part from bytes
                audio_part = types.Part.from_bytes(
                    data=audio_data,
                    mime_type=mime_type
                )
                
                logger.info(f"Transcribing audio bytes with Gemini...")
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[prompt, audio_part]
                )
                
                if response and response.text:
                    logger.info(f"Transcription successful ({len(response.text)} characters)")
                    return response.text
                else:
                    raise RuntimeError("Empty response from API")
                    
            except google_exceptions.ResourceExhausted as e:
                # Rate limit error - retry with exponential backoff
                last_error = e
                wait_time = (2 ** attempt) * 1
                logger.warning(
                    f"Rate limit hit (attempt {attempt + 1}/{max_retries}). "
                    f"Retrying in {wait_time}s..."
                )
                time.sleep(wait_time)
                
            except google_exceptions.Unauthenticated as e:
                # Authentication error - don't retry
                logger.error(f"Authentication failed: {e}")
                raise ValueError(
                    "Invalid API key. Please check your GOOGLE_API_KEY configuration."
                ) from e
                
            except google_exceptions.DeadlineExceeded as e:
                # Timeout error - retry
                last_error = e
                logger.warning(
                    f"Request timeout (attempt {attempt + 1}/{max_retries}). Retrying..."
                )
                time.sleep(1)
                
            except Exception as e:
                # Other errors - log and raise
                logger.error(f"Unexpected error during transcription: {e}")
                raise RuntimeError(f"Failed to transcribe audio: {str(e)}") from e
        
        # All retries exhausted
        error_msg = self.get_error_message(last_error)
        logger.error(f"All retries exhausted. Last error: {error_msg}")
        raise RuntimeError(
            f"Failed to transcribe audio after {max_retries} attempts: {error_msg}"
        )
    
    def get_error_message(self, error: Exception) -> str:
        """Convert an exception to a user-friendly error message.
        
        Args:
            error: The exception that occurred
            
        Returns:
            str: User-friendly error message
        """
        if isinstance(error, google_exceptions.ResourceExhausted):
            return (
                "API rate limit exceeded. Please wait a moment and try again. "
                "If this persists, consider upgrading your API quota."
            )
        elif isinstance(error, google_exceptions.Unauthenticated):
            return (
                "Authentication failed. Please check that your GOOGLE_API_KEY "
                "is valid and has not expired."
            )
        elif isinstance(error, google_exceptions.DeadlineExceeded):
            return (
                "Request timed out. Please check your internet connection "
                "and try again. Large audio files may take longer to process."
            )
        elif isinstance(error, ValueError):
            return str(error)
        else:
            return f"An unexpected error occurred: {str(error)}"
    
    @staticmethod
    def get_supported_formats() -> dict[str, str]:
        """Get supported audio formats.
        
        Returns:
            dict: Dictionary mapping format extensions to MIME types
        """
        return AudioService.SUPPORTED_FORMATS.copy()
    
    @staticmethod
    def get_max_duration_seconds() -> int:
        """Get maximum supported audio duration.
        
        Returns:
            int: Maximum duration in seconds (from config)
        """
        return config.max_audio_duration
    
    @staticmethod
    def estimate_tokens_from_duration(duration_seconds: float) -> int:
        """Estimate token count from audio duration.
        
        Gemini represents each second of audio as 32 tokens.
        
        Args:
            duration_seconds: Audio duration in seconds
            
        Returns:
            int: Estimated token count
        """
        return int(duration_seconds * 32)
