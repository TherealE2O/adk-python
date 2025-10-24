# Implementation Plan

- [x] 1. Set up project structure and core interfaces





  - Create directory structure for models, services, agents, and UI components
  - Define base interfaces and abstract classes for services and agents
  - Set up configuration management for environment variables
  - _Requirements: 1.1, 1.2_

- [x] 2. Implement Truth Knowledge Base data models





  - [x] 2.1 Create Character, PlotEvent, and Setting models

    - Write Pydantic models with validation for Character (name, description, traits, backstory, relationships)
    - Write Pydantic models for PlotEvent (title, description, order, significance, related entities)
    - Write Pydantic models for Setting (name, type, description, properties)
    - _Requirements: 10.2, 11.2, 12.2_


  - [x] 2.2 Create QuestionNode and QuestionTree models







    - Implement QuestionNode with id, question, answer, entity_type, status, parent_id, children_ids
    - Implement QuestionTree with root_id, nodes dictionary, and navigation methods
    - Add methods: get_pending_questions(), get_answered_questions(), get_node()
    - _Requirements: 3.2, 3.3, 4.1, 4.2_


  - [x] 2.3 Create TruthKnowledgeBase container model





    - Implement TruthKnowledgeBase with dictionaries for characters, plot_events, settings
    - Add question_tree field
    - Implement search() method for global Truth search
    - Add methods: add_character(), add_plot_event(), add_setting()
    - _Requirements: 13.2, 13.3_

- [x] 3. Implement Project and Chapter models




  - [x] 3.1 Create Chapter model


    - Implement Chapter with id, number, title, content, word_count, timestamps
    - Add update_word_count() method
    - _Requirements: 6.2, 6.4_

  - [x] 3.2 Create Project model


    - Implement Project with id, title, description, author, genre, chapters, truth
    - Add get_sorted_chapters() method
    - Add get_total_word_count() method
    - _Requirements: 1.2, 1.5_

- [x] 4. Implement StorageService for persistence





  - [x] 4.1 Create JSON-based storage implementation


    - Implement save_project() to serialize Project to JSON files
    - Implement load_project() to deserialize JSON to Project objects
    - Create directory structure: data/projects/{project_id}/
    - Handle file I/O errors gracefully
    - _Requirements: 1.5_


  - [x] 4.2 Implement project listing and management

    - Implement list_projects() to scan project directories
    - Implement delete_project() to remove project files
    - Implement project_exists() check
    - Add support for example projects in data/projects/examples/
    - _Requirements: 1.2, 1.3_

- [x] 5. Implement ProjectManager service







  - [x] 5.1 Create project lifecycle management

    - Implement create_project() to initialize new Project with empty Truth
    - Implement list_all_projects() combining user and example projects
    - Implement get_example_projects() filtering
    - Implement delete_project() with confirmation
    - _Requirements: 1.1, 1.2, 1.3, 1.4_


  - [x] 5.2 Implement chapter management

    - Implement add_chapter() to create new Chapter in Project
    - Implement update_chapter_content() to modify Chapter content
    - Implement save_current_project() to persist changes
    - _Requirements: 6.3, 6.4, 6.5_

- [x] 6. Implement LLMService wrapper





  - [x] 6.1 Create Gemini API integration


    - Initialize Google Gemini client with API key from environment
    - Implement generate_text() for general text generation
    - Implement generate_with_json_schema() for structured extraction
    - Add is_available() check for API key presence
    - Configure model: gemini-2.0-flash-exp
    - _Requirements: 2.4, 3.1, 7.2_


  - [x] 6.2 Add error handling and retry logic

    - Handle API errors (rate limits, authentication, timeouts)
    - Implement exponential backoff for rate limits
    - Add user-friendly error messages
    - Log errors for debugging
    - _Requirements: 2.4, 7.2_

- [x] 7. Implement AudioService for transcription




  - [x] 7.1 Create Gemini Audio API integration


    - Initialize audio transcription with Gemini API
    - Implement transcribe_audio() for byte data
    - Implement transcribe_file() for uploaded files
    - Support formats: MP3, WAV, FLAC, OGG, WebM
    - Add is_available() check
    - _Requirements: 2.3_

  - [x] 7.2 Add audio processing utilities


    - Validate audio file formats
    - Handle file size limits
    - Add error handling for corrupted files
    - Provide user feedback during processing
    - _Requirements: 2.3_

- [x] 8. Implement WorldBuildingAgent
















  - [x] 8.1 Create question tree initialization


    - Implement initialize_question_tree() to create root question
    - Parse initial answer to identify story elements
    - Create root QuestionNode with initial question and answer
    - _Requirements: 2.1, 2.2, 2.4_


  - [x] 8.2 Implement entity extraction

    - Create extract_entities() using LLM with JSON schema
    - Extract characters with name, description, traits
    - Extract plot events with title, description, order
    - Extract settings with name, type, description
    - Update Truth knowledge base with extracted entities
    - _Requirements: 3.1, 3.2_



  - [x] 8.3 Implement question generation

    - Create generate_follow_up_questions() using LLM
    - Analyze answer to identify key entities and concepts
    - Generate 2-5 follow-up questions per entity
    - Categorize questions by entity type (character, plot_event, setting)
    - Add questions as children in QuestionTree


    - _Requirements: 3.2, 3.3, 3.4_


  - [x] 8.4 Implement cross-branch analysis


    - Analyze new answers against entire QuestionTree
    - Identify questions partially or fully answered by new information

    - Update question status (pending, partially_answered, answered)
    - Link related questions via related_entity_ids
    - _Requirements: 3.5_




  - [x] 8.5 Create answer processing workflow

    - Implement answer_question() to handle user answers
    - Update QuestionNode with answer and status
    - Trigger entity extraction
    - Trigger follow-up question generation
    - Return list of newly generated questions
    - _Requirements: 2.4, 3.1, 3.2_

- [x] 9. Implement EditingAgent






  - [x] 9.1 Create context building system

    - Implement build_context() to gather Truth and chapter context
    - Serialize characters, plot_events, settings from Truth
    - Include previous chapters with summaries
    - Include current chapter metadata
    - _Requirements: 7.2, 7.3, 7.4_


  - [x] 9.2 Implement text editing operations

    - Implement improve_text() with context-aware prompts
    - Implement expand_text() with detail addition instructions
    - Implement rephrase_text() with alternative phrasing guidance
    - Create create_editing_prompt() to build prompts with context
    - Ensure all operations include Truth and previous chapters in context
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_


  - [x] 9.3 Implement auto-completion and generation

    - Create suggest_completion() for paragraph-level suggestions
    - Implement generate_paragraph() based on user instruction
    - Ensure consistency with Truth and previous chapters
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_


  - [x] 9.4 Implement chapter-level operations


    - Implement edit_chapter() for full chapter revision
    - Implement suggest_next_chapter() analyzing current progress and Truth
    - Implement plan_chapter() to generate chapter outlines
    - Ensure all operations maintain consistency with Truth
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 10. Implement universal audio input UI component





  - [x] 10.1 Create universal_text_input() function


    - Support both text_input and text_area Streamlit widgets
    - Add audio mode selector (text, upload, record)
    - Integrate with AudioService for transcription
    - Handle microphone recording via browser
    - Handle file uploads for pre-recorded audio
    - _Requirements: 2.3_


  - [x] 10.2 Add transcript management

    - Store transcripts in session state
    - Merge transcripts with existing text
    - Provide clear/edit transcript options
    - Show visual feedback during recording/processing
    - _Requirements: 2.3_

- [x] 11. Implement project manager UI





  - [x] 11.1 Create project listing view


    - Display all user projects with title, description, genre, chapter count
    - Display example projects in separate section
    - Add open and delete buttons for each project
    - Show project statistics (total words, chapters)
    - _Requirements: 1.1, 1.2, 1.3_

  - [x] 11.2 Create project creation form


    - Add text inputs for title, description, author, genre
    - Integrate universal_text_input for audio support
    - Validate required fields (title)
    - Create project and navigate to world-building on submit
    - _Requirements: 1.4, 2.1_


  - [x] 11.3 Implement project loading

    - Load selected project into session state
    - Initialize WorldBuildingAgent with project Truth
    - Initialize EditingAgent with project Truth
    - Navigate to appropriate page (world-building or editor)
    - _Requirements: 1.5_

- [-] 12. Implement world-building UI



  - [x] 12.1 Create initial question interface


    - Display "What is your story about?" question
    - Use universal_text_input for answer with audio support
    - Initialize question tree on submit
    - Generate initial follow-up questions
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 12.2 Implement question tree visualization


    - Create tree view with expandable nodes
    - Create list by category view (characters, plot, settings)
    - Create timeline view showing question order
    - Add mind map view with interactive graph (if streamlit-agraph available)
    - Show status indicators (answered, pending)
    - Show entity type icons
    - _Requirements: 4.1, 4.2_



  - [x] 12.3 Create question answering interface

    - Display question selector dropdown
    - Show breadcrumb navigation (path from root to current question)
    - Use universal_text_input for answers with audio support
    - Submit answer and generate follow-up questions
    - Update question tree visualization
    - _Requirements: 4.3, 4.4, 4.5_


  - [x] 12.4 Add progress tracking

    - Show answered vs pending question counts
    - Display progress bar
    - Add "Start Writing" button to exit world-building
    - _Requirements: 5.1, 5.2, 5.3_

- [x] 13. Implement text editor UI
  - [x] 13.1 Create chapter management sidebar
    - List all chapters with number and title
    - Add chapter selection buttons
    - Create "Add Chapter" form with universal_text_input
    - Add navigation back to project manager
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

  - [x] 13.2 Create chapter editor
    - Display chapter number and title
    - Use universal_text_input for chapter content with audio support
    - Add save button to persist changes
    - Update word count automatically
    - _Requirements: 6.5, 8.1_

  - [x] 13.3 Implement AI editing toolbar
    - Add text selection input with universal_text_input
    - Create buttons for improve, expand, rephrase actions
    - Add suggest next chapter button
    - Disable buttons when API key not available
    - Show loading spinner during AI operations
    - _Requirements: 7.1, 7.2, 9.3_

  - [x] 13.4 Create AI result display
    - Show AI-generated result in expandable section
    - Add "Use This" button to apply suggestion
    - Add "Discard" button to reject suggestion
    - Handle text replacement for selected text
    - Handle text appending for full chapter operations
    - _Requirements: 7.2, 7.5, 8.4, 8.5_

- [x] 14. Enhance Truth viewer UIs
  - [x] 14.1 Enhance Character Sheet viewer
    - Add search functionality to find specific characters
    - Improve layout with better formatting for traits and relationships
    - Add character count and statistics
    - Show related plot events and settings for each character
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

  - [x] 14.2 Enhance Timeline viewer
    - Add filtering by character or setting
    - Show visual timeline with date/order markers
    - Add ability to jump to chapters where events occur
    - Include character involvement indicators
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

  - [x] 14.3 Enhance Setting and World-Building viewer
    - Add filtering by setting type
    - Show related characters and events for each setting
    - Add visual organization (tabs or categories)
    - Include setting usage statistics
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

  - [x] 14.4 Implement global Truth search
    - Create search bar in sidebar accessible from editor
    - Search across all Truth entities (characters, events, settings)
    - Display search results with entity type indicators
    - Allow navigation to full entity view from results
    - Add search result highlighting
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

- [x] 15. Implement session state management
  - [x] 15.1 Initialize session state variables
    - Set up current_page, current_project, current_chapter_id
    - Initialize agent instances (worldbuilding_agent, editing_agent)
    - Set up service instances (llm_service, audio_service)
    - Initialize UI state (ai_result, selected_text, audio_mode)
    - _Requirements: 1.1, 1.5_

  - [x] 15.2 Implement page navigation
    - Create navigation between project_manager, worldbuilding, editor pages
    - Preserve state during navigation
    - Handle back navigation
    - _Requirements: 1.1, 1.5, 5.1_

- [x] 16. Enhance error handling and user feedback
  - [x] 16.1 Add comprehensive API error handling
    - Review and enhance LLMService error handling with exponential backoff for rate limits
    - Add retry mechanism with user notification in UI
    - Display detailed timeout errors with retry option in Streamlit
    - Enhance error logging for debugging
    - _Requirements: 2.4, 7.2_

  - [x] 16.2 Enhance storage error handling
    - Add automatic backup before save operations in StorageService
    - Implement recovery wizard for corrupted projects in UI
    - Add data validation before save in ProjectManager
    - Show detailed error messages with recovery steps in UI
    - _Requirements: 1.5_

  - [x] 16.3 Add progress indicators and feedback
    - Add progress bars for long operations (entity extraction, question generation) in world-building UI
    - Show toast notifications for successful operations using st.toast()
    - Add confirmation dialogs for destructive actions (delete project, discard changes)
    - Implement auto-save with visual indicator in editor
    - _Requirements: 1.4, 2.2, 6.5_

- [x] 17. Create example projects
  - [x] 17.1 Create fantasy novel example
    - Create project.json with fantasy novel metadata (title, description, genre)
    - Build Truth with magic system, multiple characters (3-5), fantasy settings (2-3 locations)
    - Write 2-3 sample chapters (500-1000 words each) with established Truth
    - Create comprehensive question tree with answered questions (10-15 nodes)
    - Save to data/projects/examples/fantasy-quest/
    - _Requirements: 1.3_

  - [x] 17.2 Create sci-fi novel example
    - Create project.json with sci-fi novel metadata (title, description, genre)
    - Build Truth with complex timeline, futuristic settings (space stations, planets)
    - Write 2-3 sample chapters (500-1000 words each) with established Truth
    - Create comprehensive question tree with answered questions (10-15 nodes)
    - Save to data/projects/examples/space-odyssey/
    - _Requirements: 1.3_

- [x] 18. Add configuration and environment setup
  - [x] 18.1 Create environment configuration
    - Create .env.example with GOOGLE_API_KEY placeholder
    - Add .env to .gitignore
    - Document API key setup in README
    - _Requirements: 2.4, 7.2_

  - [x] 18.2 Create requirements.txt
    - List all Python dependencies with versions
    - Include streamlit, google-genai, pydantic, python-dotenv
    - Add optional dependencies (streamlit-agraph for mind map)
    - _Requirements: 1.1_

  - [x] 18.3 Create run script
    - Create run.sh for easy startup
    - Check for virtual environment
    - Check for .env file
    - Start Streamlit application
    - _Requirements: 1.1_





- [x] 20. Implement Truth entity editing and deletion
  - [x] 20.1 Add update and delete methods to TruthKnowledgeBase
    - Implement update_character() to modify existing Character in truth.characters
    - Implement update_plot_event() to modify existing PlotEvent in truth.plot_events
    - Implement update_setting() to modify existing Setting in truth.settings
    - Implement delete_character() to remove Character and clean up relationships
    - Implement delete_plot_event() to remove PlotEvent and clean up references
    - Implement delete_setting() to remove Setting and clean up references
    - Update updated_at timestamp on all modifications
    - _Requirements: 14.5, 14.6, 14.7_

  - [x] 20.2 Create truth_editors.py UI module
    - Create src/ui/truth_editors.py file
    - Import necessary models (Character, PlotEvent, Setting, Project)
    - Import universal_text_input for audio support
    - Set up module structure with editor functions
    - _Requirements: 14.1, 14.2, 14.3, 15.1, 15.2, 15.3_

  - [x] 20.3 Implement character editor UI
    - Create render_character_editor() function
    - Add mode parameter to switch between create/edit (character_id=None for create)
    - Display form with universal_text_input for name, description, backstory, physical_description, role
    - Add multi-select for traits (with option to add new traits)
    - Add relationship editor (select character + describe relationship)
    - Add save button that validates and calls add_character() or update_character()
    - Add delete button (edit mode only) with confirmation dialog
    - Show success/error messages using st.toast()
    - _Requirements: 14.1, 14.4, 14.5, 14.7, 14.8, 15.4, 15.5, 15.6, 15.7_

  - [x] 20.4 Implement plot event editor UI
    - Create render_plot_event_editor() function
    - Add mode parameter to switch between create/edit (event_id=None for create)
    - Display form with universal_text_input for title, description, significance, location, timestamp
    - Add number input for order (chronological position)
    - Add multi-select for characters_involved (from existing characters)
    - Add save button that validates and calls add_plot_event() or update_plot_event()
    - Add delete button (edit mode only) with confirmation dialog
    - Show success/error messages using st.toast()
    - _Requirements: 14.2, 14.4, 14.5, 14.7, 14.8, 15.4, 15.5, 15.6, 15.7_

  - [x] 20.5 Implement setting editor UI
    - Create render_setting_editor() function
    - Add mode parameter to switch between create/edit (setting_id=None for create)
    - Display form with universal_text_input for name, description, type
    - Add dynamic list input for rules (add/remove rules)
    - Add multi-select for related_characters (from existing characters)
    - Add multi-select for related_events (from existing plot events)
    - Add save button that validates and calls add_setting() or update_setting()
    - Add delete button (edit mode only) with confirmation dialog
    - Show success/error messages using st.toast()
    - _Requirements: 14.3, 14.4, 14.5, 14.7, 14.8, 15.4, 15.5, 15.6, 15.7_

  - [ ] 20.6 Integrate editors into truth viewers
    - Update render_character_viewer() to add "Edit" button for each character
    - Update render_timeline_viewer() to add "Edit" button for each event
    - Update render_settings_viewer() to add "Edit" button for each setting
    - When edit button clicked, set session state to show editor modal
    - Pass entity_id to editor function for edit mode
    - After save/delete, refresh viewer and clear editor state
    - _Requirements: 14.1, 14.2, 14.3_

  - [ ] 20.7 Add manual truth creation to editor sidebar
    - Add "Create Truth Entity" section to editor sidebar in app.py
    - Add button "➕ New Character" that opens character editor in create mode
    - Add button "➕ New Event" that opens plot event editor in create mode
    - Add button "➕ New Setting" that opens setting editor in create mode
    - Store editor state in session_state (show_truth_editor, editor_type, entity_id)
    - Render appropriate editor based on session state
    - _Requirements: 15.1, 15.2, 15.3_

  - [ ] 20.8 Add editor modal rendering to app.py
    - In show_editor() function, check for show_truth_editor session state
    - Render editor modal with close button
    - Call appropriate editor function (render_character_editor, render_plot_event_editor, render_setting_editor)
    - Pass audio_service for audio input support
    - Clear editor state after close/save
    - Save project after entity modifications
    - _Requirements: 14.4, 14.5, 15.4, 15.6_

- [ ] 21. Implement world-building access from editor
  - [ ] 21.1 Add world-building navigation to editor sidebar
    - Add "🌍 Continue World-Building" button to editor sidebar in app.py
    - Place button in prominent location (near truth viewers section)
    - Add tooltip explaining "Answer more questions to expand your Truth"
    - _Requirements: 16.1_

  - [ ] 21.2 Implement navigation to world-building from editor
    - When "Continue World-Building" button clicked, set current_page to 'worldbuilding'
    - Preserve current_project and worldbuilding_agent in session state
    - Ensure Question Tree state is maintained (don't reinitialize)
    - Save current project before navigation
    - Use st.rerun() to navigate to world-building page
    - _Requirements: 16.1, 16.2, 16.3, 16.7_

  - [ ] 21.3 Update world-building UI to handle mid-app access
    - In show_worldbuilding() function, check if question tree already exists
    - Skip initial question interface if question tree is already initialized
    - Display question tree visualization and answering interface directly
    - Show message "Continue building your story's Truth" instead of "Let's start building"
    - Maintain all existing answered questions and pending questions
    - _Requirements: 16.2, 16.3, 16.7_

  - [ ] 21.4 Add return to editor from world-building
    - Update "🚀 Start Writing" button text to "🚀 Return to Editor" when accessed from editor
    - Detect if user came from editor by checking if chapters exist
    - When returning to editor, preserve current_chapter_id if set
    - Save project before returning to editor
    - Use st.rerun() to navigate back to editor page
    - _Requirements: 16.5_

  - [ ] 21.5 Ensure Truth updates propagate to editor
    - After answering questions in world-building, verify Truth entities are updated
    - Ensure EditingAgent has access to updated Truth when returning to editor
    - Test that newly created entities appear in truth viewers
    - Verify that AI editing operations use updated Truth context
    - _Requirements: 16.4, 16.6_
