"""Editing agent for AI-assisted text editing."""

from __future__ import annotations

from typing import Optional

from ..models.truth import TruthKnowledgeBase
from ..models.project import Chapter
from ..services.llm_service import LLMService


class EditingAgent:
  """Agent for AI-assisted text editing grounded in Truth."""
  
  def __init__(self, truth: TruthKnowledgeBase, llm_service: Optional[LLMService] = None):
    """Initialize the editing agent.
    
    Args:
      truth: The truth knowledge base to use for grounding.
      llm_service: Optional LLM service. If None, creates a new one.
    """
    self.truth = truth
    self.llm_service = llm_service or LLMService()
  
  def get_truth_context(self) -> str:
    """Get a text summary of the Truth for context.
    
    Returns:
      A formatted string containing the Truth context.
    """
    context_parts = []
    
    # Add characters
    if self.truth.characters:
      context_parts.append("CHARACTERS:")
      for char in self.truth.characters.values():
        char_info = f"- {char.name}: {char.description}"
        if char.traits:
          char_info += f" Traits: {', '.join(char.traits)}"
        context_parts.append(char_info)
    
    # Add plot events
    if self.truth.plot_events:
      context_parts.append("\nPLOT EVENTS:")
      sorted_events = sorted(
          self.truth.plot_events.values(),
          key=lambda e: e.order
      )
      for event in sorted_events:
        context_parts.append(f"- {event.title}: {event.description}")
    
    # Add settings
    if self.truth.settings:
      context_parts.append("\nSETTINGS:")
      for setting in self.truth.settings.values():
        context_parts.append(f"- {setting.name}: {setting.description}")
    
    return "\n".join(context_parts)
  
  def get_previous_chapters_context(
      self,
      chapters: list[Chapter],
      current_chapter_number: int
  ) -> str:
    """Get context from previous chapters.
    
    Args:
      chapters: List of all chapters.
      current_chapter_number: The current chapter number.
      
    Returns:
      A summary of previous chapters.
    """
    previous_chapters = [
        c for c in chapters
        if c.number < current_chapter_number
    ]
    previous_chapters.sort(key=lambda c: c.number)
    
    if not previous_chapters:
      return "No previous chapters."
    
    context_parts = ["PREVIOUS CHAPTERS SUMMARY:"]
    for chapter in previous_chapters:
      summary = f"Chapter {chapter.number}: {chapter.title}"
      if chapter.outline:
        summary += f" - {chapter.outline}"
      context_parts.append(summary)
    
    return "\n".join(context_parts)
  
  def create_editing_prompt(
      self,
      action: str,
      text: str,
      chapter: Optional[Chapter] = None,
      all_chapters: Optional[list[Chapter]] = None
  ) -> str:
    """Create a prompt for editing actions.
    
    Args:
      action: The editing action (improve, expand, rephrase).
      text: The text to edit.
      chapter: The current chapter.
      all_chapters: All chapters for context.
      
    Returns:
      The complete prompt for the LLM.
    """
    prompt_parts = []
    
    # Add Truth context
    truth_context = self.get_truth_context()
    if truth_context:
      prompt_parts.append("STORY TRUTH (established facts):")
      prompt_parts.append(truth_context)
      prompt_parts.append("")
    
    # Add previous chapters context
    if chapter and all_chapters:
      prev_context = self.get_previous_chapters_context(
          all_chapters,
          chapter.number
      )
      prompt_parts.append(prev_context)
      prompt_parts.append("")
    
    # Add the specific editing instruction
    action_instructions = {
        'improve': (
            "Improve the following text while maintaining consistency with "
            "the established story facts and previous chapters. Enhance "
            "clarity, flow, and prose quality."
        ),
        'expand': (
            "Expand the following text with more detail and description, "
            "staying consistent with the established story facts and "
            "previous chapters."
        ),
        'rephrase': (
            "Rephrase the following text in a different way while "
            "maintaining the same meaning and staying consistent with "
            "the established story facts."
        ),
    }
    
    instruction = action_instructions.get(
        action,
        "Edit the following text:"
    )
    prompt_parts.append(instruction)
    prompt_parts.append("")
    prompt_parts.append("TEXT TO EDIT:")
    prompt_parts.append(text)
    
    return "\n".join(prompt_parts)
  
  def create_generation_prompt(
      self,
      instruction: str,
      chapter: Optional[Chapter] = None,
      all_chapters: Optional[list[Chapter]] = None
  ) -> str:
    """Create a prompt for generating new content.
    
    Args:
      instruction: The user's instruction for generation.
      chapter: The current chapter.
      all_chapters: All chapters for context.
      
    Returns:
      The complete prompt for the LLM.
    """
    prompt_parts = []
    
    # Add Truth context
    truth_context = self.get_truth_context()
    if truth_context:
      prompt_parts.append("STORY TRUTH (established facts):")
      prompt_parts.append(truth_context)
      prompt_parts.append("")
    
    # Add previous chapters context
    if chapter and all_chapters:
      prev_context = self.get_previous_chapters_context(
          all_chapters,
          chapter.number
      )
      prompt_parts.append(prev_context)
      prompt_parts.append("")
    
    # Add generation instruction
    prompt_parts.append("INSTRUCTION:")
    prompt_parts.append(instruction)
    prompt_parts.append("")
    prompt_parts.append(
        "Generate content that is consistent with the established "
        "story facts and previous chapters."
    )
    
    return "\n".join(prompt_parts)
  
  def create_chapter_planning_prompt(
      self,
      all_chapters: list[Chapter]
  ) -> str:
    """Create a prompt for planning the next chapter.
    
    Args:
      all_chapters: All existing chapters.
      
    Returns:
      The complete prompt for the LLM.
    """
    prompt_parts = []
    
    # Add Truth context
    truth_context = self.get_truth_context()
    if truth_context:
      prompt_parts.append("STORY TRUTH (established facts):")
      prompt_parts.append(truth_context)
      prompt_parts.append("")
    
    # Add existing chapters summary
    if all_chapters:
      prompt_parts.append("EXISTING CHAPTERS:")
      for chapter in sorted(all_chapters, key=lambda c: c.number):
        prompt_parts.append(
            f"Chapter {chapter.number}: {chapter.title} - {chapter.outline}"
        )
      prompt_parts.append("")
    
    prompt_parts.append(
        "Based on the story truth and existing chapters, suggest what "
        "the next chapter should be about. Provide a title and outline."
    )
    
    return "\n".join(prompt_parts)
  
  def improve_text(
      self,
      text: str,
      chapter: Optional[Chapter] = None,
      all_chapters: Optional[list[Chapter]] = None
  ) -> str:
    """Improve the given text using AI.
    
    Args:
      text: The text to improve.
      chapter: The current chapter.
      all_chapters: All chapters for context.
      
    Returns:
      The improved text.
    """
    if not self.llm_service.is_available():
      return "AI service not available. Please set GOOGLE_API_KEY."
    
    prompt = self.create_editing_prompt('improve', text, chapter, all_chapters)
    
    try:
      return self.llm_service.generate_text(prompt, temperature=0.7)
    except Exception as e:
      return f"Error improving text: {str(e)}"
  
  def expand_text(
      self,
      text: str,
      chapter: Optional[Chapter] = None,
      all_chapters: Optional[list[Chapter]] = None
  ) -> str:
    """Expand the given text with more detail using AI.
    
    Args:
      text: The text to expand.
      chapter: The current chapter.
      all_chapters: All chapters for context.
      
    Returns:
      The expanded text.
    """
    if not self.llm_service.is_available():
      return "AI service not available. Please set GOOGLE_API_KEY."
    
    prompt = self.create_editing_prompt('expand', text, chapter, all_chapters)
    
    try:
      return self.llm_service.generate_text(prompt, temperature=0.7)
    except Exception as e:
      return f"Error expanding text: {str(e)}"
  
  def rephrase_text(
      self,
      text: str,
      chapter: Optional[Chapter] = None,
      all_chapters: Optional[list[Chapter]] = None
  ) -> str:
    """Rephrase the given text using AI.
    
    Args:
      text: The text to rephrase.
      chapter: The current chapter.
      all_chapters: All chapters for context.
      
    Returns:
      The rephrased text.
    """
    if not self.llm_service.is_available():
      return "AI service not available. Please set GOOGLE_API_KEY."
    
    prompt = self.create_editing_prompt('rephrase', text, chapter, all_chapters)
    
    try:
      return self.llm_service.generate_text(prompt, temperature=0.7)
    except Exception as e:
      return f"Error rephrasing text: {str(e)}"
  
  def suggest_next_chapter(
      self,
      all_chapters: list[Chapter]
  ) -> str:
    """Suggest what the next chapter should be about.
    
    Args:
      all_chapters: All existing chapters.
      
    Returns:
      Suggestion for the next chapter.
    """
    if not self.llm_service.is_available():
      return "AI service not available. Please set GOOGLE_API_KEY."
    
    prompt = self.create_chapter_planning_prompt(all_chapters)
    
    try:
      return self.llm_service.generate_text(prompt, temperature=0.8)
    except Exception as e:
      return f"Error suggesting next chapter: {str(e)}"
  
  def generate_paragraph(
      self,
      instruction: str,
      chapter: Optional[Chapter] = None,
      all_chapters: Optional[list[Chapter]] = None
  ) -> str:
    """Generate a new paragraph based on instruction.
    
    Args:
      instruction: User's instruction for what to generate.
      chapter: The current chapter.
      all_chapters: All chapters for context.
      
    Returns:
      The generated paragraph.
    """
    if not self.llm_service.is_available():
      return "AI service not available. Please set GOOGLE_API_KEY."
    
    prompt = self.create_generation_prompt(instruction, chapter, all_chapters)
    
    try:
      return self.llm_service.generate_text(prompt, temperature=0.8)
    except Exception as e:
      return f"Error generating paragraph: {str(e)}"
