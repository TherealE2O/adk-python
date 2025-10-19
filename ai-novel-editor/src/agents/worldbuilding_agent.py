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
from ..services.llm_service import LLMService


class WorldBuildingAgent:
  """Agent for conducting interactive world-building Q&A."""
  
  def __init__(self, truth: TruthKnowledgeBase, llm_service: Optional[LLMService] = None):
    """Initialize the world-building agent.
    
    Args:
      truth: The truth knowledge base to populate.
      llm_service: Optional LLM service. If None, creates a new one.
    """
    self.truth = truth
    self.question_tree: Optional[QuestionTree] = None
    self.llm_service = llm_service or LLMService()
  
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
    
    # Use AI to generate contextual questions if available
    if self.llm_service.is_available():
      ai_questions = self._generate_ai_questions(answer, current_node)
      if ai_questions:
        return ai_questions
    
    # Fallback to rule-based question generation
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
  
  def _generate_ai_questions(
      self,
      answer: str,
      current_node: QuestionNode
  ) -> list[QuestionNode]:
    """Generate questions using AI based on the answer.
    
    Args:
      answer: The user's answer.
      current_node: The current question node.
      
    Returns:
      List of generated question nodes.
    """
    context = f"""Previous question: {current_node.question}
User's answer: {answer}

Based on this answer, generate 3-5 insightful follow-up questions that would help develop the story. Focus on:
- Character development and motivations
- Plot details and conflicts
- World-building and settings
- Relationships and dynamics

Generate questions that are specific to the information provided."""
    
    try:
      questions = self.llm_service.generate_questions(context, num_questions=5)
      
      new_nodes = []
      for question in questions:
        # Determine entity type based on question content
        entity_type = EntityType.PLOT_EVENT
        if any(word in question.lower() for word in ['character', 'who', 'protagonist']):
          entity_type = EntityType.CHARACTER
        elif any(word in question.lower() for word in ['where', 'world', 'place', 'setting']):
          entity_type = EntityType.SETTING
        
        node = QuestionNode(
            question=question,
            entity_type=entity_type,
            parent_id=current_node.id
        )
        self.question_tree.add_node(node, current_node.id)
        new_nodes.append(node)
      
      return new_nodes
    except Exception as e:
      print(f"Error generating AI questions: {e}")
      return []
  
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
    # Try AI extraction first if available
    if self.llm_service.is_available():
      entity_data = self.llm_service.extract_entities(
          answer,
          entity_type.value
      )
      
      if entity_data:
        try:
          if entity_type == EntityType.CHARACTER:
            char = Character(
                name=entity_data.get('name', 'Unnamed Character'),
                description=entity_data.get('description', answer),
                traits=entity_data.get('traits', []),
                role=entity_data.get('role', '')
            )
            self.truth.add_character(char)
            return
          
          elif entity_type == EntityType.PLOT_EVENT:
            event = PlotEvent(
                title=entity_data.get('title', 'Story Event'),
                description=entity_data.get('description', answer),
                significance=entity_data.get('significance', '')
            )
            self.truth.add_plot_event(event)
            return
          
          elif entity_type == EntityType.SETTING:
            setting = Setting(
                name=entity_data.get('name', 'Story Setting'),
                type=entity_data.get('type', 'location'),
                description=entity_data.get('description', answer),
                rules=entity_data.get('rules', [])
            )
            self.truth.add_setting(setting)
            return
        except Exception as e:
          print(f"Error creating entity from AI extraction: {e}")
    
    # Fallback to simple extraction
    if entity_type == EntityType.CHARACTER:
      char = Character(
          name="Extracted Character",
          description=answer
      )
      self.truth.add_character(char)
    
    elif entity_type == EntityType.PLOT_EVENT:
      event = PlotEvent(
          title="Story Event",
          description=answer
      )
      self.truth.add_plot_event(event)
    
    elif entity_type == EntityType.SETTING:
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
