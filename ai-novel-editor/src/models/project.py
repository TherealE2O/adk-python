"""Data models for novel projects and chapters."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from .truth import TruthKnowledgeBase


class Chapter(BaseModel):
  """Represents a chapter in the novel."""
  
  id: str = Field(default_factory=lambda: f"chapter_{datetime.now().timestamp()}")
  number: int
  title: str
  content: str = ""
  outline: str = ""
  created_at: datetime = Field(default_factory=datetime.now)
  updated_at: datetime = Field(default_factory=datetime.now)
  word_count: int = 0
  
  def update_word_count(self) -> None:
    """Update the word count based on current content."""
    self.word_count = len(self.content.split()) if self.content else 0
  
  def update_content(self, new_content: str) -> None:
    """Update the chapter content and metadata."""
    self.content = new_content
    self.update_word_count()
    self.updated_at = datetime.now()


class Project(BaseModel):
  """Represents a novel writing project."""
  
  id: str = Field(default_factory=lambda: f"proj_{datetime.now().timestamp()}")
  title: str
  description: str = ""
  author: str = ""
  genre: str = ""
  truth: TruthKnowledgeBase = Field(default_factory=TruthKnowledgeBase)
  chapters: dict[str, Chapter] = Field(default_factory=dict)
  created_at: datetime = Field(default_factory=datetime.now)
  updated_at: datetime = Field(default_factory=datetime.now)
  is_example: bool = False
  
  def add_chapter(self, chapter: Chapter) -> None:
    """Add a chapter to the project."""
    self.chapters[chapter.id] = chapter
    self.updated_at = datetime.now()
  
  def get_chapter_by_number(self, number: int) -> Optional[Chapter]:
    """Get a chapter by its number."""
    for chapter in self.chapters.values():
      if chapter.number == number:
        return chapter
    return None
  
  def get_sorted_chapters(self) -> list[Chapter]:
    """Get all chapters sorted by number."""
    return sorted(self.chapters.values(), key=lambda c: c.number)
  
  def get_total_word_count(self) -> int:
    """Get the total word count across all chapters."""
    return sum(chapter.word_count for chapter in self.chapters.values())
