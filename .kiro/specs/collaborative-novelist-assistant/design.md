# Design Document

## Overview

The AI Novel Writing Editor is a Python-based application that assists novelists through an interactive world-building process and AI-powered writing assistance. The system uses Google's Agent Development Kit (ADK) and Gemini LLM to provide context-aware editing grounded in established story facts ("The Truth").

### Design Goals

1. **User-Centric AI Assistance**: AI acts as an assistant, not an author, keeping the user in creative control
2. **Consistency Through Truth**: All AI operations are grounded in established story facts to maintain continuity
3. **Flexible World-Building**: Non-linear question navigation allowing users to explore story aspects in any order
4. **Seamless Audio Integration**: Universal audio input across all text fields for natural voice interaction
5. **Modular Architecture**: Clear separation of concerns enabling independent component evolution

### Technology Stack

- **Language**: Python 3.9+
- **AI Framework**: Google Agent Development Kit (ADK)
- **LLM**: Google Gemini (via google-genai)
- **UI Framework**: Streamlit
- **Data Validation**: Pydantic
- **Storage**: JSON-based file system
- **Audio Processing**: Google Gemini Audio API

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Streamlit Web Interface                    │
│                         (app.py)                             │
└────────────┬────────────────────────────────────────────────┘
             │
    ┌────────┴────────────┬──────────────────┬────────────────┐
    │                     │                  │                │
┌───▼────────┐   ┌───────▼────────┐  ┌──────▼──────┐  ┌──────▼──────┐
│  Project   │   │ WorldBuilding  │  │   Editing   │  │    Audio    │
│  Manager   │   │     Agent      │  │    Agent    │  │   Service   │
└───┬────────┘   └────────┬───────┘  └──────┬──────┘  └──────┬──────┘
    │                     │                  │                │
    │            ┌────────▼──────────────────▼────────────────▼────┐
    │            │         Truth Knowledge Base                     │
    │            │    (Characters, Plot Events, Settings)           │
    │            └──────────────────────────────────────────────────┘
    │
┌───▼────────┐
│  Storage   │
│  Service   │
└────────────┘
```

### Component Interaction Flow

```
User Input → UI Layer → Service Layer → Agent Layer → LLM API
                ↓           ↓              ↓
            Session     Storage        Truth KB
             State      Service
```

## Components and Interfaces

### 1. Data Models (`src/models/`)

#### Truth Knowledge Base Models (`truth.py`)

**Character Model**
```python
class Character:
  id: str
  name: str
  description: str
  traits: list[str]
  backstory: str
  relationships: dict[str, str]  # character_id -> relationship description
```

**PlotEvent Model**
```python
class PlotEvent:
  id: str
  title: str
  description: str
  order: int
  significance: str
  related_characters: list[str]
  related_settings: list[str]
```

**Setting Model**
```python
class Setting:
  id: str
  name: str
  type: str  # location, magic_system, organization, object
  description: str
  properties: dict[str, str]
```

**QuestionNode Model**
```python
class QuestionNode:
  id: str
  question: str
  answer: str | None
  entity_type: EntityType  # character, plot_event, setting
  status: QuestionStatus  # pending, answered, partially_answered
  parent_id: str | None
  children_ids: list[str]
  related_entity_ids: list[str]
```

**QuestionTree Model**
```python
class QuestionTree:
  root_id: str
  nodes: dict[str, QuestionNode]
  
  def get_pending_questions() -> list[QuestionNode]
  def get_answered_questions() -> list[QuestionNode]
  def get_node(node_id: str) -> QuestionNode | None
  def add_node(node: QuestionNode) -> None
  def update_node_status(node_id: str, status: QuestionStatus) -> None
```

**TruthKnowledgeBase Model**
```python
class TruthKnowledgeBase:
  characters: dict[str, Character]
  plot_events: dict[str, PlotEvent]
  settings: dict[str, Setting]
  question_tree: QuestionTree | None
  
  def search(query: str) -> list[dict]
  def add_character(character: Character) -> None
  def add_plot_event(event: PlotEvent) -> None
  def add_setting(setting: Setting) -> None
  def update_character(character_id: str, character: Character) -> None
  def update_plot_event(event_id: str, event: PlotEvent) -> None
  def update_setting(setting_id: str, setting: Setting) -> None
  def delete_character(character_id: str) -> bool
  def delete_plot_event(event_id: str) -> bool
  def delete_setting(setting_id: str) -> bool
```

#### Project Models (`project.py`)

**Chapter Model**
```python
class Chapter:
  id: str
  number: int
  title: str
  content: str
  word_count: int
  created_at: datetime
  updated_at: datetime
  
  def update_word_count() -> None
```

**Project Model**
```python
class Project:
  id: str
  title: str
  description: str
  author: str
  genre: str
  chapters: dict[str, Chapter]
  truth: TruthKnowledgeBase
  is_example: bool
  created_at: datetime
  updated_at: datetime
  
  def get_sorted_chapters() -> list[Chapter]
  def get_total_word_count() -> int
```

### 2. Services (`src/services/`)

#### StorageService (`storage.py`)

**Purpose**: Handles persistence of projects to file system

**Interface**:
```python
class StorageService:
  def __init__(base_path: str)
  def save_project(project: Project) -> None
  def load_project(project_id: str) -> Project | None
  def list_projects() -> list[Project]
  def delete_project(project_id: str) -> bool
  def project_exists(project_id: str) -> bool
```

**Storage Structure**:
```
data/
└── projects/
    ├── {project_id}/
    │   ├── project.json
    │   └── truth.json
    └── examples/
        └── {example_id}/
            ├── project.json
            └── truth.json
```

#### ProjectManager (`project_manager.py`)

**Purpose**: Business logic for project operations

**Interface**:
```python
class ProjectManager:
  def __init__(storage: StorageService)
  def create_project(title, description, author, genre) -> Project
  def list_all_projects() -> list[Project]
  def get_example_projects() -> list[Project]
  def delete_project(project_id: str) -> bool
  def add_chapter(number: int, title: str) -> Chapter
  def update_chapter_content(chapter_id: str, content: str) -> None
  def save_current_project() -> None
```

#### LLMService (`llm_service.py`)

**Purpose**: Wrapper for Google Gemini API interactions

**Interface**:
```python
class LLMService:
  def __init__(api_key: str | None = None)
  def is_available() -> bool
  def generate_text(prompt: str, context: dict | None = None) -> str
  def generate_with_json_schema(prompt: str, schema: dict) -> dict
  def count_tokens(text: str) -> int
```

**Configuration**:
- Model: `gemini-2.0-flash-exp`
- Temperature: 0.7 for creative tasks, 0.3 for structured extraction
- Max tokens: 8192 for generation, 2048 for extraction

#### AudioService (`audio_service.py`)

**Purpose**: Handle audio transcription using Gemini Audio API

**Interface**:
```python
class AudioService:
  def __init__(api_key: str | None = None)
  def is_available() -> bool
  def transcribe_audio(audio_data: bytes, prompt: str) -> str
  def transcribe_file(file_path: str, prompt: str) -> str
```

**Supported Formats**: MP3, WAV, FLAC, OGG, WebM

### 3. AI Agents (`src/agents/`)

#### WorldBuildingAgent (`worldbuilding_agent.py`)

**Purpose**: Conducts interactive Q&A to build the Truth knowledge base

**Interface**:
```python
class WorldBuildingAgent:
  def __init__(truth: TruthKnowledgeBase, llm_service: LLMService)
  def initialize_question_tree(initial_answer: str) -> None
  def generate_follow_up_questions(answer: str, parent_id: str) -> list[QuestionNode]
  def answer_question(question_id: str, answer: str) -> list[QuestionNode]
  def extract_entities(answer: str) -> dict
```

**Question Generation Strategy**:
1. Analyze answer for key entities (characters, plot points, settings)
2. Generate 2-5 follow-up questions per entity
3. Cross-reference with existing question tree to avoid duplicates
4. Categorize questions by entity type
5. Add questions as children of current node

**Entity Extraction Process**:
```
Answer Text → LLM with JSON Schema → Structured Entities
                                          ↓
                                    Update Truth KB
                                          ↓
                                  Generate Questions
```

#### EditingAgent (`editing_agent.py`)

**Purpose**: Provides AI-assisted editing grounded in Truth

**Interface**:
```python
class EditingAgent:
  def __init__(truth: TruthKnowledgeBase, llm_service: LLMService)
  def improve_text(text: str, chapter: Chapter, all_chapters: list[Chapter]) -> str
  def expand_text(text: str, chapter: Chapter, all_chapters: list[Chapter]) -> str
  def rephrase_text(text: str, chapter: Chapter, all_chapters: list[Chapter]) -> str
  def suggest_next_chapter(all_chapters: list[Chapter]) -> str
  def create_editing_prompt(action: str, text: str, context: dict) -> str
```

**Context Building Strategy**:
```python
def build_context(chapter: Chapter, all_chapters: list[Chapter]) -> dict:
  return {
    "truth": {
      "characters": [serialize(c) for c in truth.characters.values()],
      "plot_events": [serialize(e) for e in truth.plot_events.values()],
      "settings": [serialize(s) for s in truth.settings.values()]
    },
    "previous_chapters": [
      {"number": c.number, "title": c.title, "summary": c.content[:500]}
      for c in all_chapters if c.number < chapter.number
    ],
    "current_chapter": {
      "number": chapter.number,
      "title": chapter.title
    }
  }
```

### 4. User Interface (`src/ui/`)

#### Universal Audio Input (`audio_input.py`)

**Purpose**: Provide consistent audio input across all text fields

**Interface**:
```python
def universal_text_input(
  label: str,
  key: str,
  audio_service: AudioService,
  input_type: str = "text_input",  # text_input, text_area
  height: int | None = None,
  help_text: str | None = None,
  audio_prompt: str | None = None,
  default_value: str = ""
) -> str
```

**Features**:
- Seamless integration with Streamlit text inputs
- Support for both microphone recording and file upload
- Automatic transcription using Gemini Audio API
- Transcript merging with existing text
- Visual feedback during recording/processing

#### Truth Editors (`truth_editors.py`)

**Purpose**: Provide editing and creation interfaces for truth entities

**Interface**:
```python
def render_character_editor(
  project: Project,
  character_id: str | None = None,
  audio_service: AudioService
) -> None

def render_plot_event_editor(
  project: Project,
  event_id: str | None = None,
  audio_service: AudioService
) -> None

def render_setting_editor(
  project: Project,
  setting_id: str | None = None,
  audio_service: AudioService
) -> None
```

**Features**:
- Create new entities or edit existing ones
- Audio input support for all text fields
- Relationship management (link to other entities)
- Real-time validation
- Delete functionality with confirmation
- Auto-save on changes

#### Mind Map Visualization (`mindmap.py`)

**Purpose**: Interactive visual representation of question tree

**Interface**:
```python
def render_mindmap(question_tree: QuestionTree) -> str | None
def get_mindmap_legend() -> str
```

**Visualization Features**:
- Node coloring by status (answered/pending)
- Entity type icons (character/plot/setting)
- Interactive node selection
- Zoom and pan controls
- Hierarchical layout

## Data Models

### Entity Relationship Diagram

```
Project
  ├── id: str
  ├── title: str
  ├── chapters: dict[str, Chapter]
  └── truth: TruthKnowledgeBase
        ├── characters: dict[str, Character]
        ├── plot_events: dict[str, PlotEvent]
        ├── settings: dict[str, Setting]
        └── question_tree: QuestionTree
              └── nodes: dict[str, QuestionNode]
                    ├── parent_id: str
                    ├── children_ids: list[str]
                    └── related_entity_ids: list[str]
```

### Data Flow Diagrams

#### World-Building Flow
```
User Answer
    ↓
WorldBuildingAgent.answer_question()
    ↓
Extract Entities (LLM + JSON Schema)
    ↓
Update Truth KB
    ↓
Generate Follow-up Questions (LLM)
    ↓
Update Question Tree
    ↓
Save Project
```

#### Editing Flow
```
User Selects Text + Action
    ↓
EditingAgent.create_editing_prompt()
    ↓
Build Context (Truth + Previous Chapters)
    ↓
Generate Prompt with Context
    ↓
LLM API Call
    ↓
Return Grounded Response
    ↓
User Accepts/Rejects
```

## Error Handling

### Error Categories

1. **API Errors**: LLM API failures, rate limits, authentication
2. **Storage Errors**: File system access, JSON parsing, corruption
3. **Validation Errors**: Invalid data models, missing required fields
4. **User Input Errors**: Empty inputs, invalid formats

### Error Handling Strategy

**API Errors**:
```python
try:
  response = llm_service.generate_text(prompt)
except APIError as e:
  if e.status_code == 429:
    # Rate limit - retry with exponential backoff
    retry_with_backoff()
  elif e.status_code == 401:
    # Authentication - show user-friendly message
    show_api_key_error()
  else:
    # Other errors - log and show generic message
    log_error(e)
    show_generic_error()
```

**Storage Errors**:
```python
try:
  project = storage.load_project(project_id)
except FileNotFoundError:
  show_error("Project not found")
except JSONDecodeError:
  show_error("Project file corrupted")
  offer_recovery_options()
```

**Validation Errors**:
```python
try:
  project = Project(**data)
except ValidationError as e:
  log_validation_error(e)
  show_field_errors(e.errors())
```

### Graceful Degradation

- **No API Key**: Disable AI features, allow manual writing
- **Audio Unavailable**: Fall back to text-only input
- **Storage Failure**: Keep in-memory state, retry save
- **LLM Timeout**: Show partial results, allow retry

## Testing Strategy

### Unit Tests

**Models** (`tests/unittests/models/`):
- Pydantic model validation
- Data serialization/deserialization
- Model methods (word count, sorting, etc.)

**Services** (`tests/unittests/services/`):
- Storage operations (CRUD)
- Project manager business logic
- LLM service mocking

**Agents** (`tests/unittests/agents/`):
- Question generation logic
- Entity extraction
- Context building
- Prompt creation

### Integration Tests

**End-to-End Workflows** (`tests/integration/`):
- Project creation → World-building → Writing
- Question answering → Entity extraction → Truth update
- Text editing → Context building → LLM call

**Storage Integration**:
- Save/load project cycles
- Data persistence verification
- File system operations

### Test Data

**Example Projects**:
- Fantasy novel with magic system
- Sci-fi with complex timeline
- Mystery with multiple characters

**Mock Responses**:
- LLM responses for question generation
- Entity extraction results
- Editing suggestions

### Testing Tools

- **pytest**: Test runner
- **pytest-mock**: Mocking LLM calls
- **pytest-cov**: Code coverage
- **hypothesis**: Property-based testing for models

### Coverage Goals

- Models: 95%+ coverage
- Services: 90%+ coverage
- Agents: 85%+ coverage
- UI: Manual testing (Streamlit limitations)

## Performance Considerations

### Optimization Strategies

**Question Tree Operations**:
- Current: O(n) traversal for pending questions
- Optimization: Maintain separate pending/answered indices
- Expected improvement: O(1) lookup

**Truth Search**:
- Current: Linear scan through all entities
- Optimization: Add in-memory search index
- Expected improvement: O(log n) search

**LLM Context Size**:
- Current: Include all Truth + all previous chapters
- Optimization: Summarize distant chapters, include only relevant Truth entities
- Expected improvement: 50% token reduction

**Storage**:
- Current: Save entire project on every change
- Optimization: Incremental saves, debouncing
- Expected improvement: 80% reduction in I/O

### Scalability Limits

**Current System**:
- Projects: Unlimited (file-based)
- Chapters per project: ~100 (memory constraint)
- Truth entities: ~1000 (search performance)
- Question tree nodes: ~500 (UI rendering)

**Scaling Solutions**:
1. **Database Backend**: Replace JSON with PostgreSQL
2. **Lazy Loading**: Load chapters on demand
3. **Vector Search**: Use Vertex AI for Truth search
4. **Pagination**: Paginate question tree views

## Security Considerations

### API Key Management

- Store in `.env` file (not committed)
- Load via `python-dotenv`
- Never log or expose in UI
- Validate on startup

### Data Privacy

- All data stored locally
- No external data transmission except LLM API
- User controls all project data
- No telemetry or analytics

### Input Validation

- Sanitize all user inputs
- Validate file uploads (audio)
- Prevent path traversal in storage
- Limit file sizes

### Dependency Security

- Pin dependency versions
- Regular security audits
- Use official Google SDKs
- Minimal third-party dependencies

## Deployment Considerations

### Local Development

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add GOOGLE_API_KEY to .env
streamlit run app.py
```

### Production Deployment

**Option 1: Docker Container**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

**Option 2: Cloud Run**
- Package as container
- Deploy to Google Cloud Run
- Set GOOGLE_API_KEY as secret
- Configure persistent storage

**Option 3: Local Executable**
- Use PyInstaller to create standalone executable
- Bundle Python runtime
- Include all dependencies
- Distribute as desktop app

### Environment Variables

```
GOOGLE_API_KEY=<required>
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
DATA_PATH=data/projects
LOG_LEVEL=INFO
```

## Future Enhancements

### Phase 1: Core Improvements (Next 3 months)

1. **Full Voice AI Integration**
   - Real-time speech recognition
   - Voice-driven Q&A without typing
   - Text-to-speech for AI responses

2. **Advanced Question Tree**
   - AI-suggested question priorities
   - Automatic gap detection
   - Smart question merging

3. **Enhanced Context Management**
   - Chapter summarization
   - Relevant entity extraction
   - Dynamic context window

### Phase 2: Collaboration (3-6 months)

1. **Multi-User Support**
   - Real-time collaboration
   - User permissions
   - Change tracking

2. **Version Control**
   - Chapter versioning
   - Diff visualization
   - Rollback capability

3. **Comments and Annotations**
   - Inline comments
   - Feedback system
   - Review workflow

### Phase 3: Publishing (6-12 months)

1. **Export Formats**
   - PDF with formatting
   - EPUB for e-readers
   - DOCX for editing

2. **Publishing Integration**
   - Direct publishing to platforms
   - Formatting templates
   - Cover design tools

3. **Analytics**
   - Writing statistics
   - Progress tracking
   - Goal setting

## Design Decisions and Rationales

### Why Streamlit?

**Pros**:
- Rapid prototyping
- Python-native (no JS required)
- Built-in state management
- Easy deployment

**Cons**:
- Limited customization
- Performance with large apps
- No native mobile support

**Decision**: Streamlit is ideal for MVP and internal tools. Consider React/Next.js for production.

### Why JSON Storage?

**Pros**:
- Simple implementation
- No database setup
- Easy debugging
- Version control friendly

**Cons**:
- No concurrent access
- Limited query capabilities
- Scalability issues

**Decision**: JSON is sufficient for single-user MVP. Migrate to PostgreSQL for multi-user.

### Why Google ADK?

**Pros**:
- Official Google support
- Integrated with Gemini
- Agent orchestration
- Tool calling support

**Cons**:
- Vendor lock-in
- Learning curve
- Limited documentation

**Decision**: ADK provides best integration with Gemini and future-proofs for multi-agent features.

### Why Pydantic?

**Pros**:
- Type safety
- Validation
- JSON serialization
- IDE support

**Cons**:
- Runtime overhead
- Verbose definitions

**Decision**: Type safety and validation are critical for data integrity. Performance impact is negligible.

## Conclusion

This design provides a solid foundation for the AI Novel Writing Editor with clear separation of concerns, extensibility, and user-centric features. The modular architecture enables independent evolution of components while maintaining consistency through the Truth knowledge base. The design prioritizes user control, data privacy, and graceful degradation to ensure a reliable writing experience.
