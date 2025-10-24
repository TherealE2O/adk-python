"""Tests for ProjectManager service."""

import pytest
from pathlib import Path
import tempfile
import shutil

from src.services.project_manager import ProjectManager, ProjectManagerError
from src.services.storage import StorageService
from src.models.project import Project, Chapter
from src.models.truth import TruthKnowledgeBase


@pytest.fixture
def temp_storage_dir():
  """Create a temporary directory for test storage."""
  temp_dir = tempfile.mkdtemp()
  yield temp_dir
  shutil.rmtree(temp_dir)


@pytest.fixture
def storage_service(temp_storage_dir):
  """Create a storage service with temporary directory."""
  return StorageService(base_path=temp_storage_dir)


@pytest.fixture
def project_manager(storage_service):
  """Create a project manager instance."""
  return ProjectManager(storage=storage_service)


class TestProjectLifecycle:
  """Tests for project lifecycle management."""
  
  def test_create_project(self, project_manager):
    """Test creating a new project."""
    project = project_manager.create_project(
        title="Test Novel",
        description="A test novel",
        author="Test Author",
        genre="Fantasy"
    )
    
    assert project is not None
    assert project.title == "Test Novel"
    assert project.description == "A test novel"
    assert project.author == "Test Author"
    assert project.genre == "Fantasy"
    assert isinstance(project.truth, TruthKnowledgeBase)
    assert len(project.chapters) == 0
    assert project.is_example is False
    assert project_manager.current_project == project
  
  def test_create_project_minimal(self, project_manager):
    """Test creating a project with only title."""
    project = project_manager.create_project(title="Minimal Novel")
    
    assert project is not None
    assert project.title == "Minimal Novel"
    assert project.description == ""
    assert project.author == ""
    assert project.genre == ""
  
  def test_list_all_projects_empty(self, project_manager):
    """Test listing projects when none exist."""
    projects = project_manager.list_all_projects()
    assert projects == []
  
  def test_list_all_projects_with_saved(self, project_manager):
    """Test listing projects after saving."""
    # Create and save a project
    project = project_manager.create_project(title="Novel 1")
    project_manager.save_current_project()
    
    # List all projects
    projects = project_manager.list_all_projects()
    assert len(projects) == 1
    assert projects[0].title == "Novel 1"
  
  def test_get_example_projects_empty(self, project_manager):
    """Test getting example projects when none exist."""
    examples = project_manager.get_example_projects()
    assert examples == []
  
  def test_delete_project(self, project_manager):
    """Test deleting a project."""
    # Create and save a project
    project = project_manager.create_project(title="To Delete")
    project_manager.save_current_project()
    project_id = project.id
    
    # Delete the project
    success = project_manager.delete_project(project_id)
    assert success is True
    assert project_manager.current_project is None
    
    # Verify it's gone
    projects = project_manager.list_all_projects()
    assert len(projects) == 0
  
  def test_delete_nonexistent_project(self, project_manager):
    """Test deleting a project that doesn't exist."""
    success = project_manager.delete_project("nonexistent_id")
    assert success is False
  
  def test_load_project(self, project_manager):
    """Test loading a saved project."""
    # Create and save a project
    project = project_manager.create_project(
        title="Load Test",
        author="Test Author"
    )
    project_id = project.id
    project_manager.save_current_project()
    
    # Clear current project
    project_manager.current_project = None
    
    # Load the project
    loaded = project_manager.load_project(project_id)
    assert loaded is not None
    assert loaded.title == "Load Test"
    assert loaded.author == "Test Author"
    assert project_manager.current_project == loaded
  
  def test_load_nonexistent_project(self, project_manager):
    """Test loading a project that doesn't exist."""
    loaded = project_manager.load_project("nonexistent_id")
    assert loaded is None


class TestChapterManagement:
  """Tests for chapter management."""
  
  def test_add_chapter(self, project_manager):
    """Test adding a chapter to current project."""
    # Create a project
    project_manager.create_project(title="Chapter Test")
    
    # Add a chapter
    chapter = project_manager.add_chapter(number=1, title="Chapter One")
    
    assert chapter is not None
    assert chapter.number == 1
    assert chapter.title == "Chapter One"
    assert chapter.content == ""
    assert chapter.word_count == 0
    assert chapter.id in project_manager.current_project.chapters
  
  def test_add_chapter_no_current_project(self, project_manager):
    """Test adding a chapter when no project is loaded."""
    with pytest.raises(ProjectManagerError, match="No current project"):
      project_manager.add_chapter(number=1, title="Chapter One")
  
  def test_update_chapter_content(self, project_manager):
    """Test updating chapter content."""
    # Create project and chapter
    project_manager.create_project(title="Update Test")
    chapter = project_manager.add_chapter(number=1, title="Chapter One")
    
    # Update content
    new_content = "This is the new chapter content with multiple words."
    project_manager.update_chapter_content(chapter.id, new_content)
    
    # Verify update
    updated_chapter = project_manager.current_project.chapters[chapter.id]
    assert updated_chapter.content == new_content
    assert updated_chapter.word_count == 9
  
  def test_update_chapter_content_no_project(self, project_manager):
    """Test updating chapter content when no project is loaded."""
    with pytest.raises(ProjectManagerError, match="No current project"):
      project_manager.update_chapter_content("chapter_id", "content")
  
  def test_update_chapter_content_invalid_chapter(self, project_manager):
    """Test updating content for non-existent chapter."""
    project_manager.create_project(title="Invalid Chapter Test")
    
    with pytest.raises(ProjectManagerError, match="Chapter not found"):
      project_manager.update_chapter_content("invalid_id", "content")
  
  def test_save_current_project(self, project_manager):
    """Test saving the current project."""
    # Create project with chapter
    project_manager.create_project(title="Save Test")
    project_manager.add_chapter(number=1, title="Chapter One")
    
    # Save project
    project_manager.save_current_project()
    
    # Verify it was saved by loading it
    project_id = project_manager.current_project.id
    project_manager.current_project = None
    
    loaded = project_manager.load_project(project_id)
    assert loaded is not None
    assert loaded.title == "Save Test"
    assert len(loaded.chapters) == 1
  
  def test_save_current_project_no_project(self, project_manager):
    """Test saving when no project is loaded."""
    with pytest.raises(ProjectManagerError, match="No current project"):
      project_manager.save_current_project()


class TestIntegration:
  """Integration tests for complete workflows."""
  
  def test_full_project_workflow(self, project_manager):
    """Test complete project creation, editing, and saving workflow."""
    # Create project
    project = project_manager.create_project(
        title="Full Workflow Test",
        author="Test Author",
        genre="Sci-Fi"
    )
    
    # Add chapters
    chapter1 = project_manager.add_chapter(1, "The Beginning")
    chapter2 = project_manager.add_chapter(2, "The Middle")
    
    # Update chapter content
    project_manager.update_chapter_content(
        chapter1.id,
        "This is the beginning of the story."
    )
    project_manager.update_chapter_content(
        chapter2.id,
        "The story continues here."
    )
    
    # Save project
    project_manager.save_current_project()
    
    # Load and verify
    project_id = project.id
    project_manager.current_project = None
    
    loaded = project_manager.load_project(project_id)
    assert loaded.title == "Full Workflow Test"
    assert len(loaded.chapters) == 2
    
    sorted_chapters = loaded.get_sorted_chapters()
    assert sorted_chapters[0].title == "The Beginning"
    assert sorted_chapters[1].title == "The Middle"
    assert sorted_chapters[0].word_count == 7
    assert sorted_chapters[1].word_count == 4
