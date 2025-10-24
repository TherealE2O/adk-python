"""Project manager service for managing novel projects."""

from __future__ import annotations

import logging
from typing import Optional

from ..models.project import Project, Chapter
from ..models.truth import TruthKnowledgeBase
from .storage import StorageService, StorageError


logger = logging.getLogger(__name__)


class ProjectManagerError(Exception):
  """Base exception for project manager errors."""
  pass


class ProjectManager:
  """Manages project lifecycle and operations.
  
  Provides high-level business logic for creating, loading, and managing
  novel projects including chapter management and persistence.
  """
  
  def __init__(self, storage: StorageService):
    """Initialize the project manager.
    
    Args:
      storage: The storage service for persisting projects.
    """
    self.storage = storage
    self.current_project: Optional[Project] = None
    logger.info("ProjectManager initialized")
  
  def create_project(
      self,
      title: str,
      description: str = "",
      author: str = "",
      genre: str = ""
  ) -> Project:
    """Create a new project with empty Truth knowledge base.
    
    Initializes a new Project with the provided metadata and an empty
    TruthKnowledgeBase. The project is not automatically saved.
    
    Args:
      title: The title of the novel.
      description: A brief description of the novel.
      author: The author's name.
      genre: The genre of the novel.
      
    Returns:
      The newly created Project.
      
    Raises:
      ProjectManagerError: If project creation fails.
    """
    try:
      # Create new project with empty Truth
      project = Project(
          title=title,
          description=description,
          author=author,
          genre=genre,
          truth=TruthKnowledgeBase(),
          chapters={},
          is_example=False
      )
      
      # Set as current project
      self.current_project = project
      
      logger.info(f"Created new project: {project.id} - {title}")
      return project
      
    except Exception as e:
      logger.error(f"Failed to create project: {e}")
      raise ProjectManagerError(f"Failed to create project: {e}") from e
  
  def list_all_projects(self) -> list[Project]:
    """List all projects combining user and example projects.
    
    Returns both user-created projects and example projects from the
    storage service.
    
    Returns:
      List of all projects (user + examples).
    """
    try:
      # Get all projects including examples
      projects = self.storage.list_projects(include_examples=True)
      logger.info(f"Listed {len(projects)} total projects")
      return projects
      
    except Exception as e:
      logger.error(f"Failed to list projects: {e}")
      return []
  
  def get_example_projects(self) -> list[Project]:
    """Get only example projects.
    
    Filters and returns only projects marked as examples.
    
    Returns:
      List of example projects.
    """
    try:
      examples = self.storage.list_example_projects()
      logger.info(f"Listed {len(examples)} example projects")
      return examples
      
    except Exception as e:
      logger.error(f"Failed to list example projects: {e}")
      return []
  
  def delete_project(self, project_id: str) -> bool:
    """Delete a project with confirmation.
    
    Removes the project from storage. If the deleted project is the
    current project, clears the current project reference.
    
    Args:
      project_id: The ID of the project to delete.
      
    Returns:
      True if deleted successfully, False if project doesn't exist.
      
    Raises:
      ProjectManagerError: If deletion fails.
    """
    try:
      # Check if we're deleting the current project
      if self.current_project and self.current_project.id == project_id:
        self.current_project = None
        logger.info("Cleared current project reference")
      
      # Delete from storage
      success = self.storage.delete_project(project_id)
      
      if success:
        logger.info(f"Deleted project: {project_id}")
      else:
        logger.warning(f"Project not found for deletion: {project_id}")
      
      return success
      
    except StorageError as e:
      logger.error(f"Failed to delete project {project_id}: {e}")
      raise ProjectManagerError(f"Failed to delete project: {e}") from e
  
  def load_project(self, project_id: str) -> Optional[Project]:
    """Load a project and set it as current.
    
    Args:
      project_id: The ID of the project to load.
      
    Returns:
      The loaded project, or None if not found.
      
    Raises:
      ProjectManagerError: If loading fails.
    """
    try:
      project = self.storage.load_project(project_id)
      
      if project:
        self.current_project = project
        logger.info(f"Loaded project: {project_id}")
      else:
        logger.warning(f"Project not found: {project_id}")
      
      return project
      
    except StorageError as e:
      logger.error(f"Failed to load project {project_id}: {e}")
      raise ProjectManagerError(f"Failed to load project: {e}") from e
  
  def add_chapter(self, number: int, title: str) -> Chapter:
    """Add a new chapter to the current project.
    
    Creates a new Chapter and adds it to the current project.
    The project is not automatically saved.
    
    Args:
      number: The chapter number.
      title: The chapter title.
      
    Returns:
      The newly created Chapter.
      
    Raises:
      ProjectManagerError: If no current project or chapter creation fails.
    """
    if not self.current_project:
      raise ProjectManagerError("No current project loaded")
    
    try:
      # Create new chapter
      chapter = Chapter(
          number=number,
          title=title,
          content="",
          outline=""
      )
      
      # Add to project
      self.current_project.add_chapter(chapter)
      
      logger.info(f"Added chapter {number}: {title} to project {self.current_project.id}")
      return chapter
      
    except Exception as e:
      logger.error(f"Failed to add chapter: {e}")
      raise ProjectManagerError(f"Failed to add chapter: {e}") from e
  
  def update_chapter_content(self, chapter_id: str, content: str) -> None:
    """Update the content of a chapter.
    
    Modifies the chapter content and updates word count and timestamp.
    The project is not automatically saved.
    
    Args:
      chapter_id: The ID of the chapter to update.
      content: The new content for the chapter.
      
    Raises:
      ProjectManagerError: If no current project or chapter not found.
    """
    if not self.current_project:
      raise ProjectManagerError("No current project loaded")
    
    # Find the chapter
    chapter = self.current_project.chapters.get(chapter_id)
    
    if not chapter:
      raise ProjectManagerError(f"Chapter not found: {chapter_id}")
    
    try:
      # Update chapter content
      chapter.update_content(content)
      
      # Update project timestamp
      self.current_project.updated_at = chapter.updated_at
      
      logger.info(f"Updated chapter {chapter_id} content ({chapter.word_count} words)")
      
    except Exception as e:
      logger.error(f"Failed to update chapter content: {e}")
      raise ProjectManagerError(f"Failed to update chapter content: {e}") from e
  
  def save_current_project(self) -> None:
    """Save the current project to storage with validation.
    
    Validates project data before persisting to ensure data integrity.
    Persists all project data including chapters and Truth knowledge base.
    
    Raises:
      ProjectManagerError: If no current project, validation fails, or save fails.
    """
    if not self.current_project:
      raise ProjectManagerError("No current project to save")
    
    try:
      # Validate project data before saving
      if not self.current_project.title or not self.current_project.title.strip():
        raise ProjectManagerError("Project title cannot be empty")
      
      # Validate chapters
      for chapter_id, chapter in self.current_project.chapters.items():
        if not chapter.title or not chapter.title.strip():
          raise ProjectManagerError(f"Chapter {chapter.number} title cannot be empty")
        if chapter.number < 1:
          raise ProjectManagerError(f"Chapter number must be positive: {chapter.number}")
      
      # Validate Truth data
      if self.current_project.truth:
        # Ensure all character IDs are unique
        character_ids = set()
        for char_id in self.current_project.truth.characters.keys():
          if char_id in character_ids:
            raise ProjectManagerError(f"Duplicate character ID: {char_id}")
          character_ids.add(char_id)
        
        # Ensure all plot event IDs are unique
        event_ids = set()
        for event_id in self.current_project.truth.plot_events.keys():
          if event_id in event_ids:
            raise ProjectManagerError(f"Duplicate plot event ID: {event_id}")
          event_ids.add(event_id)
        
        # Ensure all setting IDs are unique
        setting_ids = set()
        for setting_id in self.current_project.truth.settings.keys():
          if setting_id in setting_ids:
            raise ProjectManagerError(f"Duplicate setting ID: {setting_id}")
          setting_ids.add(setting_id)
      
      # Save the project
      self.storage.save_project(self.current_project)
      logger.info(f"Saved current project: {self.current_project.id}")
      
    except ProjectManagerError:
      # Re-raise validation errors
      raise
    except StorageError as e:
      logger.error(f"Failed to save project: {e}")
      raise ProjectManagerError(f"Failed to save project: {e}") from e
    except Exception as e:
      logger.error(f"Unexpected error during save: {e}")
      raise ProjectManagerError(f"Unexpected error during save: {e}") from e
