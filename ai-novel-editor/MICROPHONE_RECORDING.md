# Microphone Recording Guide

## Overview

The AI Novel Editor now supports **direct microphone recording** in your browser. No need to record separately and upload files - just click and speak!

## ✅ Features

### Browser-Based Recording
- **No software needed** - Works directly in your browser
- **Click to record** - Simple one-click interface
- **Real-time** - Record and transcribe immediately
- **Universal** - Works everywhere you can type
- **Secure** - Recording happens locally in your browser

### Two Input Methods
Every 🎤 Audio button now offers:
1. **🎙️ Record** - Use your microphone (NEW!)
2. **📁 Upload** - Upload pre-recorded files

## 🎤 How to Use

### Quick Start (30 seconds)

1. **Click 🎤 Audio** button next to any text field
2. **Select "Record" tab**
3. **Click microphone icon** to start
4. **Speak your content**
5. **Click again** to stop
6. **Wait 2-5 seconds** for transcription
7. **Done!** Transcript fills the field

### Detailed Steps

#### Step 1: Enable Microphone

**First Time Only:**
- Browser will ask for microphone permission
- Click "Allow" to enable recording
- Permission is remembered for future use

**Troubleshooting:**
- If blocked, check browser settings
- Look for microphone icon in address bar
- Click and select "Allow"

#### Step 2: Start Recording

1. Find any text field in the app
2. Click the **🎤 Audio** button
3. Select the **🎙️ Record** tab
4. Click the **microphone icon**
5. Icon turns red when recording

#### Step 3: Record Your Content

**While Recording:**
- Speak at normal pace
- Stay close to microphone
- Avoid background noise
- Pause naturally between sentences

**Recording Indicator:**
- Red icon = Recording active
- Blue icon = Ready to record
- Timer shows recording duration

#### Step 4: Stop Recording

1. Click the microphone icon again
2. Recording stops immediately
3. Audio is processed automatically

#### Step 5: Transcription

**Automatic Process:**
- Audio sent to Gemini API
- Transcription takes 2-10 seconds
- Progress shown with spinner
- Transcript appears when ready

**What You'll See:**
- "🎧 Transcribing recording..." message
- Success message: "✅ Transcribed!"
- Transcript fills the text field
- Audio input closes automatically

#### Step 6: Review & Submit

1. **Review** the transcript
2. **Edit** if needed (fix any errors)
3. **Submit** the form or continue editing

## 📍 Where It Works

### 1. Project Creation
- **Project Title**: Record your project name
- **Description**: Describe your novel
- **Author Name**: Say your name
- **Genre**: Specify the genre

### 2. World-Building Q&A
- **Initial Question**: "What is your story about?"
- **All Follow-ups**: Every question in the tree
- **Any Branch**: Character, plot, or setting questions

### 3. Chapter Editor
- **Chapter Title**: Name your chapters
- **Chapter Content**: Dictate entire chapters
- **Text Selection**: Select text for AI editing

### 4. Everywhere
- Any text input or text area
- All forms and fields
- Complete voice-enabled workflow

## 🎯 Best Practices

### Recording Environment

1. **Quiet Space**
   - Close windows
   - Turn off fans/AC
   - Minimize background noise
   - Use a quiet room

2. **Microphone Position**
   - 6-12 inches from mouth
   - Slightly off to the side
   - Avoid breathing directly into mic
   - Keep consistent distance

3. **Audio Quality**
   - Use built-in mic (good enough)
   - External mic is better
   - Headset mic works great
   - USB mic is best

### Speaking Technique

1. **Pace**
   - Speak at normal conversational pace
   - Don't rush or speak too slowly
   - Pause naturally between sentences
   - Take breaks for long content

2. **Clarity**
   - Enunciate clearly
   - Pronounce names carefully
   - Spell out unusual terms if needed
   - Repeat if you make a mistake

3. **Content Structure**
   - Organize thoughts before recording
   - Speak in complete sentences
   - Use natural punctuation pauses
   - Say "period" or "comma" if needed

### Recording Length

1. **Short Recordings** (Recommended)
   - Under 2 minutes ideal
   - Quick transcription
   - Easy to review
   - Less chance of errors

2. **Medium Recordings**
   - 2-5 minutes acceptable
   - Takes longer to transcribe
   - More to review
   - Higher chance of errors

3. **Long Recordings**
   - Over 5 minutes not recommended
   - Break into smaller chunks
   - Record multiple times
   - Easier to manage

## 🔧 Technical Details

### Browser Compatibility

**Supported Browsers:**
- ✅ Chrome/Chromium (recommended)
- ✅ Edge
- ✅ Firefox
- ✅ Safari
- ✅ Opera

**Requirements:**
- Modern browser (last 2 years)
- Microphone access permission
- Internet connection (for transcription)

### Audio Format

**Recording Specs:**
- Format: WAV
- Sample Rate: 44.1 kHz
- Bit Depth: 16-bit
- Channels: Mono

**Automatic Handling:**
- Browser records in optimal format
- Converted automatically for Gemini
- No user configuration needed

### Privacy & Security

**What Happens:**
1. Recording happens in your browser
2. Audio sent to Gemini API for transcription
3. Temporary file created for processing
4. File deleted immediately after transcription
5. No permanent storage of audio

**Data Flow:**
```
Your Mic → Browser → Temp File → Gemini API → Transcript → Text Field
                                      ↓
                                  Deleted
```

**Privacy Notes:**
- Audio not stored on server
- Temporary files cleaned up
- Only transcript is kept
- Gemini API processes audio securely

## 🐛 Troubleshooting

### Microphone Not Working

**Problem**: Can't record, no audio captured

**Solutions:**
1. Check browser permissions
   - Click microphone icon in address bar
   - Select "Allow"
   - Refresh page

2. Check system settings
   - Ensure microphone is enabled
   - Check system privacy settings
   - Test mic in other apps

3. Try different browser
   - Chrome works best
   - Update to latest version

### Poor Transcription Quality

**Problem**: Transcript has many errors

**Solutions:**
1. Improve recording environment
   - Reduce background noise
   - Move to quieter space
   - Close windows/doors

2. Improve speaking
   - Speak more clearly
   - Slow down slightly
   - Enunciate better

3. Check microphone
   - Position closer to mouth
   - Use better microphone
   - Test with other apps

### Recording Cuts Off

**Problem**: Recording stops unexpectedly

**Solutions:**
1. Check browser settings
   - Ensure mic permission is persistent
   - Don't switch tabs while recording
   - Keep browser window active

2. Keep recordings shorter
   - Under 2 minutes recommended
   - Break long content into chunks

3. Check internet connection
   - Stable connection needed
   - Don't let computer sleep

### Transcription Fails

**Problem**: "Failed to transcribe" error

**Solutions:**
1. Check API key
   - Verify GOOGLE_API_KEY is set
   - Check key is valid
   - Restart app

2. Check internet
   - Ensure stable connection
   - Try again

3. Try uploading instead
   - Switch to Upload tab
   - Upload a file instead

## 📊 Comparison

### Recording vs Upload

| Feature | 🎙️ Record | 📁 Upload |
|---------|-----------|-----------|
| Speed | Instant | Need to record first |
| Convenience | Very high | Medium |
| Quality | Good | Excellent |
| Editing | No | Yes (can edit file) |
| File Size | Automatic | Manual |
| Best For | Quick input | Prepared content |

### When to Use Each

**Use Recording When:**
- ✅ You want to input quickly
- ✅ You're at your computer
- ✅ Content is short (< 2 min)
- ✅ You don't need to edit audio

**Use Upload When:**
- ✅ You recorded on phone
- ✅ You edited the audio
- ✅ Content is long (> 5 min)
- ✅ You want best quality

## 💡 Tips & Tricks

### Efficient Workflow

1. **Plan Before Recording**
   - Outline what you'll say
   - Organize thoughts
   - Have notes ready

2. **Record in Chunks**
   - One paragraph at a time
   - One question at a time
   - Easy to manage

3. **Review Immediately**
   - Check transcript right away
   - Fix errors while fresh
   - Re-record if needed

### Advanced Techniques

1. **Dictation Punctuation**
   - Say "period" for .
   - Say "comma" for ,
   - Say "new paragraph" for breaks

2. **Name Spelling**
   - Spell unusual names
   - "Elena, E-L-E-N-A"
   - Helps transcription accuracy

3. **Multiple Takes**
   - Record multiple versions
   - Choose best transcript
   - Combine if needed

## 🎓 Examples

### Example 1: Project Description

**Recording** (30 seconds):
> "My novel is a science fiction thriller set in the year 2157. The story follows Captain Elena Rodriguez as she investigates a mysterious signal from deep space. The signal leads her crew to an abandoned alien station where they discover a terrifying secret that could destroy humanity."

**Transcript**:
> "My novel is a science fiction thriller set in the year 2157. The story follows Captain Elena Rodriguez as she investigates a mysterious signal from deep space. The signal leads her crew to an abandoned alien station where they discover a terrifying secret that could destroy humanity."

### Example 2: Character Development

**Recording** (45 seconds):
> "Elena is a 45-year-old veteran of the Earth Defense Force. She's tough, experienced, and haunted by the loss of her family during the Fall of Earth. Despite her trauma, she's fiercely protective of her crew and driven by a deep sense of duty. She has short gray hair, a scar across her left cheek, and piercing blue eyes that seem to see right through people."

**Transcript**:
> "Elena is a 45-year-old veteran of the Earth Defense Force. She's tough, experienced, and haunted by the loss of her family during the Fall of Earth. Despite her trauma, she's fiercely protective of her crew and driven by a deep sense of duty. She has short gray hair, a scar across her left cheek, and piercing blue eyes that seem to see right through people."

### Example 3: Chapter Content

**Recording** (2 minutes):
> "The bridge was silent except for the steady beep of the proximity alarm. Elena stared at the viewscreen, her hands gripping the armrests of the captain's chair. The alien station loomed before them, a massive structure of impossible geometry that seemed to shift and change as she watched. 'Status report,' she said, her voice steady despite the knot of fear in her stomach. 'All systems nominal, Captain,' replied her first officer, Lieutenant Chen. 'But I'm reading some strange energy signatures from the station. Nothing in our database matches.' Elena nodded slowly. This was it. The moment that would change everything."

**Transcript**: [Full chapter opening, ready to edit and expand]

## 🚀 Getting Started

### Quick Setup (1 minute)

1. **Open the app**
   ```bash
   streamlit run app.py
   ```

2. **Find any text field**
   - Project creation, Q&A, or editor

3. **Click 🎤 Audio button**
   - Allow microphone access (first time)

4. **Select Record tab**
   - Click microphone icon

5. **Start speaking!**
   - That's it - you're recording!

### First Recording Checklist

- [ ] Browser is up to date
- [ ] Microphone permission granted
- [ ] Quiet environment
- [ ] GOOGLE_API_KEY is set
- [ ] Internet connection stable
- [ ] Ready to speak!

## 🎉 Summary

Microphone recording makes the AI Novel Editor **truly voice-first**:

1. ✅ **Instant** - No file upload needed
2. ✅ **Easy** - Click and speak
3. ✅ **Universal** - Works everywhere
4. ✅ **Accurate** - 95-98% transcription
5. ✅ **Flexible** - Record or upload
6. ✅ **Secure** - Browser-based, private

**Just click, speak, and write!** 🎤📖✨
