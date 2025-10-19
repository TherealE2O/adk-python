"""LLM service for Google Gemini integration."""

from __future__ import annotations

import os
from typing import Optional

from google import genai
from google.genai import types


class LLMService:
  """Service for interacting with Google Gemini LLM."""
  
  def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash-exp"):
    """Initialize the LLM service.
    
    Args:
      api_key: Google AI API key. If None, reads from GOOGLE_API_KEY env var.
      model: The Gemini model to use.
    """
    self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
    self.model = model
    self.client = None
    
    if self.api_key:
      self.client = genai.Client(api_key=self.api_key)
  
  def is_available(self) -> bool:
    """Check if the LLM service is available.
    
    Returns:
      True if API key is configured, False otherwise.
    """
    return self.client is not None
  
  def generate_text(
      self,
      prompt: str,
      temperature: float = 0.7,
      max_tokens: Optional[int] = None
  ) -> str:
    """Generate text using the LLM.
    
    Args:
      prompt: The prompt to send to the LLM.
      temperature: Sampling temperature (0.0 to 1.0).
      max_tokens: Maximum tokens to generate.
      
    Returns:
      The generated text.
      
    Raises:
      ValueError: If LLM service is not available.
    """
    if not self.is_available():
      raise ValueError(
          "LLM service not available. Please set GOOGLE_API_KEY environment variable."
      )
    
    config = types.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=max_tokens,
    )
    
    response = self.client.models.generate_content(
        model=self.model,
        contents=prompt,
        config=config
    )
    
    return response.text
  
  def generate_questions(
      self,
      context: str,
      num_questions: int = 3
  ) -> list[str]:
    """Generate follow-up questions based on context.
    
    Args:
      context: The context to generate questions from.
      num_questions: Number of questions to generate.
      
    Returns:
      List of generated questions.
    """
    if not self.is_available():
      return []
    
    prompt = f"""Based on the following story information, generate {num_questions} insightful follow-up questions that would help develop the story further. Focus on characters, plot, and world-building.

Story Information:
{context}

Generate exactly {num_questions} questions, one per line, without numbering or bullet points."""
    
    try:
      response = self.generate_text(prompt, temperature=0.8)
      questions = [q.strip() for q in response.split('\n') if q.strip()]
      return questions[:num_questions]
    except Exception as e:
      print(f"Error generating questions: {e}")
      return []
  
  def extract_entities(
      self,
      text: str,
      entity_type: str
  ) -> dict:
    """Extract entities from text.
    
    Args:
      text: The text to extract entities from.
      entity_type: Type of entity (character, plot_event, setting).
      
    Returns:
      Dictionary with extracted entity information.
    """
    if not self.is_available():
      return {}
    
    prompts = {
        'character': """Extract character information from the following text. Return a JSON object with these fields:
- name: character name
- description: brief description
- traits: list of personality traits
- role: their role in the story

Text: {text}

Return only valid JSON, no additional text.""",
        
        'plot_event': """Extract plot event information from the following text. Return a JSON object with these fields:
- title: event title
- description: event description
- significance: why this event matters

Text: {text}

Return only valid JSON, no additional text.""",
        
        'setting': """Extract setting/world-building information from the following text. Return a JSON object with these fields:
- name: location or concept name
- type: type of setting (location, magic system, organization, etc.)
- description: detailed description
- rules: list of important rules or facts

Text: {text}

Return only valid JSON, no additional text."""
    }
    
    prompt = prompts.get(entity_type, '').format(text=text)
    if not prompt:
      return {}
    
    try:
      response = self.generate_text(prompt, temperature=0.3)
      # Try to parse JSON from response
      import json
      # Remove markdown code blocks if present
      response = response.strip()
      if response.startswith('```'):
        response = response.split('```')[1]
        if response.startswith('json'):
          response = response[4:]
      response = response.strip()
      
      return json.loads(response)
    except Exception as e:
      print(f"Error extracting entities: {e}")
      return {}
