"""Test script for audio service functionality."""

import os
from src.services.audio_service import AudioService

def test_audio_service():
  """Test audio service initialization and features."""
  print("Testing Audio Service...")
  print("-" * 50)
  
  # Check for API key
  api_key = os.getenv('GOOGLE_API_KEY')
  if not api_key:
    print("❌ GOOGLE_API_KEY not set")
    print("   Set it in .env file to test audio features")
    return
  
  # Initialize service
  audio_service = AudioService()
  
  # Check availability
  if audio_service.is_available():
    print("✅ Audio service is available")
  else:
    print("❌ Audio service not available")
    return
  
  # Show supported formats
  print("\n📁 Supported Audio Formats:")
  formats = audio_service.get_supported_formats()
  for name, mime_type in formats.items():
    print(f"   • {name}: {mime_type}")
  
  # Show limits
  print(f"\n⏱️  Max Duration: {audio_service.get_max_duration_hours()} hours")
  
  # Token estimation
  duration_seconds = 60  # 1 minute
  tokens = audio_service.estimate_tokens_from_duration(duration_seconds)
  print(f"\n🔢 Token Estimation:")
  print(f"   • 1 minute of audio ≈ {tokens} tokens")
  print(f"   • 1 second of audio = 32 tokens")
  
  print("\n" + "-" * 50)
  print("Audio service test complete!")
  print("\n💡 To test transcription:")
  print("   1. Run the app: streamlit run app.py")
  print("   2. Create a project")
  print("   3. Select '🎤 Audio Upload' mode")
  print("   4. Upload an audio file")

if __name__ == "__main__":
  test_audio_service()
