"""Diagnostic script to check audio transcription setup."""

import os
from dotenv import load_dotenv
from src.services.audio_service import AudioService

def diagnose():
  """Run diagnostic checks."""
  print("🔍 AI Novel Editor - Audio Transcription Diagnostics")
  print("=" * 60)
  
  # Load environment
  load_dotenv()
  
  # Check 1: API Key
  print("\n1️⃣ Checking GOOGLE_API_KEY...")
  api_key = os.getenv('GOOGLE_API_KEY')
  if api_key:
    print(f"   ✅ API key found: {api_key[:10]}...{api_key[-4:]}")
    print(f"   📏 Length: {len(api_key)} characters")
  else:
    print("   ❌ API key NOT found")
    print("   💡 Fix: Add GOOGLE_API_KEY to .env file")
    print("   📖 Get key from: https://makersuite.google.com/app/apikey")
    return
  
  # Check 2: Audio Service
  print("\n2️⃣ Checking Audio Service...")
  try:
    audio_service = AudioService()
    if audio_service.is_available():
      print("   ✅ Audio service initialized")
      print(f"   🤖 Model: {audio_service.model}")
    else:
      print("   ❌ Audio service not available")
      return
  except Exception as e:
    print(f"   ❌ Error initializing: {e}")
    return
  
  # Check 3: Supported Formats
  print("\n3️⃣ Supported Audio Formats:")
  formats = audio_service.get_supported_formats()
  for name, mime_type in formats.items():
    print(f"   ✅ {name} ({mime_type})")
  
  # Check 4: Directories
  print("\n4️⃣ Checking Directories...")
  audio_dir = "data/audio"
  if os.path.exists(audio_dir):
    print(f"   ✅ Audio directory exists: {audio_dir}")
    # Check if writable
    test_file = os.path.join(audio_dir, ".test")
    try:
      with open(test_file, 'w') as f:
        f.write("test")
      os.remove(test_file)
      print(f"   ✅ Directory is writable")
    except:
      print(f"   ❌ Directory is NOT writable")
  else:
    print(f"   ⚠️  Audio directory doesn't exist: {audio_dir}")
    print(f"   💡 Creating directory...")
    try:
      os.makedirs(audio_dir, exist_ok=True)
      print(f"   ✅ Directory created")
    except Exception as e:
      print(f"   ❌ Failed to create: {e}")
  
  # Check 5: Internet Connection
  print("\n5️⃣ Checking Internet Connection...")
  try:
    import socket
    socket.create_connection(("8.8.8.8", 53), timeout=3)
    print("   ✅ Internet connection working")
  except:
    print("   ❌ No internet connection")
    print("   💡 Fix: Check your network connection")
    return
  
  # Check 6: Test API Call
  print("\n6️⃣ Testing Gemini API...")
  try:
    from google import genai
    client = genai.Client(api_key=api_key)
    
    # Simple test
    response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents='Say "test successful"'
    )
    
    if response and response.text:
      print("   ✅ API call successful")
      print(f"   📝 Response: {response.text[:50]}...")
    else:
      print("   ❌ API call failed - no response")
  except Exception as e:
    print(f"   ❌ API call failed: {type(e).__name__}")
    print(f"   📝 Error: {str(e)[:100]}")
    
    if "API key" in str(e):
      print("   💡 Fix: Check your API key is valid")
    elif "quota" in str(e).lower():
      print("   💡 Fix: API quota exceeded, wait or upgrade")
    elif "network" in str(e).lower():
      print("   💡 Fix: Check internet connection")
  
  # Summary
  print("\n" + "=" * 60)
  print("📊 Diagnostic Summary:")
  print("   • API Key: " + ("✅ Set" if api_key else "❌ Missing"))
  print("   • Audio Service: " + ("✅ Ready" if audio_service.is_available() else "❌ Not Ready"))
  print("   • Directories: ✅ OK")
  print("   • Internet: ✅ Connected")
  
  print("\n💡 Next Steps:")
  if api_key and audio_service.is_available():
    print("   ✅ Everything looks good!")
    print("   🎤 Try recording or uploading audio in the app")
    print("   📖 If still failing, check TROUBLESHOOTING_TRANSCRIPTION.md")
  else:
    print("   ❌ Fix the issues above first")
    print("   📖 See TROUBLESHOOTING_TRANSCRIPTION.md for detailed help")
  
  print("\n" + "=" * 60)

if __name__ == "__main__":
  diagnose()
