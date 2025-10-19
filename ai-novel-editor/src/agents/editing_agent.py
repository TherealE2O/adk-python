"""Editing agent for AI-assisted text editing."""

from __future__ import annotations

from typing import Optional

from ..models.truth import TruthKnowledgeBase
from ..models.project import Chapter


class EditingAgent:
  """Agent for AI-assisted text editing grounded in Truth."""
  
  def __init__(self, truth: TruthKnowledgeBase):
    """Initialize the editing agent.
    
    Args:
      truth: The truth knowledge base to use for grounding.
    """
    self.truth = truth
  
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
