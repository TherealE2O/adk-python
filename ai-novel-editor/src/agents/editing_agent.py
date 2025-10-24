"""Editing Agent for AI-assisted text editing and generation.

This agent provides context-aware editing operations grounded in the Truth
knowledge base and previous chapter content to maintain consistency.
"""

import logging
from typing import Any, Optional
from datetime import datetime

from .base import EditingAgentInterface
from ..models.truth import TruthKnowledgeBase
from ..models.project import Chapter
from ..services.llm_service import LLMService


logger = logging.getLogger(__name__)


class EditingAgent(EditingAgentInterface):
    """Agent for AI-assisted text editing and generation.
    
    This agent:
    1. Builds context from Truth and previous chapters
    2. Provides text editing operations (improve, expand, rephrase)
    3. Generates auto-completions and new paragraphs
    4. Performs chapter-level operations (edit, suggest, plan)
    5. Ensures all operations maintain consistency with established facts
    """
    
    def __init__(self, truth: TruthKnowledgeBase, llm_service: LLMService):
        """Initialize the Editing agent.
        
        Args:
            truth: The Truth knowledge base for this project
            llm_service: LLM service for text generation
        """
        super().__init__(truth)
        self.llm_service = llm_service
    
    def is_ready(self) -> bool:
        """Check if the agent is ready to perform operations.
        
        Returns:
            bool: True if LLM service is available
        """
        return self.llm_service.is_available()
    
    def build_context(
        self,
        chapter: Chapter,
        all_chapters: list[Chapter]
    ) -> dict[str, Any]:
        """Build context dictionary from Truth and chapter information.
        
        Gathers all relevant context for AI editing operations including:
        - Characters with their traits, descriptions, and relationships
        - Plot events in chronological order
        - Settings and world-building elements
        - Previous chapters with summaries
        - Current chapter metadata
        
        Args:
            chapter: Current chapter being edited
            all_chapters: List of all chapters in the project
            
        Returns:
            dict: Context dictionary with truth, previous_chapters, and current_chapter
        """
        logger.debug(f"Building context for chapter {chapter.number}")
        
        # Serialize Truth entities
        truth_context = {
            "characters": [
                {
                    "name": char.name,
                    "description": char.description,
                    "traits": char.traits,
                    "role": char.role,
                    "backstory": char.backstory,
                    "relationships": char.relationships
                }
                for char in self.truth.characters.values()
            ],
            "plot_events": [
                {
                    "title": event.title,
                    "description": event.description,
                    "order": event.order,
                    "significance": event.significance,
                    "characters_involved": event.characters_involved,
                    "location": event.location
                }
                for event in sorted(
                    self.truth.plot_events.values(),
                    key=lambda e: e.order
                )
            ],
            "settings": [
                {
                    "name": setting.name,
                    "type": setting.type,
                    "description": setting.description,
                    "rules": setting.rules
                }
                for setting in self.truth.settings.values()
            ]
        }
        
        # Get previous chapters (sorted by number, only those before current)
        previous_chapters = [
            ch for ch in sorted(all_chapters, key=lambda c: c.number)
            if ch.number < chapter.number
        ]
        
        # Serialize previous chapters with summaries
        previous_chapters_context = [
            {
                "number": ch.number,
                "title": ch.title,
                "summary": self._create_chapter_summary(ch),
                "word_count": ch.word_count
            }
            for ch in previous_chapters
        ]
        
        # Current chapter metadata
        current_chapter_context = {
            "number": chapter.number,
            "title": chapter.title,
            "word_count": chapter.word_count,
            "outline": chapter.outline if hasattr(chapter, 'outline') else ""
        }
        
        return {
            "truth": truth_context,
            "previous_chapters": previous_chapters_context,
            "current_chapter": current_chapter_context
        }
    
    def _create_chapter_summary(self, chapter: Chapter) -> str:
        """Create a summary of a chapter for context.
        
        Uses the first 500 characters as a summary. For longer chapters,
        this provides enough context without overwhelming the prompt.
        
        Args:
            chapter: Chapter to summarize
            
        Returns:
            str: Chapter summary (first 500 characters)
        """
        if not chapter.content:
            return "[Empty chapter]"
        
        summary = chapter.content[:500]
        if len(chapter.content) > 500:
            summary += "..."
        
        return summary

    def create_editing_prompt(
        self,
        action: str,
        text: str,
        context: dict[str, Any]
    ) -> str:
        """Create a prompt for an editing action with full context.
        
        Builds a comprehensive prompt that includes:
        - The editing action to perform
        - The text to edit
        - Truth context (characters, plot events, settings)
        - Previous chapter context
        - Current chapter metadata
        
        Args:
            action: Type of editing action (improve, expand, rephrase)
            text: Text to edit
            context: Context dictionary from build_context()
            
        Returns:
            str: Formatted prompt for LLM
        """
        logger.debug(f"Creating editing prompt for action: {action}")
        
        # Build Truth context section
        truth_section = self._format_truth_context(context["truth"])
        
        # Build previous chapters section
        prev_chapters_section = self._format_previous_chapters(context["previous_chapters"])
        
        # Build current chapter section
        current_chapter = context["current_chapter"]
        current_section = f"""CURRENT CHAPTER:
Chapter {current_chapter['number']}: {current_chapter['title']}
Word Count: {current_chapter['word_count']}"""
        
        if current_chapter.get('outline'):
            current_section += f"\nOutline: {current_chapter['outline']}"
        
        # Build action-specific instructions
        action_instructions = self._get_action_instructions(action)
        
        # Assemble full prompt
        prompt = f"""{truth_section}

{prev_chapters_section}

{current_section}

{action_instructions}

TEXT TO EDIT:
{text}

EDITED TEXT:"""
        
        return prompt
    
    def _format_truth_context(self, truth: dict[str, Any]) -> str:
        """Format Truth context for prompt inclusion.
        
        Args:
            truth: Truth context dictionary
            
        Returns:
            str: Formatted Truth context
        """
        sections = []
        
        # Characters
        if truth["characters"]:
            char_lines = ["ESTABLISHED CHARACTERS:"]
            for char in truth["characters"]:
                char_lines.append(f"\n- {char['name']}")
                if char.get('description'):
                    char_lines.append(f"  Description: {char['description']}")
                if char.get('traits'):
                    char_lines.append(f"  Traits: {', '.join(char['traits'])}")
                if char.get('role'):
                    char_lines.append(f"  Role: {char['role']}")
            sections.append("\n".join(char_lines))
        
        # Plot Events
        if truth["plot_events"]:
            event_lines = ["ESTABLISHED PLOT EVENTS:"]
            for event in truth["plot_events"]:
                event_lines.append(f"\n- {event['title']}")
                if event.get('description'):
                    event_lines.append(f"  {event['description']}")
                if event.get('significance'):
                    event_lines.append(f"  Significance: {event['significance']}")
            sections.append("\n".join(event_lines))
        
        # Settings
        if truth["settings"]:
            setting_lines = ["ESTABLISHED SETTINGS:"]
            for setting in truth["settings"]:
                setting_lines.append(f"\n- {setting['name']} ({setting['type']})")
                if setting.get('description'):
                    setting_lines.append(f"  {setting['description']}")
            sections.append("\n".join(setting_lines))
        
        if not sections:
            return "ESTABLISHED STORY FACTS:\n[No established facts yet]"
        
        return "\n\n".join(sections)
    
    def _format_previous_chapters(self, prev_chapters: list[dict]) -> str:
        """Format previous chapters for prompt inclusion.
        
        Args:
            prev_chapters: List of previous chapter dictionaries
            
        Returns:
            str: Formatted previous chapters context
        """
        if not prev_chapters:
            return "PREVIOUS CHAPTERS:\n[This is the first chapter]"
        
        lines = ["PREVIOUS CHAPTERS:"]
        for ch in prev_chapters:
            lines.append(f"\nChapter {ch['number']}: {ch['title']}")
            lines.append(f"Summary: {ch['summary']}")
        
        return "\n".join(lines)
    
    def _get_action_instructions(self, action: str) -> str:
        """Get specific instructions for an editing action.
        
        Args:
            action: Type of editing action
            
        Returns:
            str: Action-specific instructions
        """
        instructions = {
            "improve": """TASK: Improve the quality of the text while maintaining consistency.

Instructions:
- Enhance clarity, flow, and readability
- Strengthen word choice and sentence structure
- Maintain the author's voice and style
- Ensure consistency with established characters, plot events, and settings
- Keep the same meaning and content, just improve the expression
- Do not add new information or change the plot""",
            
            "expand": """TASK: Expand the text with additional details and depth.

Instructions:
- Add sensory details, descriptions, and atmosphere
- Develop character emotions and internal thoughts
- Expand dialogue with subtext and body language
- Include relevant world-building details from established settings
- Maintain consistency with character traits and plot events
- Keep the original content and build upon it naturally""",
            
            "rephrase": """TASK: Rephrase the text with alternative wording.

Instructions:
- Rewrite using different sentence structures and vocabulary
- Maintain the same meaning and information
- Keep consistency with established story facts
- Preserve the tone and style appropriate for the scene
- Offer a fresh perspective on the same content
- Do not add or remove information"""
        }
        
        return instructions.get(
            action,
            "TASK: Edit the text while maintaining consistency with established story facts."
        )
    
    def improve_text(
        self,
        text: str,
        chapter: Chapter,
        all_chapters: list[Chapter]
    ) -> str:
        """Improve the quality of text while maintaining consistency.
        
        Enhances clarity, flow, and readability while ensuring consistency
        with established characters, plot events, and settings from Truth.
        
        Args:
            text: Text to improve
            chapter: Current chapter object
            all_chapters: List of all chapters for context
            
        Returns:
            str: Improved text
            
        Raises:
            ValueError: If service is not available
            RuntimeError: If generation fails
        """
        logger.info("Improving text")
        
        if not self.is_ready():
            raise ValueError("Editing agent is not ready. LLM service unavailable.")
        
        # Build context
        context = self.build_context(chapter, all_chapters)
        
        # Create prompt
        prompt = self.create_editing_prompt("improve", text, context)
        
        # Generate improved text
        try:
            improved = self.llm_service.generate_text(
                prompt=prompt,
                temperature=0.7  # Creative but controlled
            )
            logger.debug("Text improvement completed")
            return improved.strip()
        except Exception as e:
            logger.error(f"Failed to improve text: {e}")
            raise RuntimeError(f"Failed to improve text: {str(e)}") from e
    
    def expand_text(
        self,
        text: str,
        chapter: Chapter,
        all_chapters: list[Chapter]
    ) -> str:
        """Expand text with additional details and depth.
        
        Adds sensory details, character emotions, and world-building elements
        while maintaining consistency with Truth and previous chapters.
        
        Args:
            text: Text to expand
            chapter: Current chapter object
            all_chapters: List of all chapters for context
            
        Returns:
            str: Expanded text
            
        Raises:
            ValueError: If service is not available
            RuntimeError: If generation fails
        """
        logger.info("Expanding text")
        
        if not self.is_ready():
            raise ValueError("Editing agent is not ready. LLM service unavailable.")
        
        # Build context
        context = self.build_context(chapter, all_chapters)
        
        # Create prompt
        prompt = self.create_editing_prompt("expand", text, context)
        
        # Generate expanded text
        try:
            expanded = self.llm_service.generate_text(
                prompt=prompt,
                temperature=0.8  # More creative for expansion
            )
            logger.debug("Text expansion completed")
            return expanded.strip()
        except Exception as e:
            logger.error(f"Failed to expand text: {e}")
            raise RuntimeError(f"Failed to expand text: {str(e)}") from e
    
    def rephrase_text(
        self,
        text: str,
        chapter: Chapter,
        all_chapters: list[Chapter]
    ) -> str:
        """Rephrase text with alternative wording.
        
        Rewrites text using different sentence structures and vocabulary
        while maintaining the same meaning and consistency with Truth.
        
        Args:
            text: Text to rephrase
            chapter: Current chapter object
            all_chapters: List of all chapters for context
            
        Returns:
            str: Rephrased text
            
        Raises:
            ValueError: If service is not available
            RuntimeError: If generation fails
        """
        logger.info("Rephrasing text")
        
        if not self.is_ready():
            raise ValueError("Editing agent is not ready. LLM service unavailable.")
        
        # Build context
        context = self.build_context(chapter, all_chapters)
        
        # Create prompt
        prompt = self.create_editing_prompt("rephrase", text, context)
        
        # Generate rephrased text
        try:
            rephrased = self.llm_service.generate_text(
                prompt=prompt,
                temperature=0.7  # Balanced creativity
            )
            logger.debug("Text rephrasing completed")
            return rephrased.strip()
        except Exception as e:
            logger.error(f"Failed to rephrase text: {e}")
            raise RuntimeError(f"Failed to rephrase text: {str(e)}") from e

    def suggest_completion(
        self,
        text: str,
        chapter: Chapter,
        all_chapters: list[Chapter]
    ) -> str:
        """Suggest completion for a paragraph in progress.
        
        Generates a natural continuation of the text that maintains
        consistency with Truth and previous chapters.
        
        Args:
            text: Text to complete (partial paragraph)
            chapter: Current chapter object
            all_chapters: List of all chapters for context
            
        Returns:
            str: Suggested completion text
            
        Raises:
            ValueError: If service is not available
            RuntimeError: If generation fails
        """
        logger.info("Suggesting completion")
        
        if not self.is_ready():
            raise ValueError("Editing agent is not ready. LLM service unavailable.")
        
        # Build context
        context = self.build_context(chapter, all_chapters)
        
        # Build Truth context section
        truth_section = self._format_truth_context(context["truth"])
        
        # Build previous chapters section
        prev_chapters_section = self._format_previous_chapters(context["previous_chapters"])
        
        # Build current chapter section
        current_chapter = context["current_chapter"]
        current_section = f"""CURRENT CHAPTER:
Chapter {current_chapter['number']}: {current_chapter['title']}"""
        
        # Create completion prompt
        prompt = f"""{truth_section}

{prev_chapters_section}

{current_section}

TASK: Continue the following text naturally and coherently.

Instructions:
- Write a natural continuation that flows from the existing text
- Maintain consistency with established characters, plot events, and settings
- Match the tone and style of the existing text
- Keep the completion focused and relevant to the current scene
- Provide 1-3 sentences to complete the thought or paragraph

TEXT TO COMPLETE:
{text}

COMPLETION:"""
        
        # Generate completion
        try:
            completion = self.llm_service.generate_text(
                prompt=prompt,
                temperature=0.8,  # Creative for natural continuation
                max_tokens=200  # Limit to paragraph-level completion
            )
            logger.debug("Completion suggestion generated")
            return completion.strip()
        except Exception as e:
            logger.error(f"Failed to suggest completion: {e}")
            raise RuntimeError(f"Failed to suggest completion: {str(e)}") from e
    
    def generate_paragraph(
        self,
        instruction: str,
        chapter: Chapter,
        all_chapters: list[Chapter]
    ) -> str:
        """Generate a new paragraph based on user instruction.
        
        Creates new content based on the user's instruction while ensuring
        consistency with Truth and previous chapters.
        
        Args:
            instruction: User's instruction for what to write
            chapter: Current chapter object
            all_chapters: List of all chapters for context
            
        Returns:
            str: Generated paragraph
            
        Raises:
            ValueError: If service is not available
            RuntimeError: If generation fails
        """
        logger.info(f"Generating paragraph from instruction: {instruction}")
        
        if not self.is_ready():
            raise ValueError("Editing agent is not ready. LLM service unavailable.")
        
        # Build context
        context = self.build_context(chapter, all_chapters)
        
        # Build Truth context section
        truth_section = self._format_truth_context(context["truth"])
        
        # Build previous chapters section
        prev_chapters_section = self._format_previous_chapters(context["previous_chapters"])
        
        # Build current chapter section
        current_chapter = context["current_chapter"]
        current_section = f"""CURRENT CHAPTER:
Chapter {current_chapter['number']}: {current_chapter['title']}
Word Count: {current_chapter['word_count']}"""
        
        if current_chapter.get('outline'):
            current_section += f"\nOutline: {current_chapter['outline']}"
        
        # Get chapter content for additional context
        chapter_content = ""
        if chapter.content:
            # Include last 500 characters for immediate context
            chapter_content = f"\n\nCURRENT CHAPTER CONTENT (excerpt):\n...{chapter.content[-500:]}"
        
        # Create generation prompt
        prompt = f"""{truth_section}

{prev_chapters_section}

{current_section}{chapter_content}

TASK: Write a paragraph based on the following instruction.

Instructions:
- Follow the user's instruction for what to write
- Maintain consistency with established characters, plot events, and settings
- Ensure continuity with previous chapters and current chapter content
- Match the tone and style appropriate for this story
- Write a complete, well-formed paragraph

USER INSTRUCTION:
{instruction}

GENERATED PARAGRAPH:"""
        
        # Generate paragraph
        try:
            paragraph = self.llm_service.generate_text(
                prompt=prompt,
                temperature=0.8,  # Creative for generation
                max_tokens=500  # Allow for full paragraph
            )
            logger.debug("Paragraph generation completed")
            return paragraph.strip()
        except Exception as e:
            logger.error(f"Failed to generate paragraph: {e}")
            raise RuntimeError(f"Failed to generate paragraph: {str(e)}") from e

    def edit_chapter(
        self,
        chapter: Chapter,
        all_chapters: list[Chapter]
    ) -> str:
        """Edit and revise an entire chapter for consistency.
        
        Performs a comprehensive revision of the chapter content to ensure
        consistency with Truth and previous chapters, improving quality
        throughout.
        
        Args:
            chapter: Chapter to edit
            all_chapters: List of all chapters for context
            
        Returns:
            str: Revised chapter content
            
        Raises:
            ValueError: If service is not available or chapter is empty
            RuntimeError: If generation fails
        """
        logger.info(f"Editing chapter {chapter.number}: {chapter.title}")
        
        if not self.is_ready():
            raise ValueError("Editing agent is not ready. LLM service unavailable.")
        
        if not chapter.content:
            raise ValueError("Cannot edit empty chapter. Please add content first.")
        
        # Build context
        context = self.build_context(chapter, all_chapters)
        
        # Build Truth context section
        truth_section = self._format_truth_context(context["truth"])
        
        # Build previous chapters section
        prev_chapters_section = self._format_previous_chapters(context["previous_chapters"])
        
        # Build current chapter section
        current_chapter = context["current_chapter"]
        current_section = f"""CURRENT CHAPTER:
Chapter {current_chapter['number']}: {current_chapter['title']}"""
        
        if current_chapter.get('outline'):
            current_section += f"\nOutline: {current_chapter['outline']}"
        
        # Create chapter editing prompt
        prompt = f"""{truth_section}

{prev_chapters_section}

{current_section}

TASK: Revise and improve the entire chapter content.

Instructions:
- Ensure consistency with all established characters, plot events, and settings
- Maintain continuity with previous chapters
- Improve clarity, flow, and readability throughout
- Enhance descriptions, dialogue, and pacing
- Keep the core content and plot progression
- Maintain the author's voice and style
- Fix any inconsistencies or continuity errors

CHAPTER CONTENT TO EDIT:
{chapter.content}

REVISED CHAPTER:"""
        
        # Generate revised chapter
        try:
            revised = self.llm_service.generate_text(
                prompt=prompt,
                temperature=0.7,  # Balanced for editing
                max_tokens=8192  # Allow for full chapter
            )
            logger.debug("Chapter editing completed")
            return revised.strip()
        except Exception as e:
            logger.error(f"Failed to edit chapter: {e}")
            raise RuntimeError(f"Failed to edit chapter: {str(e)}") from e
    
    def suggest_next_chapter(
        self,
        all_chapters: list[Chapter]
    ) -> str:
        """Suggest what should happen in the next chapter.
        
        Analyzes current progress and Truth to suggest the next chapter's
        content, maintaining plot consistency and narrative momentum.
        
        Args:
            all_chapters: List of all chapters for context
            
        Returns:
            str: Suggestion for next chapter content and direction
            
        Raises:
            ValueError: If service is not available
            RuntimeError: If generation fails
        """
        logger.info("Suggesting next chapter")
        
        if not self.is_ready():
            raise ValueError("Editing agent is not ready. LLM service unavailable.")
        
        # Build Truth context
        truth_context = {
            "characters": [
                {
                    "name": char.name,
                    "description": char.description,
                    "traits": char.traits,
                    "role": char.role
                }
                for char in self.truth.characters.values()
            ],
            "plot_events": [
                {
                    "title": event.title,
                    "description": event.description,
                    "order": event.order,
                    "significance": event.significance
                }
                for event in sorted(
                    self.truth.plot_events.values(),
                    key=lambda e: e.order
                )
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
        
        # Build Truth context section
        truth_section = self._format_truth_context(truth_context)
        
        # Build all chapters summary
        sorted_chapters = sorted(all_chapters, key=lambda c: c.number)
        chapters_summary = []
        for ch in sorted_chapters:
            summary = self._create_chapter_summary(ch)
            chapters_summary.append(
                f"Chapter {ch.number}: {ch.title}\n{summary}"
            )
        
        chapters_section = "STORY SO FAR:\n\n" + "\n\n".join(chapters_summary)
        
        if not chapters_summary:
            chapters_section = "STORY SO FAR:\n[No chapters written yet]"
        
        # Create suggestion prompt
        prompt = f"""{truth_section}

{chapters_section}

TASK: Suggest what should happen in the next chapter.

Instructions:
- Analyze the story's current state and progression
- Consider which plot events from the Truth should be addressed next
- Identify character arcs that need development
- Suggest specific scenes, conflicts, or developments
- Maintain narrative momentum and pacing
- Ensure the suggestion aligns with established plot events and character motivations
- Provide concrete, actionable suggestions for the next chapter

NEXT CHAPTER SUGGESTION:"""
        
        # Generate suggestion
        try:
            suggestion = self.llm_service.generate_text(
                prompt=prompt,
                temperature=0.7,  # Balanced creativity
                max_tokens=1000  # Allow for detailed suggestion
            )
            logger.debug("Next chapter suggestion generated")
            return suggestion.strip()
        except Exception as e:
            logger.error(f"Failed to suggest next chapter: {e}")
            raise RuntimeError(f"Failed to suggest next chapter: {str(e)}") from e
    
    def plan_chapter(
        self,
        chapter_number: int,
        chapter_title: str,
        all_chapters: list[Chapter]
    ) -> str:
        """Generate an outline for a chapter.
        
        Creates a detailed chapter outline based on the chapter title,
        current story progress, and established Truth.
        
        Args:
            chapter_number: Number of the chapter to plan
            chapter_title: Title of the chapter to plan
            all_chapters: List of all chapters for context
            
        Returns:
            str: Chapter outline with scenes and key points
            
        Raises:
            ValueError: If service is not available
            RuntimeError: If generation fails
        """
        logger.info(f"Planning chapter {chapter_number}: {chapter_title}")
        
        if not self.is_ready():
            raise ValueError("Editing agent is not ready. LLM service unavailable.")
        
        # Build Truth context
        truth_context = {
            "characters": [
                {
                    "name": char.name,
                    "description": char.description,
                    "traits": char.traits,
                    "role": char.role
                }
                for char in self.truth.characters.values()
            ],
            "plot_events": [
                {
                    "title": event.title,
                    "description": event.description,
                    "order": event.order,
                    "significance": event.significance
                }
                for event in sorted(
                    self.truth.plot_events.values(),
                    key=lambda e: e.order
                )
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
        
        # Build Truth context section
        truth_section = self._format_truth_context(truth_context)
        
        # Build previous chapters summary
        previous_chapters = [
            ch for ch in sorted(all_chapters, key=lambda c: c.number)
            if ch.number < chapter_number
        ]
        
        prev_chapters_context = []
        for ch in previous_chapters:
            summary = self._create_chapter_summary(ch)
            prev_chapters_context.append(
                f"Chapter {ch.number}: {ch.title}\n{summary}"
            )
        
        if prev_chapters_context:
            prev_section = "PREVIOUS CHAPTERS:\n\n" + "\n\n".join(prev_chapters_context)
        else:
            prev_section = "PREVIOUS CHAPTERS:\n[This is the first chapter]"
        
        # Create planning prompt
        prompt = f"""{truth_section}

{prev_section}

TASK: Create a detailed outline for the following chapter.

Chapter {chapter_number}: {chapter_title}

Instructions:
- Break down the chapter into 3-5 key scenes or sections
- For each scene, describe:
  * Setting and characters involved
  * Main action or conflict
  * Character development or revelations
  * How it advances the plot
- Ensure consistency with established Truth and previous chapters
- Maintain narrative flow and pacing
- Include specific details that can guide the writing

CHAPTER OUTLINE:"""
        
        # Generate outline
        try:
            outline = self.llm_service.generate_text(
                prompt=prompt,
                temperature=0.7,  # Balanced for planning
                max_tokens=1500  # Allow for detailed outline
            )
            logger.debug("Chapter outline generated")
            return outline.strip()
        except Exception as e:
            logger.error(f"Failed to plan chapter: {e}")
            raise RuntimeError(f"Failed to plan chapter: {str(e)}") from e
