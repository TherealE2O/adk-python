# AI Novel Editor - Architecture Documentation

## Overview

The AI Novel Editor is a Python-based application that uses Google's Agent Development Kit (ADK) to provide AI-assisted novel writing capabilities. The application is structured around three main modules that work together to provide a comprehensive writing experience.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Web UI                         │
│                        (app.py)                              │
└────────────────┬────────────────────────────────────────────┘
                 │
    ┌────────────┴────────────┬──────────────────┐
    │                         │                  │
┌───▼────────┐    ┌──────────▼─────┐   ┌───────▼────────┐
│  Project   │    │  WorldBuilding │   │    Editing     │
│  Manager   │    │     Agent      │   │     Agent      │
└───┬────────┘    └────────┬───────┘   └───────┬────────┘
    │                      │                    │
    │             ┌────────▼────────────────────▼────┐
    │             │   Truth Knowledge Base           │
    │             │  (Characters, Plot, Settings)    │
    │             └──────────────────────────────────┘
    │
┌───▼────────┐
│  Storage   │
│  Service   │
└────────────┘
```

## Core Components

### 1. Data Models (`src/models/`)

#### Truth Knowledge Base (`truth.py`)
The foundation of the application, storing all established story facts:

- **Character**: Represents story characters with traits, backstory, relationships
- **PlotEvent**: Timeline events with order, description, and significance
- **Setting**: Locations and world-building elements
- **QuestionNode**: Individual questions in the Q&A tree
- **QuestionTree**: Branching structure of questions with navigation
- **TruthKnowledgeBase**: Container for all truth data with search capabilities

#### Project Models (`project.py`)
Manages the novel project structure:

- **Chapter**: Individual chapters with content, word count, metadata
- **Project**: Top-level project containing chapters and truth

### 2. Services (`src/services/`)

#### StorageService (`storage.py`)
Handles persistence of projects to disk:
- JSON-based file storage
- CRUD operations for projects
- Directory management

#### ProjectManager (`project_manager.py`)
Business logic for project operations:
- Project lifecycle management
- Chapter management
- Integration with storage service

### 3. AI Agents (`src/agents/`)

#### WorldBuildingAgent (`worldbuilding_agent.py`)
Conducts interactive Q&A to build the Truth:

**Key Features:**
- Initializes question tree from initial story description
- Generates follow-up questions based on answers
- Extracts entities (characters, plot, settings) from answers
- Manages question tree navigation
- Supports non-linear question answering

**Question Generation Logic:**
```python
Answer → Entity Detection → Generate Questions
                ↓
         Update Question Tree
                ↓
         Extract Entities → Update Truth
```

#### EditingAgent (`editing_agent.py`)
Provides AI-assisted editing grounded in Truth:

**Key Features:**
- Creates context-aware prompts
- Includes Truth and previous chapters in context
- Supports multiple editing actions:
  - Improve: Enhance prose quality
  - Expand: Add detail and description
  - Rephrase: Alternative phrasing
- Chapter planning and suggestions

**Context Building:**
```
Truth Context + Previous Chapters + User Instruction
                ↓
        Complete Prompt for LLM
                ↓
        Grounded AI Response
```

### 4. User Interface (`app.py`)

Built with Streamlit, providing three main views:

#### Project Manager View
- List all projects
- Create new projects
- Open existing projects
- View example projects

#### World-Building View
- Interactive Q&A interface
- Question tree visualization
- Progress tracking
- Non-linear navigation

#### Editor View
- Chapter-based writing interface
- AI editing tools
- Truth viewers (characters, timeline, settings)
- Chapter management

## Data Flow

### 1. Project Creation Flow
```
User Input → ProjectManager.create_project()
                ↓
         Create Project with Truth
                ↓
         StorageService.save_project()
                ↓
         Initialize WorldBuildingAgent
```

### 2. World-Building Flow
```
Initial Answer → WorldBuildingAgent.initialize_question_tree()
                ↓
         Generate Follow-up Questions
                ↓
User Answers → WorldBuildingAgent.answer_question()
                ↓
         Extract Entities → Update Truth
                ↓
         Generate More Questions (recursive)
```

### 3. Editing Flow
```
User Selects Text + Action
                ↓
EditingAgent.create_editing_prompt()
                ↓
         Include Truth + Previous Chapters
                ↓
         Send to LLM (Google Gemini)
                ↓
         Return Grounded Response
```

## Key Design Patterns

### 1. Repository Pattern
`StorageService` acts as a repository, abstracting data persistence:
- Separates business logic from storage implementation
- Easy to swap storage backends (JSON → Database)

### 2. Agent Pattern
AI agents encapsulate specific AI behaviors:
- `WorldBuildingAgent`: Q&A and entity extraction
- `EditingAgent`: Context-aware editing

### 3. State Management
Streamlit session state manages application state:
- Current project
- Current page
- Agent instances
- UI state

### 4. Separation of Concerns
Clear separation between:
- **Models**: Data structures
- **Services**: Business logic
- **Agents**: AI behavior
- **UI**: Presentation

## Integration with Google ADK

### Current Integration
The application is designed to integrate with Google ADK but currently uses a simplified implementation:

1. **Models**: Pydantic models compatible with ADK's type system
2. **Agent Structure**: Follows ADK agent patterns
3. **Context Management**: Similar to ADK's invocation context

### Future ADK Integration

To fully integrate with Google ADK:

```python
from google.adk import Agent
from google.genai import types

# World-building agent as ADK agent
worldbuilding_agent = Agent(
    name="worldbuilding_assistant",
    model="gemini-2.0-flash-exp",
    instruction="""
    You are a world-building assistant for novel writing.
    Ask insightful questions to help authors develop their story.
    Extract characters, plot events, and settings from answers.
    """,
    tools=[
        extract_character,
        extract_plot_event,
        extract_setting,
        generate_questions
    ]
)

# Editing agent as ADK agent
editing_agent = Agent(
    name="editing_assistant",
    model="gemini-2.0-flash-exp",
    instruction="""
    You are an editing assistant for novel writing.
    All edits must be consistent with the established Truth.
    Consider previous chapters for continuity.
    """,
    tools=[
        improve_text,
        expand_text,
        rephrase_text,
        suggest_next_chapter
    ]
)
```

## Scalability Considerations

### Current Limitations
- In-memory question tree (limited by RAM)
- JSON file storage (not suitable for large scale)
- No concurrent editing support
- Limited context window for large novels

### Scaling Solutions

1. **Database Backend**
   - Replace JSON storage with PostgreSQL/MongoDB
   - Enable multi-user support
   - Better query performance

2. **Vector Database for Truth**
   - Use Vertex AI Vector Search or similar
   - Enable semantic search across Truth
   - Handle larger context windows

3. **Distributed Agents**
   - Deploy agents as separate services
   - Use ADK's multi-agent orchestration
   - Scale agents independently

4. **Caching Strategy**
   - Cache frequently accessed Truth data
   - Use ADK's context caching for prompts
   - Reduce API calls

## Security Considerations

1. **API Key Management**
   - Store in environment variables
   - Never commit to version control
   - Use secret management in production

2. **Data Privacy**
   - User projects stored locally
   - No data sent to external services except LLM API
   - Consider encryption for sensitive content

3. **Input Validation**
   - Validate all user inputs
   - Sanitize before storage
   - Prevent injection attacks

## Testing Strategy

### Unit Tests
- Model validation
- Service logic
- Agent behavior

### Integration Tests
- End-to-end workflows
- Storage operations
- Agent interactions

### UI Tests
- Streamlit component testing
- User flow validation

## Future Enhancements

### Phase 1: Core Improvements
- Full Google ADK integration
- Voice AI implementation
- Real-time collaboration

### Phase 2: Advanced Features
- Export to multiple formats (PDF, EPUB, DOCX)
- Advanced question tree visualization
- Memory/RAG for larger contexts

### Phase 3: Enterprise Features
- Multi-user workspaces
- Version control for chapters
- Publishing workflow integration

## Performance Optimization

### Current Performance
- Fast for small projects (<10 chapters)
- Question tree operations: O(n) where n = number of nodes
- Search operations: O(n) linear scan

### Optimization Opportunities
1. **Indexing**: Add search indices for Truth entities
2. **Lazy Loading**: Load chapters on demand
3. **Caching**: Cache LLM responses for common operations
4. **Batch Operations**: Batch multiple AI requests

## Deployment

### Local Development
```bash
./run.sh
```

### Production Deployment
1. **Containerization**: Docker container with dependencies
2. **Cloud Deployment**: Deploy to Cloud Run, AWS ECS, or similar
3. **Environment Management**: Use proper secret management
4. **Monitoring**: Add logging and error tracking

## Conclusion

The AI Novel Editor is built with a modular, scalable architecture that separates concerns and enables future enhancements. The design follows best practices for AI agent applications and is ready for integration with Google's ADK for production use.
