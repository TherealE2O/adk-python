"""World-building agent for interactive Q&A."""

from __future__ import annotations

import json
from typing import Optional

from ..models.truth import (
    Character,
    PlotEvent,
    Setting,
    QuestionNode,
    QuestionTree,
    EntityType,
    QuestionStatus,
    TruthKnowledgeBase,
)


class WorldBuildingAgent:
  """Agent for conducting interactive world-building Q&A."""
  
  def __init__(self, truth: TruthKnowledgeBase):
    """Initialize the world-building agent.
    
    Args:
      truth: The truth knowledge base to populate.
    """
    self.truth = truth
    self.question_tree: Optional[QuestionTree] = None
  
  def initialize_question_tree(self, initial_answer: str) -> QuestionTree:
    """Initialize the question tree based on the initial story description.
    
    Args:
      initial_answer: The user's answer to "What is your story about?"
      
    Returns:
      The initialized question tree.
    """
    root_node = QuestionNode(
        question="What is your story about?",
        entity_type=EntityType.PLOT_EVENT,
        status=QuestionStatus.ANSWERED,
        answer=initial_answer
    )
    
    tree = QuestionTree(root_id=root_node.id)
    tree.add_node(root_node)
    
    self.question_tree = tree
    self.truth.question_tree = tree
    
    return tree
  
  def generate_follow_up_questions(
      self,
      answer: str,
      current_node_id: str
  ) -> list[QuestionNode]:
    """Generate follow-up questions based on an answer.
    
    This analyzes the answer to extract entities and generate relevant questions.
    
    Args:
      answer: The user's answer.
      current_node_id: The ID of the current question node.
      
    Returns:
      List of generated question nodes.
    """
    if not self.question_tree:
      return []
    
    current_node = self.question_tree.get_node(current_node_id)
    if not current_node:
      return []
    
    current_node.answer = answer
    current_node.status = QuestionStatus.ANSWERED
    
    new_questions = []
    
    # Generate character-related questions
    if "character" in answer.lower() or "protagonist" in answer.lower():
      char_questions = [
          "What is the main character's name and background?",
          "What motivates the main character?",
          "What are the main character's key traits and personality?",
      ]
      for q in char_questions:
        node = QuestionNode(
            question=q,
            entity_type=EntityType.CHARACTER,
            parent_id=current_node_id
        )
        self.question_tree.add_node(node, current_node_id)
        new_questions.append(node)
    
    # Generate plot-related questions
    if any(word in answer.lower() for word in ["plot", "story", "conflict", "goal"]):
      plot_questions = [
          "What is the central conflict or challenge?",
          "What are the major plot points or turning events?",
          "How does the story begin?",
      ]
      for q in plot_questions:
        node = QuestionNode(
            question=q,
            entity_type=EntityType.PLOT_EVENT,
            parent_id=current_node_id
        )
        self.question_tree.add_node(node, current_node_id)
        new_questions.append(node)
    
    # Generate setting-related questions
    if any(word in answer.lower() for word in ["world", "place", "setting", "location"]):
      setting_questions = [
          "Where does the story take place?",
          "What is unique about this world or setting?",
          "What are the key locations in your story?",
      ]
      for q in setting_questions:
        node = QuestionNode(
            question=q,
            entity_type=EntityType.SETTING,
            parent_id=current_node_id
        )
        self.question_tree.add_node(node, current_node_id)
        new_questions.append(node)
    
    return new_questions
  
  def extract_entities_from_answer(
      self,
      answer: str,
      entity_type: EntityType
  ) -> None:
    """Extract and store entities from an answer.
    
    Args:
      answer: The user's answer.
      entity_type: The type of entity to extract.
    """
    # Simple extraction logic - in production, use LLM for better extraction
    if entity_type == EntityType.CHARACTER:
      # Extract character information
      char = Character(
          name="Extracted Character",
          description=answer
      )
      self.truth.add_character(char)
    
    elif entity_type == EntityType.PLOT_EVENT:
      # Extract plot event
      event = PlotEvent(
          title="Story Event",
          description=answer
      )
      self.truth.add_plot_event(event)
    
    elif entity_type == EntityType.SETTING:
      # Extract setting
      setting = Setting(
          name="Story Setting",
          type="location",
          description=answer
      )
      self.truth.add_setting(setting)
  
  def get_next_question(self) -> Optional[QuestionNode]:
    """Get the next pending question.
    
    Returns:
      The next pending question node, or None if all answered.
    """
    if not self.question_tree:
      return None
    
    pending = self.question_tree.get_pending_questions()
    return pending[0] if pending else None
  
  def answer_question(
      self,
      node_id: str,
      answer: str
  ) -> list[QuestionNode]:
    """Answer a question and generate follow-ups.
    
    Args:
      node_id: The ID of the question node to answer.
      answer: The user's answer.
      
    Returns:
      List of newly generated follow-up questions.
    """
    if not self.question_tree:
      return []
    
    node = self.question_tree.get_node(node_id)
    if not node:
      return []
    
    # Extract entities from the answer
    self.extract_entities_from_answer(answer, node.entity_type)
    
    # Generate follow-up questions
    new_questions = self.generate_follow_up_questions(answer, node_id)
    
    return new_questions
  
  def get_question_tree_summary(self) -> dict:
    """Get a summary of the question tree for visualization.
    
    Returns:
      Dictionary representation of the tree structure.
    """
    if not self.question_tree:
      return {}
    
    def node_to_dict(node: QuestionNode) -> dict:
      return {
          'id': node.id,
          'question': node.question,
          'status': node.status.value,
          'entity_type': node.entity_type.value,
          'children': [
              node_to_dict(self.question_tree.get_node(child_id))
              for child_id in node.children_ids
              if self.question_tree.get_node(child_id)
          ]
      }
    
    root = self.question_tree.get_node(self.question_tree.root_id)
    if not root:
      return {}
    
    return node_to_dict(root)
