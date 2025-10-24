"""Tests for the StorageService."""

import json
import tempfile
from pathlib import Path

import pytest

from src.models.project import Project, Chapter
from src.models.truth import TruthKnowledgeBase, Character
from src.services.storage import StorageService, StorageError


@pytest.fixture
def temp_storage():
  """Create a temporary storage service for testing."""
  with tempfile.TemporaryDirectory() as tmpdir:
    storage = StorageService(base_path=tmpdir)
    yield storage


@pytest.fixture
def sample_project():
  """Create a sample project for testing."""
  project = Project(
    title="Test Novel",
    description="A test novel project",
    author="Test Author",
    genre="Fantasy"
  )
  
  # Add a chapter
  chapter = Chapter(number=1, title="Chapter One", content="Once upon a time...")
  chapter.update_word_count()
  project.add_chapter(chapter)
  
  # Add a character to Truth
  character = Character(name="Hero", description="The main character")
  project.truth.add_character(character)
  
  return project


def test_save_and_load_project(temp_storage, sample_project):
  """Test saving and loading a project."""
  # Save the project
  temp_storage.save_project(sample_project)
  
  # Load the project
  loaded_project = temp_storage.load_project(sample_project.id)
  
  assert loaded_project is not None
  assert loaded_project.title == sample_project.title
  assert loaded_project.author == sample_project.author
  assert len(loaded_project.chapters) == 1
  assert len(loaded_project.truth.characters) == 1


def test_project_exists(temp_storage, sample_project):
  """Test checking if a project exists."""
  # Project doesn't exist yet
  assert not temp_storage.project_exists(sample_project.id)
  
  # Save the project
  temp_storage.save_project(sample_project)
  
  # Now it exists
  assert temp_storage.project_exists(sample_project.id)


def test_list_projects(temp_storage, sample_project):
  """Test listing projects."""
  # Initially empty
  projects = temp_storage.list_projects()
  assert len(projects) == 0
  
  # Save a project
  temp_storage.save_project(sample_project)
  
  # Now we have one project
  projects = temp_storage.list_projects()
  assert len(projects) == 1
  assert projects[0].title == sample_project.title


def test_delete_project(temp_storage, sample_project):
  """Test deleting a project."""
  # Save the project
  temp_storage.save_project(sample_project)
  assert temp_storage.project_exists(sample_project.id)
  
  # Delete the project
  result = temp_storage.delete_project(sample_project.id)
  assert result is True
  assert not temp_storage.project_exists(sample_project.id)
  
  # Try to delete non-existent project
  result = temp_storage.delete_project("nonexistent")
  assert result is False


def test_example_projects(temp_storage, sample_project):
  """Test example project handling."""
  # Mark as example
  sample_project.is_example = True
  
  # Save the example project
  temp_storage.save_project(sample_project)
  
  # List example projects
  examples = temp_storage.list_example_projects()
  assert len(examples) == 1
  assert examples[0].is_example is True
  
  # Regular list should not include examples
  projects = temp_storage.list_projects(include_examples=False)
  assert len(projects) == 0
  
  # But can include them if requested
  all_projects = temp_storage.list_projects(include_examples=True)
  assert len(all_projects) == 1


def test_load_nonexistent_project(temp_storage):
  """Test loading a project that doesn't exist."""
  project = temp_storage.load_project("nonexistent")
  assert project is None


def test_corrupted_project_file(temp_storage, sample_project):
  """Test handling of corrupted project files."""
  # Save a valid project
  temp_storage.save_project(sample_project)
  
  # Corrupt the file
  project_file = Path(temp_storage.base_path) / sample_project.id / "project.json"
  with open(project_file, 'w') as f:
    f.write("{ invalid json }")
  
  # Try to load it
  with pytest.raises(StorageError):
    temp_storage.load_project(sample_project.id)
