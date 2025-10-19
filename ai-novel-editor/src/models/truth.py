"""Data models for the Truth knowledge base."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class EntityType(str, Enum):
  """Types of entities in the Truth knowledge base."""
  CHARACTER = "character"
  PLOT_EVENT = "plot_event"
  SETTING = "setting"
  WORLD_BUILDING = "world_building"


class QuestionStatus(str, Enum):
  """Status of a question in the question tree."""
  PENDING = "pending"
  ANSWERED = "answered"
  SKIPPED = "skipped"


class Character(BaseModel):
  """Represents a character in the story."""
  
  id: str = Field(default_factory=lambda: f"char_{datetime.now().timestamp()}")
  name: str
  description: str = ""
  traits: list[str] = Field(default_factory=list)
  backstory: str = ""
  motivations: list[str] = Field(default_factory=list)
  relationships: dict[str, str] = Field(default_factory=dict)
  physical_description: str = ""
  role: str = ""
  metadata: dict[str, Any] = Field(default_factory=dict)


class PlotEvent(BaseModel):
  """Represents a plot event or timeline entry."""
  
  id: str = Field(default_factory=lambda: f"event_{datetime.now().timestamp()}")
  title: str
  description: str
  timestamp: Optional[str] = None
  characters_involved: list[str] = Field(default_factory=list)
  location: Optional[str] = None
  significance: str = ""
  order: int = 0
  metadata: dict[str, Any] = Field(default_factory=dict)


class Setting(BaseModel):
  """Represents a setting or world-building element."""
  
  id: str = Field(default_factory=lambda: f"setting_{datetime.now().timestamp()}")
  name: str
  type: str
  description: str
  rules: list[str] = Field(default_factory=list)
  related_characters: list[str] = Field(default_factory=list)
  related_events: list[str] = Field(default_factory=list)
  metadata: dict[str, Any] = Field(default_factory=dict)


class QuestionNode(BaseModel):
  """Represents a node in the question tree."""
  
  id: str = Field(default_factory=lambda: f"q_{datetime.now().timestamp()}")
  question: str
  entity_type: EntityType
  entity_id: Optional[str] = None
  parent_id: Optional[str] = None
  children_ids: list[str] = Field(default_factory=list)
  status: QuestionStatus = QuestionStatus.PENDING
  answer: Optional[str] = None
  answered_at: Optional[datetime] = None
  metadata: dict[str, Any] = Field(default_factory=dict)


class QuestionTree(BaseModel):
  """Represents the entire question tree structure."""
  
  root_id: str
  nodes: dict[str, QuestionNode] = Field(default_factory=dict)
  current_node_id: Optional[str] = None
  
  def add_node(self, node: QuestionNode, parent_id: Optional[str] = None) -> None:
    """Add a node to the tree."""
    self.nodes[node.id] = node
    if parent_id and parent_id in self.nodes:
      self.nodes[parent_id].children_ids.append(node.id)
      node.parent_id = parent_id
  
  def get_node(self, node_id: str) -> Optional[QuestionNode]:
    """Get a node by ID."""
    return self.nodes.get(node_id)
  
  def get_pending_questions(self) -> list[QuestionNode]:
    """Get all pending questions."""
    return [
        node for node in self.nodes.values()
        if node.status == QuestionStatus.PENDING
    ]
  
  def get_answered_questions(self) -> list[QuestionNode]:
    """Get all answered questions."""
    return [
        node for node in self.nodes.values()
        if node.status == QuestionStatus.ANSWERED
    ]


class TruthKnowledgeBase(BaseModel):
  """The complete Truth knowledge base for a story."""
  
  characters: dict[str, Character] = Field(default_factory=dict)
  plot_events: dict[str, PlotEvent] = Field(default_factory=dict)
  settings: dict[str, Setting] = Field(default_factory=dict)
  question_tree: Optional[QuestionTree] = None
  created_at: datetime = Field(default_factory=datetime.now)
  updated_at: datetime = Field(default_factory=datetime.now)
  
  def add_character(self, character: Character) -> None:
    """Add a character to the knowledge base."""
    self.characters[character.id] = character
    self.updated_at = datetime.now()
  
  def add_plot_event(self, event: PlotEvent) -> None:
    """Add a plot event to the knowledge base."""
    self.plot_events[event.id] = event
    self.updated_at = datetime.now()
  
  def add_setting(self, setting: Setting) -> None:
    """Add a setting to the knowledge base."""
    self.settings[setting.id] = setting
    self.updated_at = datetime.now()
  
  def search(self, query: str) -> dict[str, list[Any]]:
    """Search across all entities in the knowledge base."""
    results = {
        'characters': [],
        'plot_events': [],
        'settings': []
    }
    
    query_lower = query.lower()
    
    for char in self.characters.values():
      if (query_lower in char.name.lower() or
          query_lower in char.description.lower()):
        results['characters'].append(char)
    
    for event in self.plot_events.values():
      if (query_lower in event.title.lower() or
          query_lower in event.description.lower()):
        results['plot_events'].append(event)
    
    for setting in self.settings.values():
      if (query_lower in setting.name.lower() or
          query_lower in setting.description.lower()):
        results['settings'].append(setting)
    
    return results
