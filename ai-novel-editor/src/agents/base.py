"""Base interfaces and abstract classes for AI agents.

This module defines the common interfaces that all agents should implement,
ensuring consistent behavior across different agent types.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from ..models.truth import TruthKnowledgeBase


class BaseAgent(ABC):
    """Abstract base class for all AI agents.
    
    Agents are autonomous components that use LLM services to perform
    complex tasks like world-building, editing, and content generation.
    """
    
    def __init__(self, truth: TruthKnowledgeBase):
        """Initialize the agent with a Truth knowledge base.
        
        Args:
            truth: The Truth knowledge base for this project
        """
        self.truth = truth
    
    @abstractmethod
    def is_ready(self) -> bool:
        """Check if the agent is ready to perform operations.
        
        Returns:
            bool: True if agent has all required dependencies
        """
        pass
    
    def get_context(self) -> dict[str, Any]:
        """Build context dictionary from the Truth knowledge base.
        
        Returns:
            dict: Context information for LLM prompts
        """
        return {
            "characters": [
                {
                    "name": char.name,
                    "description": char.description,
                    "traits": char.traits
                }
                for char in self.truth.characters.values()
            ],
            "plot_events": [
                {
                    "title": event.title,
                    "description": event.description,
                    "order": event.order
                }
                for event in self.truth.plot_events.values()
            ],
            "settings": [
                {
                    "name": setting.name,
                    "type": setting.type,
                    "description": setting.description
                }
                for setting in self.truth.settings.values()
            ]
        }


class WorldBuildingAgentInterface(BaseAgent):
    """Interface for world-building agents.
    
    World-building agents conduct interactive Q&A sessions to build
    the Truth knowledge base through entity extraction and question generation.
    """
    
    @abstractmethod
    def initialize_question_tree(self, initial_answer: str) -> None:
        """Initialize the question tree with the first answer.
        
        Args:
            initial_answer: User's answer to "What is your story about?"
        """
        pass
    
    @abstractmethod
    def generate_follow_up_questions(
        self, 
        answer: str, 
        parent_id: str
    ) -> list[Any]:
        """Generate follow-up questions based on an answer.
        
        Args:
            answer: The user's answer text
            parent_id: ID of the parent question node
            
        Returns:
            list: List of generated QuestionNode objects
        """
        pass
    
    @abstractmethod
    def answer_question(self, question_id: str, answer: str) -> list[Any]:
        """Process a question answer and generate follow-ups.
        
        Args:
            question_id: ID of the question being answered
            answer: The user's answer text
            
        Returns:
            list: List of newly generated QuestionNode objects
        """
        pass
    
    @abstractmethod
    def extract_entities(self, answer: str) -> dict[str, Any]:
        """Extract story entities from an answer.
        
        Args:
            answer: The user's answer text
            
        Returns:
            dict: Extracted entities (characters, plot_events, settings)
        """
        pass


class EditingAgentInterface(BaseAgent):
    """Interface for editing agents.
    
    Editing agents provide AI-assisted text editing operations that are
    grounded in the Truth knowledge base and previous chapter context.
    """
    
    @abstractmethod
    def improve_text(
        self, 
        text: str, 
        chapter: Any, 
        all_chapters: list[Any]
    ) -> str:
        """Improve the quality of text while maintaining consistency.
        
        Args:
            text: Text to improve
            chapter: Current chapter object
            all_chapters: List of all chapters for context
            
        Returns:
            str: Improved text
        """
        pass
    
    @abstractmethod
    def expand_text(
        self, 
        text: str, 
        chapter: Any, 
        all_chapters: list[Any]
    ) -> str:
        """Expand text with additional details.
        
        Args:
            text: Text to expand
            chapter: Current chapter object
            all_chapters: List of all chapters for context
            
        Returns:
            str: Expanded text
        """
        pass
    
    @abstractmethod
    def rephrase_text(
        self, 
        text: str, 
        chapter: Any, 
        all_chapters: list[Any]
    ) -> str:
        """Rephrase text with alternative wording.
        
        Args:
            text: Text to rephrase
            chapter: Current chapter object
            all_chapters: List of all chapters for context
            
        Returns:
            str: Rephrased text
        """
        pass
    
    @abstractmethod
    def suggest_next_chapter(self, all_chapters: list[Any]) -> str:
        """Suggest what should happen in the next chapter.
        
        Args:
            all_chapters: List of all chapters for context
            
        Returns:
            str: Suggestion for next chapter
        """
        pass
    
    @abstractmethod
    def create_editing_prompt(
        self, 
        action: str, 
        text: str, 
        context: dict[str, Any]
    ) -> str:
        """Create a prompt for an editing action.
        
        Args:
            action: Type of editing action (improve, expand, rephrase)
            text: Text to edit
            context: Context information from Truth and chapters
            
        Returns:
            str: Formatted prompt for LLM
        """
        pass
