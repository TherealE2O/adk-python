"""Tests for project setup and configuration."""

import pytest
from pathlib import Path
from src.config import Config, config
from src.services.base import BaseService, AIService, StorageServiceInterface
from src.agents.base import BaseAgent, WorldBuildingAgentInterface, EditingAgentInterface


def test_config_initialization():
    """Test that configuration initializes correctly."""
    test_config = Config()
    assert test_config is not None
    assert hasattr(test_config, 'google_api_key')
    assert hasattr(test_config, 'gemini_model')
    assert hasattr(test_config, 'data_path')


def test_config_api_key_check():
    """Test API key configuration check."""
    test_config = Config()
    # Should return bool
    result = test_config.is_api_key_configured()
    assert isinstance(result, bool)


def test_config_validation():
    """Test configuration validation."""
    test_config = Config()
    errors = test_config.validate()
    assert isinstance(errors, list)


def test_config_directories_exist():
    """Test that required directories are created."""
    test_config = Config()
    assert test_config.data_path.exists()
    assert test_config.examples_path.exists()


def test_global_config_instance():
    """Test that global config instance is available."""
    assert config is not None
    assert isinstance(config, Config)


def test_base_service_interface():
    """Test that BaseService interface is properly defined."""
    assert hasattr(BaseService, 'is_available')
    assert hasattr(BaseService, 'validate_configuration')


def test_ai_service_interface():
    """Test that AIService interface is properly defined."""
    assert hasattr(AIService, 'generate')
    assert hasattr(AIService, 'get_error_message')
    assert issubclass(AIService, BaseService)


def test_storage_service_interface():
    """Test that StorageServiceInterface is properly defined."""
    assert hasattr(StorageServiceInterface, 'save')
    assert hasattr(StorageServiceInterface, 'load')
    assert hasattr(StorageServiceInterface, 'delete')
    assert hasattr(StorageServiceInterface, 'exists')
    assert hasattr(StorageServiceInterface, 'list_keys')
    assert issubclass(StorageServiceInterface, BaseService)


def test_base_agent_interface():
    """Test that BaseAgent interface is properly defined."""
    assert hasattr(BaseAgent, 'is_ready')
    assert hasattr(BaseAgent, 'get_context')


def test_worldbuilding_agent_interface():
    """Test that WorldBuildingAgentInterface is properly defined."""
    assert hasattr(WorldBuildingAgentInterface, 'initialize_question_tree')
    assert hasattr(WorldBuildingAgentInterface, 'generate_follow_up_questions')
    assert hasattr(WorldBuildingAgentInterface, 'answer_question')
    assert hasattr(WorldBuildingAgentInterface, 'extract_entities')
    assert issubclass(WorldBuildingAgentInterface, BaseAgent)


def test_editing_agent_interface():
    """Test that EditingAgentInterface is properly defined."""
    assert hasattr(EditingAgentInterface, 'improve_text')
    assert hasattr(EditingAgentInterface, 'expand_text')
    assert hasattr(EditingAgentInterface, 'rephrase_text')
    assert hasattr(EditingAgentInterface, 'suggest_next_chapter')
    assert hasattr(EditingAgentInterface, 'create_editing_prompt')
    assert issubclass(EditingAgentInterface, BaseAgent)


def test_directory_structure():
    """Test that all required directories exist."""
    base_path = Path(__file__).parent.parent
    
    # Check main directories
    assert (base_path / 'src').exists()
    assert (base_path / 'src' / 'models').exists()
    assert (base_path / 'src' / 'services').exists()
    assert (base_path / 'src' / 'agents').exists()
    assert (base_path / 'src' / 'ui').exists()
    assert (base_path / 'tests').exists()
    assert (base_path / 'data' / 'projects').exists()
    
    # Check key files
    assert (base_path / 'src' / '__init__.py').exists()
    assert (base_path / 'src' / 'config.py').exists()
    assert (base_path / 'src' / 'services' / 'base.py').exists()
    assert (base_path / 'src' / 'agents' / 'base.py').exists()
    assert (base_path / '.env.example').exists()
