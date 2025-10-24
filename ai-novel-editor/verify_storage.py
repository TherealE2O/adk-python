"""Simple verification script for StorageService."""

import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.storage import StorageService, StorageError
from src.models.project import Project, Chapter
from src.models.truth import Character

def test_storage():
  """Test basic storage operations."""
  print("Testing StorageService...")
  
  # Create temporary storage
  with tempfile.TemporaryDirectory() as tmpdir:
    storage = StorageService(base_path=tmpdir)
    print(f"✓ Storage initialized at {tmpdir}")
    
    # Create a test project
    project = Project(
      title="Test Novel",
      description="A test project",
      author="Test Author",
      genre="Fantasy"
    )
    
    # Add a chapter
    chapter = Chapter(number=1, title="Chapter One", content="Once upon a time...")
    chapter.update_word_count()
    project.add_chapter(chapter)
    print(f"✓ Created project with {len(project.chapters)} chapter(s)")
    
    # Add a character
    character = Character(name="Hero", description="The protagonist")
    project.truth.add_character(character)
    print(f"✓ Added {len(project.truth.characters)} character(s) to Truth")
    
    # Save the project
    storage.save_project(project)
    print(f"✓ Saved project {project.id}")
    
    # Check if project exists
    assert storage.project_exists(project.id), "Project should exist"
    print(f"✓ Project exists check passed")
    
    # Load the project
    loaded = storage.load_project(project.id)
    assert loaded is not None, "Project should load"
    assert loaded.title == project.title, "Title should match"
    assert len(loaded.chapters) == 1, "Should have 1 chapter"
    assert len(loaded.truth.characters) == 1, "Should have 1 character"
    print(f"✓ Loaded project successfully")
    
    # List projects
    projects = storage.list_projects()
    assert len(projects) == 1, "Should have 1 project"
    print(f"✓ Listed {len(projects)} project(s)")
    
    # Test example project
    example = Project(
      title="Example Novel",
      description="An example",
      author="Example Author",
      is_example=True
    )
    storage.save_project(example)
    print(f"✓ Saved example project")
    
    # List example projects
    examples = storage.list_example_projects()
    assert len(examples) == 1, "Should have 1 example"
    print(f"✓ Listed {len(examples)} example project(s)")
    
    # Regular list should not include examples
    user_projects = storage.list_projects(include_examples=False)
    assert len(user_projects) == 1, "Should have 1 user project"
    print(f"✓ User projects list excludes examples")
    
    # Delete project
    result = storage.delete_project(project.id)
    assert result is True, "Delete should succeed"
    assert not storage.project_exists(project.id), "Project should not exist"
    print(f"✓ Deleted project successfully")
    
    print("\n✅ All storage tests passed!")

if __name__ == "__main__":
  try:
    test_storage()
  except Exception as e:
    print(f"\n❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
