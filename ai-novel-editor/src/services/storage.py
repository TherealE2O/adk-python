"""Storage service for persisting projects."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from ..models.project import Project


class StorageService:
  """Handles saving and loading projects from disk."""
  
  def __init__(self, base_path: str = "data/projects"):
    """Initialize the storage service.
    
    Args:
      base_path: Base directory for storing projects.
    """
    self.base_path = Path(base_path)
    self.base_path.mkdir(parents=True, exist_ok=True)
  
  def save_project(self, project: Project) -> None:
    """Save a project to disk.
    
    Args:
      project: The project to save.
    """
    project_dir = self.base_path / project.id
    project_dir.mkdir(parents=True, exist_ok=True)
    
    project_file = project_dir / "project.json"
    with open(project_file, 'w', encoding='utf-8') as f:
      json.dump(project.model_dump(mode='json'), f, indent=2, default=str)
  
  def load_project(self, project_id: str) -> Optional[Project]:
    """Load a project from disk.
    
    Args:
      project_id: The ID of the project to load.
      
    Returns:
      The loaded project, or None if not found.
    """
    project_file = self.base_path / project_id / "project.json"
    if not project_file.exists():
      return None
    
    with open(project_file, 'r', encoding='utf-8') as f:
      data = json.load(f)
      return Project(**data)
  
  def list_projects(self) -> list[Project]:
    """List all projects.
    
    Returns:
      List of all projects.
    """
    projects = []
    for project_dir in self.base_path.iterdir():
      if project_dir.is_dir():
        project = self.load_project(project_dir.name)
        if project:
          projects.append(project)
    return projects
  
  def delete_project(self, project_id: str) -> bool:
    """Delete a project.
    
    Args:
      project_id: The ID of the project to delete.
      
    Returns:
      True if deleted successfully, False otherwise.
    """
    project_dir = self.base_path / project_id
    if not project_dir.exists():
      return False
    
    import shutil
    shutil.rmtree(project_dir)
    return True
  
  def project_exists(self, project_id: str) -> bool:
    """Check if a project exists.
    
    Args:
      project_id: The ID of the project to check.
      
    Returns:
      True if the project exists, False otherwise.
    """
    project_file = self.base_path / project_id / "project.json"
    return project_file.exists()
