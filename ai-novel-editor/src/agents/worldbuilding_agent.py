"""WorldBuilding Agent for interactive story development.

This agent conducts Q&A sessions to build the Truth knowledge base through
entity extraction and dynamic question generation.
"""

import logging
from typing import Any, Optional
from datetime import datetime

from .base import WorldBuildingAgentInterface
from ..models.truth import (
    TruthKnowledgeBase,
    QuestionTree,
    QuestionNode,
    QuestionStatus,
    EntityType,
    Character,
    PlotEvent,
    Setting
)
from ..services.llm_service import LLMService


logger = logging.getLogger(__name__)


class WorldBuildingAgent(WorldBuildingAgentInterface):
    """Agent for conducting interactive world-building Q&A sessions.
    
    This agent:
    1. Initializes question trees from initial story descriptions
    2. Extracts entities (characters, plot events, settings) from answers
    3. Generates follow-up questions based on identified entities
    4. Performs cross-branch analysis to update question statuses
    5. Maintains the Truth knowledge base
    """
    
    INITIAL_QUESTION = "What is your story about?"
    
    def __init__(self, truth: TruthKnowledgeBase, llm_service: LLMService):
        """Initialize the WorldBuilding agent.
        
        Args:
            truth: The Truth knowledge base for this project
            llm_service: LLM service for text generation and extraction
        """
        super().__init__(truth)
        self.llm_service = llm_service
    
    def is_ready(self) -> bool:
        """Check if the agent is ready to perform operations.
        
        Returns:
            bool: True if LLM service is available
        """
        return self.llm_service.is_available()
    
    def initialize_question_tree(self, initial_answer: str) -> None:
        """Initialize the question tree with the first answer.
        
        Creates the root question node with the initial "What is your story about?"
        question and the user's answer. Extracts initial entities and generates
        first set of follow-up questions.
        
        Args:
            initial_answer: User's answer to "What is your story about?"
        """
        logger.info("Initializing question tree with initial answer")
        
        # Create root question node
        root_node = QuestionNode(
            question=self.INITIAL_QUESTION,
            answer=initial_answer,
            entity_type=EntityType.WORLD_BUILDING,
            status=QuestionStatus.ANSWERED,
            answered_at=datetime.now()
        )
        
        # Create question tree with root node
        question_tree = QuestionTree(root_id=root_node.id)
        question_tree.add_node(root_node)
        
        # Set the question tree in Truth
        self.truth.question_tree = question_tree
        
        # Extract entities from initial answer
        try:
            entities = self.extract_entities(initial_answer)
            logger.info(f"Extracted {len(entities.get('characters', []))} characters, "
                       f"{len(entities.get('plot_events', []))} plot events, "
                       f"{len(entities.get('settings', []))} settings")
        except Exception as e:
            logger.error(f"Failed to extract entities from initial answer: {e}")
        
        # Generate follow-up questions
        try:
            follow_up_questions = self.generate_follow_up_questions(
                initial_answer,
                root_node.id
            )
            logger.info(f"Generated {len(follow_up_questions)} follow-up questions")
        except Exception as e:
            logger.error(f"Failed to generate follow-up questions: {e}")

    def extract_entities(self, answer: str) -> dict[str, Any]:
        """Extract story entities from an answer.
        
        Uses LLM with JSON schema to extract structured information about
        characters, plot events, and settings mentioned in the answer.
        Updates the Truth knowledge base with extracted entities.
        
        Args:
            answer: The user's answer text
            
        Returns:
            dict: Extracted entities with keys 'characters', 'plot_events', 'settings'
        """
        logger.info("Extracting entities from answer")
        
        # Define JSON schema for entity extraction
        schema = {
            "type": "object",
            "properties": {
                "characters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "traits": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "role": {"type": "string"}
                        },
                        "required": ["name"]
                    }
                },
                "plot_events": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "order": {"type": "integer"},
                            "significance": {"type": "string"}
                        },
                        "required": ["title", "description"]
                    }
                },
                "settings": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"type": "string"},
                            "description": {"type": "string"}
                        },
                        "required": ["name", "type", "description"]
                    }
                }
            },
            "required": ["characters", "plot_events", "settings"]
        }
        
        # Create extraction prompt
        prompt = f"""Analyze the following story description and extract all mentioned entities.

Story Description:
{answer}

Extract:
1. Characters: Any people, creatures, or beings mentioned. Include their name, description, traits, and role.
2. Plot Events: Any events, conflicts, or story beats mentioned. Include title, description, chronological order (0 for earliest), and significance.
3. Settings: Any locations, magic systems, organizations, or important objects mentioned. Include name, type (location/magic_system/organization/object), and description.

Be thorough but only extract entities that are explicitly or implicitly mentioned in the text.
If no entities of a type are found, return an empty array for that type."""

        try:
            # Extract entities using LLM with JSON schema
            extracted = self.llm_service.generate_with_json_schema(
                prompt=prompt,
                schema=schema
            )
            
            # Update Truth knowledge base with extracted entities
            self._update_truth_with_entities(extracted)
            
            return extracted
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            # Return empty structure on failure
            return {
                "characters": [],
                "plot_events": [],
                "settings": []
            }
    
    def _update_truth_with_entities(self, entities: dict[str, Any]) -> None:
        """Update the Truth knowledge base with extracted entities.
        
        Args:
            entities: Dictionary containing extracted characters, plot_events, settings
        """
        # Add characters
        for char_data in entities.get("characters", []):
            character = Character(
                name=char_data["name"],
                description=char_data.get("description", ""),
                traits=char_data.get("traits", []),
                role=char_data.get("role", "")
            )
            self.truth.add_character(character)
            logger.debug(f"Added character: {character.name}")
        
        # Add plot events
        for event_data in entities.get("plot_events", []):
            plot_event = PlotEvent(
                title=event_data["title"],
                description=event_data.get("description", ""),
                order=event_data.get("order", 0),
                significance=event_data.get("significance", "")
            )
            self.truth.add_plot_event(plot_event)
            logger.debug(f"Added plot event: {plot_event.title}")
        
        # Add settings
        for setting_data in entities.get("settings", []):
            setting = Setting(
                name=setting_data["name"],
                type=setting_data.get("type", "location"),
                description=setting_data.get("description", "")
            )
            self.truth.add_setting(setting)
            logger.debug(f"Added setting: {setting.name}")

    def generate_follow_up_questions(
        self, 
        answer: str, 
        parent_id: str
    ) -> list[QuestionNode]:
        """Generate follow-up questions based on an answer.
        
        Analyzes the answer to identify key entities and concepts, then generates
        2-5 follow-up questions per entity. Questions are categorized by entity type
        and added as children in the QuestionTree.
        
        Args:
            answer: The user's answer text
            parent_id: ID of the parent question node
            
        Returns:
            list: List of generated QuestionNode objects
        """
        logger.info(f"Generating follow-up questions for parent {parent_id}")
        
        if not self.truth.question_tree:
            logger.error("Question tree not initialized")
            return []
        
        # Get current Truth context for question generation
        context = self._build_question_context()
        
        # Define JSON schema for question generation
        schema = {
            "type": "object",
            "properties": {
                "questions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string"},
                            "entity_type": {
                                "type": "string",
                                "enum": ["character", "plot_event", "setting", "world_building"]
                            },
                            "related_entity_name": {"type": "string"}
                        },
                        "required": ["question", "entity_type"]
                    }
                }
            },
            "required": ["questions"]
        }
        
        # Create question generation prompt
        prompt = f"""Based on the following answer, generate 2-5 insightful follow-up questions to deepen the story world.

Answer:
{answer}

Current Story Context:
{context}

Generate questions that:
1. Explore character motivations, backgrounds, and relationships
2. Clarify plot events, conflicts, and story structure
3. Develop settings, world-building, and atmosphere
4. Fill gaps in the story world
5. Build on what's already established

For each question, specify:
- question: The question text
- entity_type: Type of entity (character, plot_event, setting, world_building)
- related_entity_name: Name of the specific entity this question relates to (if applicable)

Generate 2-5 questions total. Focus on the most important aspects that need development."""

        try:
            # Generate questions using LLM
            result = self.llm_service.generate_with_json_schema(
                prompt=prompt,
                schema=schema
            )
            
            # Create QuestionNode objects and add to tree
            generated_nodes = []
            for q_data in result.get("questions", []):
                node = QuestionNode(
                    question=q_data["question"],
                    entity_type=EntityType(q_data["entity_type"]),
                    status=QuestionStatus.PENDING,
                    parent_id=parent_id
                )
                
                # Add related entity name to metadata if provided
                if q_data.get("related_entity_name"):
                    node.metadata["related_entity_name"] = q_data["related_entity_name"]
                
                # Add node to question tree
                self.truth.question_tree.add_node(node, parent_id)
                generated_nodes.append(node)
                logger.debug(f"Generated question: {node.question}")
            
            logger.info(f"Generated {len(generated_nodes)} follow-up questions")
            return generated_nodes
            
        except Exception as e:
            logger.error(f"Question generation failed: {e}")
            return []
    
    def _build_question_context(self) -> str:
        """Build a context string from current Truth for question generation.
        
        Returns:
            str: Formatted context string with characters, plot events, and settings
        """
        context_parts = []
        
        # Add characters
        if self.truth.characters:
            char_list = [f"- {c.name}: {c.description}" for c in self.truth.characters.values()]
            context_parts.append(f"Characters:\n" + "\n".join(char_list))
        
        # Add plot events
        if self.truth.plot_events:
            event_list = [f"- {e.title}: {e.description}" for e in self.truth.plot_events.values()]
            context_parts.append(f"Plot Events:\n" + "\n".join(event_list))
        
        # Add settings
        if self.truth.settings:
            setting_list = [f"- {s.name} ({s.type}): {s.description}" for s in self.truth.settings.values()]
            context_parts.append(f"Settings:\n" + "\n".join(setting_list))
        
        if not context_parts:
            return "No entities established yet."
        
        return "\n\n".join(context_parts)

    def analyze_cross_branch_impact(self, new_answer: str, answered_node_id: str) -> None:
        """Analyze new answers against entire QuestionTree.
        
        Identifies questions that may be partially or fully answered by new information.
        Updates question status and links related questions via related_entity_ids.
        
        Args:
            new_answer: The newly provided answer text
            answered_node_id: ID of the question that was just answered
        """
        logger.info("Performing cross-branch analysis")
        
        if not self.truth.question_tree:
            logger.error("Question tree not initialized")
            return
        
        # Get all pending questions
        pending_questions = self.truth.question_tree.get_pending_questions()
        
        if not pending_questions:
            logger.info("No pending questions to analyze")
            return
        
        # Build context for analysis
        questions_text = "\n".join([
            f"{i+1}. (ID: {q.id}) {q.question}"
            for i, q in enumerate(pending_questions)
        ])
        
        # Define JSON schema for cross-branch analysis
        schema = {
            "type": "object",
            "properties": {
                "affected_questions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "question_id": {"type": "string"},
                            "status": {
                                "type": "string",
                                "enum": ["answered", "partially_answered", "pending"]
                            },
                            "explanation": {"type": "string"}
                        },
                        "required": ["question_id", "status"]
                    }
                }
            },
            "required": ["affected_questions"]
        }
        
        # Create analysis prompt
        prompt = f"""Analyze whether the following answer provides information that answers or partially answers any of the pending questions.

New Answer:
{new_answer}

Pending Questions:
{questions_text}

For each question that is affected by this answer:
- question_id: The ID of the affected question
- status: "answered" if fully answered, "partially_answered" if some information provided, "pending" if not affected
- explanation: Brief explanation of what information was provided

Only include questions that are actually affected by the new answer. If no questions are affected, return an empty array."""

        try:
            # Analyze using LLM
            result = self.llm_service.generate_with_json_schema(
                prompt=prompt,
                schema=schema,
                temperature=0.3  # Lower temperature for analytical task
            )
            
            # Update affected questions
            affected_count = 0
            for affected in result.get("affected_questions", []):
                question_id = affected["question_id"]
                new_status = QuestionStatus(affected["status"])
                
                # Only update if status changed
                node = self.truth.question_tree.get_node(question_id)
                if node and node.status != new_status:
                    self.truth.question_tree.update_node_status(question_id, new_status)
                    
                    # Link related questions
                    if answered_node_id not in node.related_entity_ids:
                        node.related_entity_ids.append(answered_node_id)
                    
                    # Store explanation in metadata
                    node.metadata["cross_branch_info"] = affected.get("explanation", "")
                    
                    affected_count += 1
                    logger.debug(f"Updated question {question_id} to {new_status}")
            
            logger.info(f"Cross-branch analysis affected {affected_count} questions")
            
        except Exception as e:
            logger.error(f"Cross-branch analysis failed: {e}")

    def answer_question(self, question_id: str, answer: str) -> list[QuestionNode]:
        """Process a user's answer to a question.
        
        This method orchestrates the complete answer processing workflow:
        1. Updates the QuestionNode with the answer and status
        2. Triggers entity extraction from the answer
        3. Performs cross-branch analysis to update related questions
        4. Generates follow-up questions based on the answer
        
        Args:
            question_id: ID of the question being answered
            answer: The user's answer text
            
        Returns:
            list: List of newly generated QuestionNode objects
        """
        logger.info(f"Processing answer for question {question_id}")
        
        if not self.truth.question_tree:
            logger.error("Question tree not initialized")
            return []
        
        # Get the question node
        node = self.truth.question_tree.get_node(question_id)
        if not node:
            logger.error(f"Question node {question_id} not found")
            return []
        
        # Update node with answer and status
        node.answer = answer
        node.status = QuestionStatus.ANSWERED
        node.answered_at = datetime.now()
        logger.debug(f"Updated question node with answer")
        
        # Extract entities from the answer
        try:
            entities = self.extract_entities(answer)
            logger.info(f"Extracted entities: {len(entities.get('characters', []))} characters, "
                       f"{len(entities.get('plot_events', []))} plot events, "
                       f"{len(entities.get('settings', []))} settings")
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
        
        # Perform cross-branch analysis
        try:
            self.analyze_cross_branch_impact(answer, question_id)
        except Exception as e:
            logger.error(f"Cross-branch analysis failed: {e}")
        
        # Generate follow-up questions
        try:
            new_questions = self.generate_follow_up_questions(answer, question_id)
            logger.info(f"Generated {len(new_questions)} new follow-up questions")
            return new_questions
        except Exception as e:
            logger.error(f"Follow-up question generation failed: {e}")
            return []
