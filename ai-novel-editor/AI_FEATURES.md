# AI Features - Implementation Guide

## Overview

The AI Novel Editor now includes **full AI integration** with Google Gemini for all editing and world-building features. This document explains how the AI features work and how to use them.

## ✅ Implemented AI Features

### 1. AI-Powered Text Editing

#### Improve Text
- **What it does**: Enhances prose quality, clarity, and flow
- **How it works**: Sends text + Truth context + previous chapters to Gemini
- **Grounding**: Strictly maintains consistency with established facts
- **Usage**: Select text → Click "✨ Improve"

#### Expand Text
- **What it does**: Adds more detail, description, and depth
- **How it works**: Analyzes context and generates expanded version
- **Grounding**: Uses Truth and previous chapters for consistency
- **Usage**: Select text → Click "📝 Expand"

#### Rephrase Text
- **What it does**: Rewrites text in a different way
- **How it works**: Maintains meaning while changing expression
- **Grounding**: Keeps all facts consistent with Truth
- **Usage**: Select text → Click "🔄 Rephrase"

### 2. AI-Powered Chapter Planning

#### Suggest Next Chapter
- **What it does**: Recommends what the next chapter should be about
- **How it works**: Analyzes existing chapters and Truth to suggest progression
- **Grounding**: Based on established plot and character arcs
- **Usage**: Click "💡 Suggest Next"

#### Generate Paragraph
- **What it does**: Creates new content based on your instruction
- **How it works**: Uses your prompt + Truth + chapter context
- **Grounding**: Maintains consistency with all established facts
- **Usage**: Provide instruction → AI generates content

### 3. AI-Powered World-Building

#### Intelligent Question Generation
- **What it does**: Generates contextual follow-up questions
- **How it works**: Analyzes your answers to create relevant questions
- **Grounding**: Questions are specific to your story details
- **Usage**: Automatic when you answer questions

#### Entity Extraction
- **What it does**: Automatically extracts characters, plot, settings from answers
- **How it works**: Uses AI to parse and structure information
- **Grounding**: Creates structured Truth entries from natural language
- **Usage**: Automatic when you answer questions

## 🔧 Setup

### Prerequisites

1. **Google AI API Key**
   - Get one from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Free tier available

2. **Install Dependencies**
   ```bash
   pip install google-genai
   ```

### Configuration

1. **Create .env file**
   ```bash
   cp .env.example .env
   ```

2. **Add your API key**
   ```bash
   echo "GOOGLE_API_KEY=your_api_key_here" >> .env
   ```

3. **Restart the application**
   ```bash
   streamlit run app.py
   ```

## 📖 How to Use AI Features

### In the Editor

1. **Open a chapter** in the editor
2. **Select text** to edit (or leave empty for full chapter)
3. **Click an AI button**:
   - ✨ Improve - Enhance quality
   - 📝 Expand - Add detail
   - 🔄 Rephrase - Rewrite differently
   - 💡 Suggest Next - Plan next chapter

4. **Review the AI result**
5. **Choose an action**:
   - ✅ Use This - Apply the suggestion
   - ❌ Discard - Reject the suggestion

### In World-Building

1. **Answer a question** about your story
2. **AI automatically**:
   - Generates 3-5 relevant follow-up questions
   - Extracts entities (characters, plot, settings)
   - Updates the Truth knowledge base

3. **Navigate** the question tree
4. **Continue** answering questions

## 🎯 AI Grounding System

### How Grounding Works

Every AI operation includes:

1. **Truth Context**
   - All characters with traits and backstories
   - All plot events in chronological order
   - All settings and world-building details

2. **Previous Chapters**
   - Summaries of all previous chapters
   - Ensures continuity and consistency

3. **User Instruction**
   - Your specific request or selected text

### Example Prompt Structure

```
STORY TRUTH (established facts):
CHARACTERS:
- Hero: A brave warrior. Traits: courageous, kind

PLOT EVENTS:
- The Beginning: Hero discovers their destiny

SETTINGS:
- The Kingdom: A medieval fantasy realm

PREVIOUS CHAPTERS SUMMARY:
Chapter 1: The Call to Adventure - Hero learns of the prophecy

INSTRUCTION:
Improve the following text while maintaining consistency...

TEXT TO EDIT:
The hero walked down the street.
```

### Result

The AI generates text that:
- ✅ Maintains all established facts
- ✅ Respects character personalities
- ✅ Follows the plot timeline
- ✅ Uses consistent world-building
- ✅ Continues from previous chapters

## 🔍 Technical Details

### LLM Service

**File**: `src/services/llm_service.py`

**Key Methods**:
- `generate_text()` - Core text generation
- `generate_questions()` - Question generation
- `extract_entities()` - Entity extraction from text

**Configuration**:
- Model: `gemini-2.0-flash-exp`
- Temperature: 0.7 (editing), 0.8 (generation)
- Max tokens: Configurable

### Editing Agent

**File**: `src/agents/editing_agent.py`

**Key Methods**:
- `improve_text()` - Improve prose quality
- `expand_text()` - Add detail and description
- `rephrase_text()` - Rewrite text
- `suggest_next_chapter()` - Chapter planning
- `generate_paragraph()` - Content generation

**Prompt Templates**:
- Each method uses specialized prompts
- All prompts include Truth context
- All prompts include previous chapters

### WorldBuilding Agent

**File**: `src/agents/worldbuilding_agent.py`

**Key Methods**:
- `generate_follow_up_questions()` - AI question generation
- `extract_entities_from_answer()` - AI entity extraction
- `_generate_ai_questions()` - Internal AI question logic

**Features**:
- Contextual question generation
- Automatic entity detection
- Structured data extraction

## 🎨 UI Integration

### Editor UI

**Location**: `app.py` - `show_editor()` function

**Features**:
- Text selection for editing
- AI action buttons
- Result display with apply/discard
- Loading spinners
- Error handling

**State Management**:
- `st.session_state.llm_service` - LLM service instance
- `st.session_state.editing_agent` - Editing agent instance
- `st.session_state.ai_result` - Current AI result
- `st.session_state.selected_text` - Selected text for editing

### World-Building UI

**Location**: `app.py` - `show_worldbuilding()` function

**Features**:
- Automatic question generation
- Entity extraction feedback
- Progress tracking
- Question tree navigation

## 🚀 Performance

### Response Times

- **Text Editing**: 2-5 seconds
- **Question Generation**: 1-3 seconds
- **Entity Extraction**: 1-2 seconds
- **Chapter Planning**: 3-6 seconds

### Optimization

- Caching: LLM service is cached in session state
- Streaming: Not yet implemented (future enhancement)
- Batching: Not yet implemented (future enhancement)

## 🔒 Privacy & Security

### Data Handling

- **API Key**: Stored in .env file (not committed to git)
- **Story Data**: Sent to Google Gemini API for processing
- **Local Storage**: All data saved locally in JSON files
- **No Tracking**: No analytics or tracking

### Best Practices

1. **Keep API key secure**: Never commit .env to version control
2. **Review AI output**: Always review before accepting
3. **Backup projects**: Regularly backup your data folder
4. **Monitor usage**: Check API quota in Google AI Studio

## 🐛 Troubleshooting

### "AI service not available"

**Cause**: GOOGLE_API_KEY not set

**Solution**:
1. Check .env file exists
2. Verify API key is correct
3. Restart application

### "Error improving text"

**Cause**: API error or network issue

**Solution**:
1. Check internet connection
2. Verify API key is valid
3. Check API quota in Google AI Studio
4. Try again

### AI results are inconsistent

**Cause**: Insufficient Truth context

**Solution**:
1. Add more details to Truth
2. Answer more world-building questions
3. Provide more context in prompts

### Questions not generating

**Cause**: AI service not available or error

**Solution**:
1. Check GOOGLE_API_KEY is set
2. Fallback to rule-based questions works automatically
3. Check console for error messages

## 📊 API Usage

### Costs

- **Model**: Gemini 2.0 Flash (free tier available)
- **Free Tier**: 15 requests per minute
- **Paid Tier**: Higher limits available

### Monitoring

Check usage at: [Google AI Studio](https://makersuite.google.com/app/apikey)

### Optimization Tips

1. **Select specific text**: Don't edit entire chapters unnecessarily
2. **Batch operations**: Plan multiple edits before applying
3. **Use fallbacks**: Rule-based features work without API
4. **Cache results**: Save good AI outputs for reuse

## 🎓 Best Practices

### For Best AI Results

1. **Build detailed Truth**: More context = better results
2. **Answer questions thoroughly**: Detailed answers = better questions
3. **Review and refine**: AI is an assistant, you're the author
4. **Iterate**: Use AI multiple times to refine
5. **Maintain consistency**: Keep Truth updated

### For Efficient Usage

1. **Start with world-building**: Build Truth first
2. **Use AI for polish**: Write first, improve with AI
3. **Select carefully**: Edit specific sections, not everything
4. **Save good results**: Keep successful AI outputs
5. **Learn patterns**: Understand what prompts work best

## 🔮 Future Enhancements

### Planned Features

- [ ] Streaming responses for real-time feedback
- [ ] Batch editing for multiple chapters
- [ ] Custom prompt templates
- [ ] AI-powered plot hole detection
- [ ] Character voice consistency checking
- [ ] Automatic chapter summaries
- [ ] Multi-language support

### Experimental Features

- [ ] Voice AI integration (speech-to-text)
- [ ] Image generation for scenes
- [ ] Audio narration generation
- [ ] Collaborative editing with AI

## 📚 Additional Resources

- [Google Gemini Documentation](https://ai.google.dev/docs)
- [Prompt Engineering Guide](https://ai.google.dev/docs/prompt_best_practices)
- [API Reference](https://ai.google.dev/api/python)

---

**AI Features Status**: ✅ **FULLY IMPLEMENTED AND READY TO USE**

Set your GOOGLE_API_KEY and start writing with AI assistance!
