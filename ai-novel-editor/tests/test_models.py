"""Tests for data models."""

import pytest
from src.models.truth import (
    Character,
    PlotEvent,
    Setting,
    QuestionNode,
    QuestionTree,
    EntityType,
    QuestionStatus,
    TruthKnowledgeBase,
)
from src.models.project import Project, Chapter


def test_character_creation():
  """Test creating a character."""
  char = Character(
      name="John Doe",
      description="A brave hero",
      traits=["brave", "kind"]
  )
  assert char.name == "John Doe"
  assert "brave" in char.traits
  assert char.id.startswith("char_")


def test_plot_event_creation():
  """Test creating a plot event."""
  event = PlotEvent(
      title="The Beginning",
      description="The story starts here",
      order=1
  )
  assert event.title == "The Beginning"
  assert event.order == 1
  assert event.id.startswith("event_")


def test_setting_creation():
  """Test creating a setting."""
  setting = Setting(
      name="The Castle",
      type="location",
      description="A grand castle on a hill"
  )
  assert setting.name == "The Castle"
  assert setting.type == "location"
  assert setting.id.startswith("setting_")


def test_question_node():
  """Test question node creation."""
  node = QuestionNode(
      question="What is your character's name?",
      entity_type=EntityType.CHARACTER,
      status=QuestionStatus.PENDING
  )
  assert node.question == "What is your character's name?"
  assert node.status == QuestionStatus.PENDING
  assert node.entity_type == EntityType.CHARACTER


def test_question_tree():
  """Test question tree operations."""
  root = QuestionNode(
      question="Root question",
      entity_type=EntityType.PLOT_EVENT
  )
  tree = QuestionTree(root_id=root.id)
  tree.add_node(root)
  
  child = QuestionNode(
      question="Child question",
      entity_type=EntityType.CHARACTER
  )
  tree.add_node(child, parent_id=root.id)
  
  assert len(tree.nodes) == 2
  assert child.id in root.children_ids
  assert child.parent_id == root.id


def test_truth_knowledge_base():
  """Test truth knowledge base operations."""
  truth = TruthKnowledgeBase()
  
  char = Character(name="Hero", description="The main character")
  truth.add_character(char)
  
  event = PlotEvent(title="Event 1", description="First event")
  truth.add_plot_event(event)
  
  setting = Setting(name="World", type="world", description="The world")
  truth.add_setting(setting)
  
  assert len(truth.characters) == 1
  assert len(truth.plot_events) == 1
  assert len(truth.settings) == 1
  
  # Test search
  results = truth.search("Hero")
  assert len(results['characters']) == 1
  assert results['characters'][0].name == "Hero"


def test_chapter():
  """Test chapter creation and updates."""
  chapter = Chapter(number=1, title="Chapter One")
  assert chapter.number == 1
  assert chapter.title == "Chapter One"
  assert chapter.word_count == 0
  
  chapter.update_content("This is some content with five words.")
  assert chapter.word_count == 7
  assert chapter.content == "This is some content with five words."


def test_project():
  """Test project creation and operations."""
  project = Project(
      title="My Novel",
      description="A great story",
      author="Author Name"
  )
  
  assert project.title == "My Novel"
  assert project.author == "Author Name"
  assert len(project.chapters) == 0
  
  chapter1 = Chapter(number=1, title="Chapter 1")
  project.add_chapter(chapter1)
  
  chapter2 = Chapter(number=2, title="Chapter 2")
  project.add_chapter(chapter2)
  
  assert len(project.chapters) == 2
  
  # Test get chapter by number
  found = project.get_chapter_by_number(1)
  assert found is not None
  assert found.title == "Chapter 1"
  
  # Test sorted chapters
  sorted_chapters = project.get_sorted_chapters()
  assert sorted_chapters[0].number == 1
  assert sorted_chapters[1].number == 2


if __name__ == "__main__":
  pytest.main([__file__, "-v"])
