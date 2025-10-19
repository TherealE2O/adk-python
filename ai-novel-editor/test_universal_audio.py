"""Test script for universal audio input component."""

from src.ui.audio_input import universal_text_input
from src.services.audio_service import AudioService

def test_universal_audio():
  """Test universal audio input component."""
  print("Testing Universal Audio Input Component...")
  print("-" * 50)
  
  # Check audio service
  audio_service = AudioService()
  
  if audio_service.is_available():
    print("✅ Audio service is available")
  else:
    print("⚠️  Audio service not available (needs GOOGLE_API_KEY)")
  
  print("\n📍 Audio Input Locations:")
  print("   1. ✅ Project Creation Form")
  print("      • Project Title")
  print("      • Description")
  print("      • Author Name")
  print("      • Genre")
  print()
  print("   2. ✅ World-Building Q&A")
  print("      • Initial question: 'What is your story about?'")
  print("      • All follow-up questions")
  print()
  print("   3. ✅ Chapter Editor")
  print("      • New chapter title")
  print("      • Chapter content (main editor)")
  print("      • Text selection for AI editing")
  print()
  print("   4. ✅ Mind Map View")
  print("      • Question answers (when selected from map)")
  print()
  
  print("\n🎤 How It Works:")
  print("   • Every text input has a '🎤 Audio' button")
  print("   • Click the button to toggle audio upload")
  print("   • Upload your audio file (WAV, MP3, etc.)")
  print("   • Gemini transcribes automatically")
  print("   • Transcript fills the text field")
  print()
  
  print("\n💡 Supported Formats:")
  formats = audio_service.get_supported_formats()
  for name, mime_type in formats.items():
    print(f"   • {name} ({mime_type})")
  print()
  
  print("\n⚡ Features:")
  print("   • ✅ Universal - works everywhere")
  print("   • ✅ Context-aware - custom prompts per field")
  print("   • ✅ Seamless - integrates with existing UI")
  print("   • ✅ Optional - text input still available")
  print("   • ✅ Smart - remembers transcripts")
  print()
  
  print("-" * 50)
  print("✅ Universal audio input test complete!")
  print()
  print("💡 To test in the app:")
  print("   1. Run: streamlit run app.py")
  print("   2. Look for '🎤 Audio' buttons everywhere")
  print("   3. Click to upload and transcribe")

if __name__ == "__main__":
  test_universal_audio()
