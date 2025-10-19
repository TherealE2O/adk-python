"""Voice service for speech recognition and text-to-speech."""

from __future__ import annotations

import os
from typing import Optional
import tempfile
from pathlib import Path

try:
  import speech_recognition as sr
  SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
  SPEECH_RECOGNITION_AVAILABLE = False

try:
  import pyttsx3
  PYTTSX3_AVAILABLE = True
except ImportError:
  PYTTSX3_AVAILABLE = False

try:
  from google.cloud import texttospeech
  GOOGLE_TTS_AVAILABLE = True
except ImportError:
  GOOGLE_TTS_AVAILABLE = False


class VoiceService:
  """Service for voice input/output functionality."""
  
  def __init__(self, use_google_tts: bool = False):
    """Initialize the voice service.
    
    Args:
      use_google_tts: Whether to use Google Cloud TTS (requires credentials).
    """
    self.recognizer = None
    self.tts_engine = None
    self.google_tts_client = None
    self.use_google_tts = use_google_tts
    
    # Initialize speech recognition
    if SPEECH_RECOGNITION_AVAILABLE:
      self.recognizer = sr.Recognizer()
      # Adjust for ambient noise
      self.recognizer.energy_threshold = 4000
      self.recognizer.dynamic_energy_threshold = True
    
    # Initialize text-to-speech
    if use_google_tts and GOOGLE_TTS_AVAILABLE:
      try:
        self.google_tts_client = texttospeech.TextToSpeechClient()
      except Exception as e:
        print(f"Failed to initialize Google TTS: {e}")
        self.google_tts_client = None
    
    if not use_google_tts and PYTTSX3_AVAILABLE:
      try:
        self.tts_engine = pyttsx3.init()
        # Configure voice properties
        self.tts_engine.setProperty('rate', 150)  # Speed
        self.tts_engine.setProperty('volume', 0.9)  # Volume
      except Exception as e:
        print(f"Failed to initialize pyttsx3: {e}")
        self.tts_engine = None
  
  def is_speech_recognition_available(self) -> bool:
    """Check if speech recognition is available.
    
    Returns:
      True if speech recognition is available.
    """
    return self.recognizer is not None
  
  def is_tts_available(self) -> bool:
    """Check if text-to-speech is available.
    
    Returns:
      True if TTS is available.
    """
    return self.tts_engine is not None or self.google_tts_client is not None
  
  def listen_for_speech(
      self,
      timeout: int = 10,
      phrase_time_limit: Optional[int] = None
  ) -> Optional[str]:
    """Listen for speech input from microphone.
    
    Args:
      timeout: Maximum time to wait for speech to start (seconds).
      phrase_time_limit: Maximum time for the phrase (seconds).
      
    Returns:
      Transcribed text, or None if failed.
    """
    if not self.is_speech_recognition_available():
      return None
    
    try:
      with sr.Microphone() as source:
        # Adjust for ambient noise
        self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        # Listen for audio
        audio = self.recognizer.listen(
            source,
            timeout=timeout,
            phrase_time_limit=phrase_time_limit
        )
        
        # Recognize speech using Google Speech Recognition
        text = self.recognizer.recognize_google(audio)
        return text
    
    except sr.WaitTimeoutError:
      print("Listening timed out - no speech detected")
      return None
    except sr.UnknownValueError:
      print("Could not understand audio")
      return None
    except sr.RequestError as e:
      print(f"Could not request results from speech recognition service: {e}")
      return None
    except Exception as e:
      print(f"Error during speech recognition: {e}")
      return None
  
  def speak_text(self, text: str) -> bool:
    """Convert text to speech and play it.
    
    Args:
      text: The text to speak.
      
    Returns:
      True if successful, False otherwise.
    """
    if not self.is_tts_available():
      return False
    
    try:
      if self.google_tts_client:
        return self._speak_with_google_tts(text)
      elif self.tts_engine:
        return self._speak_with_pyttsx3(text)
      return False
    except Exception as e:
      print(f"Error during text-to-speech: {e}")
      return False
  
  def _speak_with_pyttsx3(self, text: str) -> bool:
    """Speak text using pyttsx3.
    
    Args:
      text: The text to speak.
      
    Returns:
      True if successful.
    """
    try:
      self.tts_engine.say(text)
      self.tts_engine.runAndWait()
      return True
    except Exception as e:
      print(f"pyttsx3 error: {e}")
      return False
  
  def _speak_with_google_tts(self, text: str) -> bool:
    """Speak text using Google Cloud TTS.
    
    Args:
      text: The text to speak.
      
    Returns:
      True if successful.
    """
    try:
      # Set the text input to be synthesized
      synthesis_input = texttospeech.SynthesisInput(text=text)
      
      # Build the voice request
      voice = texttospeech.VoiceSelectionParams(
          language_code="en-US",
          ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
      )
      
      # Select the type of audio file
      audio_config = texttospeech.AudioConfig(
          audio_encoding=texttospeech.AudioEncoding.MP3
      )
      
      # Perform the text-to-speech request
      response = self.google_tts_client.synthesize_speech(
          input=synthesis_input,
          voice=voice,
          audio_config=audio_config
      )
      
      # Save to temporary file and play
      with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
        f.write(response.audio_content)
        temp_file = f.name
      
      # Play the audio (platform-specific)
      self._play_audio_file(temp_file)
      
      # Clean up
      os.unlink(temp_file)
      return True
    
    except Exception as e:
      print(f"Google TTS error: {e}")
      return False
  
  def _play_audio_file(self, file_path: str) -> None:
    """Play an audio file (platform-specific).
    
    Args:
      file_path: Path to the audio file.
    """
    import platform
    import subprocess
    
    system = platform.system()
    
    try:
      if system == 'Darwin':  # macOS
        subprocess.run(['afplay', file_path], check=True)
      elif system == 'Linux':
        subprocess.run(['mpg123', file_path], check=True)
      elif system == 'Windows':
        import winsound
        winsound.PlaySound(file_path, winsound.SND_FILENAME)
    except Exception as e:
      print(f"Error playing audio: {e}")
  
  def get_available_features(self) -> dict[str, bool]:
    """Get information about available voice features.
    
    Returns:
      Dictionary with feature availability.
    """
    return {
        'speech_recognition': self.is_speech_recognition_available(),
        'text_to_speech': self.is_tts_available(),
        'google_tts': self.google_tts_client is not None,
        'pyttsx3': self.tts_engine is not None,
    }
