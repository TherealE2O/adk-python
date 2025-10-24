"""LLM Service for interacting with Google Gemini API.

This module provides a wrapper around the Google Gemini API for text generation
and structured data extraction, with proper error handling and retry logic.
"""

import time
import logging
from typing import Any, Optional, Dict
from google import genai
from google.genai import types
from google.api_core import exceptions as google_exceptions

from .base import AIService
from ..config import config


logger = logging.getLogger(__name__)


class LLMService(AIService):
    """Service for interacting with Google Gemini LLM API.
    
    Provides methods for general text generation and structured extraction
    with JSON schema validation. Includes error handling and retry logic
    for robust API interactions.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the LLM service.
        
        Args:
            api_key: Google API key. If None, uses config.google_api_key
        """
        self.api_key = api_key or config.google_api_key
        self.model_name = config.gemini_model
        self.client: Optional[genai.Client] = None
        
        if self.is_available():
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info(f"LLM Service initialized with model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                self.client = None
    
    def is_available(self) -> bool:
        """Check if the LLM service is available.
        
        Returns:
            bool: True if API key is configured and client can be initialized
        """
        return bool(self.api_key and self.api_key.strip())
    
    def generate_text(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate text using the Gemini API.
        
        Args:
            prompt: The input prompt for text generation
            context: Optional context dictionary to include in the prompt
            temperature: Sampling temperature (0.0-1.0). Defaults to creative temperature
            max_tokens: Maximum tokens to generate. Defaults to generation max
            
        Returns:
            str: Generated text
            
        Raises:
            ValueError: If service is not available
            RuntimeError: If API call fails after retries
        """
        if not self.is_available() or not self.client:
            raise ValueError("LLM Service is not available. Please configure GOOGLE_API_KEY.")
        
        # Use default temperature for creative tasks
        if temperature is None:
            temperature = config.llm_temperature_creative
        
        if max_tokens is None:
            max_tokens = config.llm_max_tokens_generation
        
        # Build full prompt with context if provided
        full_prompt = self._build_prompt_with_context(prompt, context)
        
        # Generate with retry logic
        return self._generate_with_retry(
            prompt=full_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    def generate_with_json_schema(
        self,
        prompt: str,
        schema: Dict[str, Any],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate structured data using JSON schema validation.
        
        Args:
            prompt: The input prompt for extraction
            schema: JSON schema defining the expected output structure
            temperature: Sampling temperature. Defaults to extraction temperature
            max_tokens: Maximum tokens to generate. Defaults to extraction max
            
        Returns:
            dict: Extracted structured data matching the schema
            
        Raises:
            ValueError: If service is not available
            RuntimeError: If API call fails after retries
        """
        if not self.is_available() or not self.client:
            raise ValueError("LLM Service is not available. Please configure GOOGLE_API_KEY.")
        
        # Use lower temperature for structured extraction
        if temperature is None:
            temperature = config.llm_temperature_extraction
        
        if max_tokens is None:
            max_tokens = config.llm_max_tokens_extraction
        
        # Generate with schema and retry logic
        return self._generate_with_schema_retry(
            prompt=prompt,
            schema=schema,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate content using the AI service (implements AIService interface).
        
        Args:
            prompt: The input prompt for generation
            **kwargs: Additional parameters (context, temperature, max_tokens)
            
        Returns:
            str: Generated text
        """
        return self.generate_text(prompt, **kwargs)
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in a text string.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            int: Approximate token count
        """
        # Simple approximation: ~4 characters per token
        # For more accurate counting, use the Gemini API's token counting endpoint
        return len(text) // 4
    
    def _build_prompt_with_context(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Build a full prompt including context information.
        
        Args:
            prompt: Base prompt
            context: Optional context dictionary
            
        Returns:
            str: Full prompt with context
        """
        if not context:
            return prompt
        
        context_parts = []
        for key, value in context.items():
            if value:
                context_parts.append(f"{key.upper()}:\n{value}\n")
        
        if context_parts:
            context_str = "\n".join(context_parts)
            return f"{context_str}\n{prompt}"
        
        return prompt
    
    def _generate_with_retry(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        max_retries: int = 3
    ) -> str:
        """Generate text with exponential backoff retry logic.
        
        Args:
            prompt: The prompt to generate from
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            max_retries: Maximum number of retry attempts
            
        Returns:
            str: Generated text
            
        Raises:
            RuntimeError: If all retries fail
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens
                    )
                )
                
                if response.text:
                    # Log successful retry if this wasn't the first attempt
                    if attempt > 0:
                        logger.info(f"Successfully generated text after {attempt + 1} attempts")
                    return response.text
                else:
                    raise RuntimeError("Empty response from API")
                    
            except google_exceptions.ResourceExhausted as e:
                # Rate limit error - retry with exponential backoff
                last_error = e
                wait_time = (2 ** attempt) * 2  # 2s, 4s, 8s
                logger.warning(
                    f"Rate limit hit (attempt {attempt + 1}/{max_retries}). "
                    f"Retrying in {wait_time}s..."
                )
                if attempt < max_retries - 1:  # Don't sleep on last attempt
                    time.sleep(wait_time)
                
            except google_exceptions.Unauthenticated as e:
                # Authentication error - don't retry
                logger.error(f"Authentication failed: {e}")
                raise ValueError(
                    "Invalid API key. Please check your GOOGLE_API_KEY configuration."
                ) from e
                
            except google_exceptions.DeadlineExceeded as e:
                # Timeout error - retry with longer wait
                last_error = e
                wait_time = (2 ** attempt) * 1.5  # 1.5s, 3s, 6s
                logger.warning(
                    f"Request timeout (attempt {attempt + 1}/{max_retries}). "
                    f"Retrying in {wait_time}s..."
                )
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                
            except google_exceptions.ServiceUnavailable as e:
                # Service unavailable - retry
                last_error = e
                wait_time = (2 ** attempt) * 3  # 3s, 6s, 12s
                logger.warning(
                    f"Service unavailable (attempt {attempt + 1}/{max_retries}). "
                    f"Retrying in {wait_time}s..."
                )
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                
            except Exception as e:
                # Other errors - log and raise
                logger.error(f"Unexpected error during generation: {e}")
                raise RuntimeError(f"Failed to generate text: {str(e)}") from e
        
        # All retries exhausted
        error_msg = self.get_error_message(last_error)
        logger.error(f"All retries exhausted. Last error: {error_msg}")
        raise RuntimeError(f"Failed to generate text after {max_retries} attempts: {error_msg}")
    
    def _generate_with_schema_retry(
        self,
        prompt: str,
        schema: Dict[str, Any],
        temperature: float,
        max_tokens: int,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """Generate structured data with retry logic.
        
        Args:
            prompt: The prompt to generate from
            schema: JSON schema for output validation
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            max_retries: Maximum number of retry attempts
            
        Returns:
            dict: Extracted structured data
            
        Raises:
            RuntimeError: If all retries fail
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens,
                        response_mime_type="application/json",
                        response_schema=schema
                    )
                )
                
                if response.text:
                    import json
                    result = json.loads(response.text)
                    # Log successful retry if this wasn't the first attempt
                    if attempt > 0:
                        logger.info(f"Successfully generated structured data after {attempt + 1} attempts")
                    return result
                else:
                    raise RuntimeError("Empty response from API")
                    
            except google_exceptions.ResourceExhausted as e:
                # Rate limit error - retry with exponential backoff
                last_error = e
                wait_time = (2 ** attempt) * 2  # 2s, 4s, 8s
                logger.warning(
                    f"Rate limit hit (attempt {attempt + 1}/{max_retries}). "
                    f"Retrying in {wait_time}s..."
                )
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                
            except google_exceptions.Unauthenticated as e:
                # Authentication error - don't retry
                logger.error(f"Authentication failed: {e}")
                raise ValueError(
                    "Invalid API key. Please check your GOOGLE_API_KEY configuration."
                ) from e
                
            except google_exceptions.DeadlineExceeded as e:
                # Timeout error - retry with longer wait
                last_error = e
                wait_time = (2 ** attempt) * 1.5  # 1.5s, 3s, 6s
                logger.warning(
                    f"Request timeout (attempt {attempt + 1}/{max_retries}). "
                    f"Retrying in {wait_time}s..."
                )
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                
            except google_exceptions.ServiceUnavailable as e:
                # Service unavailable - retry
                last_error = e
                wait_time = (2 ** attempt) * 3  # 3s, 6s, 12s
                logger.warning(
                    f"Service unavailable (attempt {attempt + 1}/{max_retries}). "
                    f"Retrying in {wait_time}s..."
                )
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                
            except json.JSONDecodeError as e:
                # JSON parsing error - retry
                last_error = e
                logger.warning(
                    f"Failed to parse JSON response (attempt {attempt + 1}/{max_retries}). Retrying..."
                )
                if attempt < max_retries - 1:
                    time.sleep(1)
                
            except Exception as e:
                # Other errors - log and raise
                logger.error(f"Unexpected error during structured generation: {e}")
                raise RuntimeError(f"Failed to generate structured data: {str(e)}") from e
        
        # All retries exhausted
        error_msg = self.get_error_message(last_error)
        logger.error(f"All retries exhausted. Last error: {error_msg}")
        raise RuntimeError(
            f"Failed to generate structured data after {max_retries} attempts: {error_msg}"
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
                "API rate limit exceeded. The system has automatically retried your request. "
                "Please wait a moment before trying again. "
                "If this persists, consider upgrading your API quota."
            )
        elif isinstance(error, google_exceptions.Unauthenticated):
            return (
                "Authentication failed. Please check that your GOOGLE_API_KEY "
                "is valid and has not expired."
            )
        elif isinstance(error, google_exceptions.DeadlineExceeded):
            return (
                "Request timed out after multiple attempts. Please check your internet connection "
                "and try again. If the problem persists, try a shorter prompt or reduce the complexity."
            )
        elif isinstance(error, google_exceptions.ServiceUnavailable):
            return (
                "The AI service is temporarily unavailable. The system has automatically retried. "
                "Please wait a few moments and try again."
            )
        elif isinstance(error, ValueError):
            return str(error)
        else:
            return f"An unexpected error occurred: {str(error)}"
