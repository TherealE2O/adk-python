"""Storage service for persisting projects."""

from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path
from typing import Optional

from ..models.project import Project


logger = logging.getLogger(__name__)


class StorageError(Exception):
  """Base exception for storage-related errors."""
  pass


class StorageService:
  """Handles saving and loading projects from disk.
  
  Projects are stored in the following structure:
    data/projects/{project_id}/project.json
    data/projects/examples/{project_id}/project.json
  """
  
  def __init__(self, base_path: str = "data/projects"):
    """Initialize the storage service.
    
    Args:
      base_path: Base directory for storing projects.
    """
    self.base_path = Path(base_path)
    self.examples_path = self.base_path / "examples"
    
    # Create directory structure
    try:
      self.base_path.mkdir(parents=True, exist_ok=True)
      self.examples_path.mkdir(parents=True, exist_ok=True)
      logger.info(f"Storage initialized at {self.base_path}")
    except OSError as e:
      logger.error(f"Failed to create storage directories: {e}")
      raise StorageError(f"Failed to initialize storage: {e}") from e
  
  def save_project(self, project: Project) -> None:
    """Save a project to disk as JSON with automatic backup.
    
    Serializes the entire Project object including Truth knowledge base
    and all chapters to a single JSON file. Creates a backup before saving.
    
    Args:
      project: The project to save.
      
    Raises:
      StorageError: If the project cannot be saved.
    """
    try:
      # Determine the correct directory based on is_example flag
      if project.is_example:
        project_dir = self.examples_path / project.id
      else:
        project_dir = self.base_path / project.id
      
      # Create project directory
      project_dir.mkdir(parents=True, exist_ok=True)
      
      # Serialize project to JSON
      project_file = project_dir / "project.json"
      backup_file = project_dir / "project.backup.json"
      
      # Create backup if file exists
      if project_file.exists():
        try:
          shutil.copy2(project_file, backup_file)
          logger.info(f"Created backup for project {project.id}")
        except Exception as e:
          logger.warning(f"Failed to create backup for project {project.id}: {e}")
      
      # Serialize and validate project data
      project_data = project.model_dump(mode='json')
      
      # Write to temporary file first
      temp_file = project_dir / "project.tmp.json"
      with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(project_data, f, indent=2, default=str, ensure_ascii=False)
      
      # Verify the temporary file is valid JSON
      with open(temp_file, 'r', encoding='utf-8') as f:
        json.load(f)
      
      # Replace the original file with the temporary file
      shutil.move(str(temp_file), str(project_file))
      
      logger.info(f"Project {project.id} saved successfully")
      
    except (OSError, IOError) as e:
      logger.error(f"Failed to save project {project.id}: {e}")
      # Attempt to restore from backup if save failed
      if backup_file.exists():
        try:
          shutil.copy2(backup_file, project_file)
          logger.info(f"Restored project {project.id} from backup after save failure")
        except Exception as restore_error:
          logger.error(f"Failed to restore backup: {restore_error}")
      raise StorageError(f"Failed to save project: {e}") from e
    except Exception as e:
      logger.error(f"Unexpected error saving project {project.id}: {e}")
      raise StorageError(f"Unexpected error saving project: {e}") from e
  
  def load_project(self, project_id: str) -> Optional[Project]:
    """Load a project from disk with automatic recovery from backup.
    
    Deserializes JSON file back to Project object with all nested models.
    Searches both user projects and example projects. If the main file is
    corrupted, attempts to load from backup.
    
    Args:
      project_id: The ID of the project to load.
      
    Returns:
      The loaded project, or None if not found.
      
    Raises:
      StorageError: If the project file is corrupted and cannot be recovered.
    """
    # Try user projects first, then examples
    project_paths = [
      (self.base_path / project_id / "project.json", self.base_path / project_id / "project.backup.json"),
      (self.examples_path / project_id / "project.json", self.examples_path / project_id / "project.backup.json")
    ]
    
    for project_file, backup_file in project_paths:
      if project_file.exists():
        # Try loading the main file
        try:
          with open(project_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
          
          project = Project(**data)
          logger.info(f"Project {project_id} loaded successfully")
          return project
          
        except (json.JSONDecodeError, Exception) as e:
          logger.error(f"Corrupted project file {project_file}: {e}")
          
          # Try loading from backup
          if backup_file.exists():
            try:
              logger.info(f"Attempting to recover project {project_id} from backup")
              with open(backup_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
              
              project = Project(**data)
              
              # Restore the main file from backup
              shutil.copy2(backup_file, project_file)
              logger.info(f"Project {project_id} recovered from backup successfully")
              return project
              
            except Exception as backup_error:
              logger.error(f"Failed to recover from backup: {backup_error}")
              raise StorageError(
                  f"Project file is corrupted and backup recovery failed. "
                  f"Original error: {e}. Backup error: {backup_error}"
              ) from e
          else:
            raise StorageError(
                f"Project file is corrupted and no backup available: {e}"
            ) from e
        
        except (OSError, IOError) as e:
          logger.error(f"Failed to read project file {project_file}: {e}")
          raise StorageError(f"Failed to read project: {e}") from e
    
    logger.warning(f"Project {project_id} not found")
    return None
  
  def list_projects(self, include_examples: bool = False) -> list[Project]:
    """List all user projects.
    
    Scans project directories and loads project metadata.
    Excludes the examples directory by default.
    
    Args:
      include_examples: If True, include example projects in the list.
    
    Returns:
      List of all projects (excluding examples unless specified).
    """
    projects = []
    
    # List user projects
    try:
      if self.base_path.exists():
        for project_dir in self.base_path.iterdir():
          # Skip the examples directory
          if project_dir.is_dir() and project_dir.name != "examples":
            try:
              project = self.load_project(project_dir.name)
              if project:
                projects.append(project)
            except StorageError as e:
              logger.warning(f"Skipping corrupted project {project_dir.name}: {e}")
              continue
    except OSError as e:
      logger.error(f"Failed to list projects: {e}")
    
    # Optionally include example projects
    if include_examples:
      try:
        if self.examples_path.exists():
          for project_dir in self.examples_path.iterdir():
            if project_dir.is_dir():
              try:
                project = self.load_project(project_dir.name)
                if project:
                  projects.append(project)
              except StorageError as e:
                logger.warning(f"Skipping corrupted example {project_dir.name}: {e}")
                continue
      except OSError as e:
        logger.error(f"Failed to list example projects: {e}")
    
    return projects
  
  def list_example_projects(self) -> list[Project]:
    """List all example projects.
    
    Returns:
      List of example projects from data/projects/examples/.
    """
    projects = []
    
    try:
      if self.examples_path.exists():
        for project_dir in self.examples_path.iterdir():
          if project_dir.is_dir():
            try:
              project = self.load_project(project_dir.name)
              if project:
                projects.append(project)
            except StorageError as e:
              logger.warning(f"Skipping corrupted example {project_dir.name}: {e}")
              continue
    except OSError as e:
      logger.error(f"Failed to list example projects: {e}")
    
    return projects
  
  def delete_project(self, project_id: str) -> bool:
    """Delete a project and all its files.
    
    Removes the entire project directory including all chapters and Truth data.
    
    Args:
      project_id: The ID of the project to delete.
      
    Returns:
      True if deleted successfully, False if project doesn't exist.
      
    Raises:
      StorageError: If the project cannot be deleted.
    """
    # Check both user and example directories
    project_paths = [
      self.base_path / project_id,
      self.examples_path / project_id
    ]
    
    for project_dir in project_paths:
      if project_dir.exists():
        try:
          shutil.rmtree(project_dir)
          logger.info(f"Project {project_id} deleted successfully")
          return True
        except OSError as e:
          logger.error(f"Failed to delete project {project_id}: {e}")
          raise StorageError(f"Failed to delete project: {e}") from e
    
    logger.warning(f"Project {project_id} not found for deletion")
    return False
  
  def project_exists(self, project_id: str) -> bool:
    """Check if a project exists.
    
    Checks both user projects and example projects.
    
    Args:
      project_id: The ID of the project to check.
      
    Returns:
      True if the project exists, False otherwise.
    """
    user_project = self.base_path / project_id / "project.json"
    example_project = self.examples_path / project_id / "project.json"
    
    return user_project.exists() or example_project.exists()
