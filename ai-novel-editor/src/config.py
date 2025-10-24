"""Configuration management for the AI Novel Editor.

This module handles loading and validating environment variables and
application configuration settings.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Application configuration loaded from environment variables."""
    
    def __init__(self):
        """Initialize configuration by loading environment variables."""
        # Load .env file from the project root
        env_path = Path(__file__).parent.parent / '.env'
        load_dotenv(dotenv_path=env_path)
        
        # API Configuration
        self.google_api_key: Optional[str] = os.getenv('GOOGLE_API_KEY')
        self.gemini_model: str = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
        
        # Storage Configuration
        self.data_path: Path = Path(os.getenv('DATA_PATH', 'data/projects'))
        self.examples_path: Path = self.data_path / 'examples'
        
        # Application Configuration
        self.log_level: str = os.getenv('LOG_LEVEL', 'INFO')
        self.max_audio_duration: int = int(os.getenv('MAX_AUDIO_DURATION', '34200'))  # 9.5 hours in seconds
        
        # LLM Configuration
        self.llm_temperature_creative: float = float(os.getenv('LLM_TEMPERATURE_CREATIVE', '0.7'))
        self.llm_temperature_extraction: float = float(os.getenv('LLM_TEMPERATURE_EXTRACTION', '0.3'))
        self.llm_max_tokens_generation: int = int(os.getenv('LLM_MAX_TOKENS_GENERATION', '8192'))
        self.llm_max_tokens_extraction: int = int(os.getenv('LLM_MAX_TOKENS_EXTRACTION', '2048'))
        
        # Ensure data directories exist
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.examples_path.mkdir(parents=True, exist_ok=True)
    
    def is_api_key_configured(self) -> bool:
        """Check if Google API key is configured.
        
        Returns:
            bool: True if API key is set and not empty
        """
        return bool(self.google_api_key and self.google_api_key.strip())
    
    def validate(self) -> list[str]:
        """Validate configuration and return list of errors.
        
        Returns:
            list[str]: List of validation error messages (empty if valid)
        """
        errors = []
        
        if not self.is_api_key_configured():
            errors.append(
                "GOOGLE_API_KEY not configured. "
                "Please set it in .env file or environment variables."
            )
        
        if not self.data_path.exists():
            errors.append(f"Data path does not exist: {self.data_path}")
        
        return errors


# Global configuration instance
config = Config()
