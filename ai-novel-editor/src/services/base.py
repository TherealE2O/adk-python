"""Base interfaces and abstract classes for services.

This module defines the common interfaces that all services should implement,
providing a consistent API across the application.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseService(ABC):
    """Abstract base class for all services.
    
    Services encapsulate business logic and external integrations,
    providing a clean interface for the rest of the application.
    """
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the service is available and properly configured.
        
        Returns:
            bool: True if service is ready to use, False otherwise
        """
        pass
    
    def validate_configuration(self) -> list[str]:
        """Validate service configuration.
        
        Returns:
            list[str]: List of configuration errors (empty if valid)
        """
        return []


class AIService(BaseService):
    """Abstract base class for AI-powered services.
    
    AI services interact with external LLM APIs and require
    API keys and proper error handling.
    """
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> Any:
        """Generate content using the AI service.
        
        Args:
            prompt: The input prompt for generation
            **kwargs: Additional service-specific parameters
            
        Returns:
            Generated content (type depends on service)
        """
        pass
    
    def get_error_message(self, error: Exception) -> str:
        """Convert an exception to a user-friendly error message.
        
        Args:
            error: The exception that occurred
            
        Returns:
            str: User-friendly error message
        """
        return f"An error occurred: {str(error)}"


class StorageServiceInterface(BaseService):
    """Interface for storage services.
    
    Storage services handle persistence of application data
    to various backends (file system, database, etc.).
    """
    
    @abstractmethod
    def save(self, key: str, data: Any) -> bool:
        """Save data to storage.
        
        Args:
            key: Unique identifier for the data
            data: Data to save
            
        Returns:
            bool: True if save was successful
        """
        pass
    
    @abstractmethod
    def load(self, key: str) -> Optional[Any]:
        """Load data from storage.
        
        Args:
            key: Unique identifier for the data
            
        Returns:
            Loaded data or None if not found
        """
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete data from storage.
        
        Args:
            key: Unique identifier for the data
            
        Returns:
            bool: True if deletion was successful
        """
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if data exists in storage.
        
        Args:
            key: Unique identifier for the data
            
        Returns:
            bool: True if data exists
        """
        pass
    
    @abstractmethod
    def list_keys(self) -> list[str]:
        """List all keys in storage.
        
        Returns:
            list[str]: List of all keys
        """
        pass
