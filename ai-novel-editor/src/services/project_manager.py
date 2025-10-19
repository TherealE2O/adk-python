"""Project manager for handling project operations."""

from __future__ import annotations

from typing import Optional

from ..models.project import Project, Chapter
from ..models.truth import TruthKnowledgeBase
from .storage import StorageService


class ProjectManager:
  """Manages novel writing projects."""
  
  def __init__(self, storage_service: StorageService):
    """Initialize the project manager.
    
    Args:
      storage_service: The storage service to use.
    """
    self.storage = storage_service
    self.current_project: Optional[Project] = None
  
  def create_project(
      self,
      title: str,
      description: str = "",
      author: str = "",
      genre: str = ""
  ) -> Project:
    """Create a new project.
    
    Args:
      title: The title of the project.
      description: A description of the project.
      author: The author name.
      genre: The genre of the novel.
      
    Returns:
      The newly created project.
    """
    project = Project(
        title=title,
        description=description,
        author=author,
        genre=genre,
        truth=TruthKnowledgeBase()
    )
    self.storage.save_project(project)
    self.current_project = project
    return project
  
  def load_project(self, project_id: str) -> Optional[Project]:
    """Load a project by ID.
    
    Args:
      project_id: The ID of the project to load.
      
    Returns:
      The loaded project, or None if not found.
    """
    project = self.storage.load_project(project_id)
    if project:
      self.current_project = project
    return project
  
  def save_current_project(self) -> None:
    """Save the current project."""
    if self.current_project:
      self.storage.save_project(self.current_project)
  
  def list_all_projects(self) -> list[Project]:
    """List all projects.
    
    Returns:
      List of all projects.
    """
    return self.storage.list_projects()
  
  def delete_project(self, project_id: str) -> bool:
    """Delete a project.
    
    Args:
      project_id: The ID of the project to delete.
      
    Returns:
      True if deleted successfully, False otherwise.
    """
    if self.current_project and self.current_project.id == project_id:
      self.current_project = None
    return self.storage.delete_project(project_id)
  
  def add_chapter(self, number: int, title: str) -> Optional[Chapter]:
    """Add a new chapter to the current project.
    
    Args:
      number: The chapter number.
      title: The chapter title.
      
    Returns:
      The newly created chapter, or None if no current project.
    """
    if not self.current_project:
      return None
    
    chapter = Chapter(number=number, title=title)
    self.current_project.add_chapter(chapter)
    self.save_current_project()
    return chapter
  
  def update_chapter_content(
      self,
      chapter_id: str,
      content: str
  ) -> bool:
    """Update a chapter's content.
    
    Args:
      chapter_id: The ID of the chapter to update.
      content: The new content.
      
    Returns:
      True if updated successfully, False otherwise.
    """
    if not self.current_project:
      return False
    
    chapter = self.current_project.chapters.get(chapter_id)
    if not chapter:
      return False
    
    chapter.update_content(content)
    self.save_current_project()
    return True
  
  def get_example_projects(self) -> list[Project]:
    """Get example projects.
    
    Returns:
      List of example projects.
    """
    return [p for p in self.list_all_projects() if p.is_example]
