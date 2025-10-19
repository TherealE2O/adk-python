"""Audio service using Gemini's native audio understanding."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Optional

from google import genai
from google.genai import types


class AudioService:
  """Service for audio recording and transcription using Gemini."""
  
  def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash-exp"):
    """Initialize the audio service.
    
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
    """Check if the audio service is available.
    
    Returns:
      True if API key is configured, False otherwise.
    """
    return self.client is not None
  
  def transcribe_audio_file(
      self,
      file_path: str,
      prompt: str = "Generate a transcript of the speech."
  ) -> Optional[str]:
    """Transcribe an audio file using Gemini.
    
    Args:
      file_path: Path to the audio file.
      prompt: Custom prompt for transcription.
      
    Returns:
      Transcribed text, or None if failed.
    """
    if not self.is_available():
      return None
    
    try:
      # Upload the audio file
      audio_file = self.client.files.upload(file=file_path)
      
      # Generate transcript
      response = self.client.models.generate_content(
          model=self.model,
          contents=[prompt, audio_file]
      )
      
      return response.text
    
    except Exception as e:
      print(f"Error transcribing audio: {e}")
      return None
  
  def transcribe_audio_bytes(
      self,
      audio_bytes: bytes,
      mime_type: str = "audio/wav",
      prompt: str = "Generate a transcript of the speech."
  ) -> Optional[str]:
    """Transcribe audio data from bytes using Gemini.
    
    Args:
      audio_bytes: Audio data as bytes.
      mime_type: MIME type of the audio (e.g., 'audio/wav', 'audio/mp3').
      prompt: Custom prompt for transcription.
      
    Returns:
      Transcribed text, or None if failed.
    """
    if not self.is_available():
      return None
    
    try:
      # Create audio part from bytes
      audio_part = types.Part.from_bytes(
          data=audio_bytes,
          mime_type=mime_type
      )
      
      # Generate transcript
      response = self.client.models.generate_content(
          model=self.model,
          contents=[prompt, audio_part]
      )
      
      return response.text
    
    except Exception as e:
      print(f"Error transcribing audio bytes: {e}")
      return None
  
  def analyze_audio(
      self,
      file_path: str,
      prompt: str
  ) -> Optional[str]:
    """Analyze audio content with a custom prompt.
    
    Args:
      file_path: Path to the audio file.
      prompt: Analysis prompt (e.g., "Summarize the main points").
      
    Returns:
      Analysis result, or None if failed.
    """
    if not self.is_available():
      return None
    
    try:
      # Upload the audio file
      audio_file = self.client.files.upload(file=file_path)
      
      # Generate analysis
      response = self.client.models.generate_content(
          model=self.model,
          contents=[prompt, audio_file]
      )
      
      return response.text
    
    except Exception as e:
      print(f"Error analyzing audio: {e}")
      return None
  
  def transcribe_with_timestamps(
      self,
      file_path: str,
      start_time: str,
      end_time: str
  ) -> Optional[str]:
    """Transcribe a specific segment of audio using timestamps.
    
    Args:
      file_path: Path to the audio file.
      start_time: Start timestamp in MM:SS format.
      end_time: End timestamp in MM:SS format.
      
    Returns:
      Transcribed text for the segment, or None if failed.
    """
    if not self.is_available():
      return None
    
    try:
      # Upload the audio file
      audio_file = self.client.files.upload(file=file_path)
      
      # Create prompt with timestamps
      prompt = f"Provide a transcript of the speech from {start_time} to {end_time}."
      
      # Generate transcript
      response = self.client.models.generate_content(
          model=self.model,
          contents=[prompt, audio_file]
      )
      
      return response.text
    
    except Exception as e:
      print(f"Error transcribing audio segment: {e}")
      return None
  
  def count_audio_tokens(self, file_path: str) -> Optional[int]:
    """Count tokens in an audio file.
    
    Note: Gemini represents each second of audio as 32 tokens.
    
    Args:
      file_path: Path to the audio file.
      
    Returns:
      Token count, or None if failed.
    """
    if not self.is_available():
      return None
    
    try:
      # Upload the audio file
      audio_file = self.client.files.upload(file=file_path)
      
      # Count tokens
      response = self.client.models.count_tokens(
          model=self.model,
          contents=[audio_file]
      )
      
      return response.total_tokens
    
    except Exception as e:
      print(f"Error counting tokens: {e}")
      return None
  
  def save_uploaded_audio(
      self,
      uploaded_file,
      output_dir: str = "data/audio"
  ) -> Optional[str]:
    """Save an uploaded audio file to disk.
    
    Args:
      uploaded_file: Streamlit uploaded file object.
      output_dir: Directory to save the file.
      
    Returns:
      Path to saved file, or None if failed.
    """
    try:
      # Create output directory if it doesn't exist
      Path(output_dir).mkdir(parents=True, exist_ok=True)
      
      # Generate unique filename
      file_path = os.path.join(output_dir, uploaded_file.name)
      
      # Save file
      with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
      
      return file_path
    
    except Exception as e:
      print(f"Error saving audio file: {e}")
      return None
  
  @staticmethod
  def get_supported_formats() -> dict[str, str]:
    """Get supported audio formats.
    
    Returns:
      Dictionary mapping format names to MIME types.
    """
    return {
        'WAV': 'audio/wav',
        'MP3': 'audio/mp3',
        'AIFF': 'audio/aiff',
        'AAC': 'audio/aac',
        'OGG': 'audio/ogg',
        'FLAC': 'audio/flac',
    }
  
  @staticmethod
  def get_max_duration_hours() -> float:
    """Get maximum supported audio duration.
    
    Returns:
      Maximum duration in hours (9.5 hours).
    """
    return 9.5
  
  @staticmethod
  def estimate_tokens_from_duration(duration_seconds: float) -> int:
    """Estimate token count from audio duration.
    
    Gemini represents each second of audio as 32 tokens.
    
    Args:
      duration_seconds: Audio duration in seconds.
      
    Returns:
      Estimated token count.
    """
    return int(duration_seconds * 32)
