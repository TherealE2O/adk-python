"""Main Streamlit application for AI Novel Editor."""

from __future__ import annotations

import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

from src.services.storage import StorageService
from src.services.project_manager import ProjectManager
from src.services.llm_service import LLMService
from src.services.voice_service import VoiceService
from src.services.audio_service import AudioService
from src.agents.worldbuilding_agent import WorldBuildingAgent
from src.agents.editing_agent import EditingAgent
from src.models.project import Project, Chapter
from src.models.truth import QuestionNode
from src.ui.mindmap import render_mindmap, get_mindmap_legend, AGRAPH_AVAILABLE
from src.ui.audio_input import universal_text_input
from src.ui.truth_viewers import (
    render_character_viewer,
    render_timeline_viewer,
    render_settings_viewer,
    render_global_search
)
from src.ui.truth_editors import (
    render_character_editor,
    render_plot_event_editor,
    render_setting_editor
)

# Load environment variables
load_dotenv()

# Initialize services
@st.cache_resource
def get_services():
  """Initialize and cache services."""
  storage = StorageService(base_path="data/projects")
  project_manager = ProjectManager(storage)
  return storage, project_manager

storage, project_manager = get_services()

# Page configuration
st.set_page_config(
    page_title="AI Novel Editor",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session state initialization
if 'current_page' not in st.session_state:
  st.session_state.current_page = 'project_manager'
if 'current_project' not in st.session_state:
  st.session_state.current_project = None
if 'worldbuilding_agent' not in st.session_state:
  st.session_state.worldbuilding_agent = None
if 'editing_agent' not in st.session_state:
  st.session_state.editing_agent = None
if 'current_chapter_id' not in st.session_state:
  st.session_state.current_chapter_id = None
if 'llm_service' not in st.session_state:
  st.session_state.llm_service = LLMService()
if 'voice_service' not in st.session_state:
  st.session_state.voice_service = VoiceService()
if 'audio_service' not in st.session_state:
  st.session_state.audio_service = AudioService()
if 'ai_result' not in st.session_state:
  st.session_state.ai_result = None
if 'selected_text' not in st.session_state:
  st.session_state.selected_text = ""
if 'voice_enabled' not in st.session_state:
  st.session_state.voice_enabled = False
if 'listening' not in st.session_state:
  st.session_state.listening = False
if 'audio_mode' not in st.session_state:
  st.session_state.audio_mode = 'text'  # 'text', 'upload', 'record'
if 'last_save_time' not in st.session_state:
  st.session_state.last_save_time = None
if 'auto_save_enabled' not in st.session_state:
  st.session_state.auto_save_enabled = True


def show_project_manager():
  """Display the project manager page."""
  st.title("📚 AI Novel Editor - Project Manager")
  
  col1, col2 = st.columns([2, 1])
  
  with col1:
    st.header("Your Projects")
    projects = project_manager.list_all_projects()
    user_projects = [p for p in projects if not p.is_example]
    
    if user_projects:
      for project in user_projects:
        with st.expander(f"📖 {project.title}"):
          st.write(f"**Description:** {project.description}")
          st.write(f"**Genre:** {project.genre}")
          st.write(f"**Chapters:** {len(project.chapters)}")
          st.write(f"**Total Words:** {project.get_total_word_count()}")
          
          col_a, col_b = st.columns(2)
          with col_a:
            if st.button(f"Open", key=f"open_{project.id}"):
              try:
                st.session_state.current_project = project
                project_manager.current_project = project
                st.session_state.worldbuilding_agent = WorldBuildingAgent(
                    project.truth,
                    st.session_state.llm_service
                )
                st.session_state.editing_agent = EditingAgent(
                    project.truth,
                    st.session_state.llm_service
                )
                st.session_state.current_page = 'editor'
                st.rerun()
              except Exception as e:
                st.error(f"❌ Failed to open project: {str(e)}")
          
          with col_b:
            # Use a confirmation dialog for delete
            delete_key = f"confirm_delete_{project.id}"
            if delete_key not in st.session_state:
              st.session_state[delete_key] = False
            
            if not st.session_state[delete_key]:
              if st.button(f"Delete", key=f"delete_{project.id}"):
                st.session_state[delete_key] = True
                st.rerun()
            else:
              st.warning(f"⚠️ Delete '{project.title}'?")
              col_yes, col_no = st.columns(2)
              with col_yes:
                if st.button("✓ Yes", key=f"yes_{project.id}"):
                  try:
                    if project_manager.delete_project(project.id):
                      st.toast("✅ Project deleted successfully!", icon="✅")
                      st.session_state[delete_key] = False
                      st.rerun()
                    else:
                      st.error("❌ Project not found")
                  except Exception as e:
                    st.error(f"❌ Failed to delete project: {str(e)}")
              with col_no:
                if st.button("✗ No", key=f"no_{project.id}"):
                  st.session_state[delete_key] = False
                  st.rerun()
    else:
      st.info("No projects yet. Create your first project!")
  
  with col2:
    st.header("Create New Project")
    
    # Project form with audio support
    title = universal_text_input(
        "Project Title*",
        "project_title",
        st.session_state.audio_service,
        input_type="text_input",
        help_text="Enter your project title",
        audio_prompt="Transcribe the project title."
    )
    
    description = universal_text_input(
        "Description",
        "project_description",
        st.session_state.audio_service,
        input_type="text_area",
        height=100,
        help_text="Describe your novel project",
        audio_prompt="Transcribe the project description."
    )
    
    author = universal_text_input(
        "Author Name",
        "project_author",
        st.session_state.audio_service,
        input_type="text_input",
        help_text="Your name",
        audio_prompt="Transcribe the author name."
    )
    
    genre = universal_text_input(
        "Genre",
        "project_genre",
        st.session_state.audio_service,
        input_type="text_input",
        help_text="e.g., Fantasy, Sci-Fi, Romance",
        audio_prompt="Transcribe the genre."
    )
    
    if st.button("Create Project", type="primary"):
      if title:
        project = project_manager.create_project(
            title=title,
            description=description,
            author=author,
            genre=genre
        )
        st.session_state.current_project = project
        st.session_state.worldbuilding_agent = WorldBuildingAgent(
            project.truth,
            st.session_state.llm_service
        )
        st.session_state.current_page = 'worldbuilding'
        # Clear transcript session state
        for key in ['transcript_project_title', 'transcript_project_description', 
                    'transcript_project_author', 'transcript_project_genre']:
          if key in st.session_state:
            del st.session_state[key]
        st.success(f"Project '{title}' created!")
        st.rerun()
      else:
        st.error("Please provide a project title.")
  
  # Example projects section
  st.header("Example Projects")
  example_projects = project_manager.get_example_projects()
  if example_projects:
    for project in example_projects:
      with st.expander(f"📘 {project.title} (Example)"):
        st.write(f"**Description:** {project.description}")
        if st.button(f"Open Example", key=f"open_ex_{project.id}"):
          st.session_state.current_project = project
          project_manager.current_project = project
          st.session_state.worldbuilding_agent = WorldBuildingAgent(
              project.truth,
              st.session_state.llm_service
          )
          st.session_state.editing_agent = EditingAgent(
              project.truth,
              st.session_state.llm_service
          )
          st.session_state.current_page = 'editor'
          st.rerun()
  else:
    st.info("No example projects available.")


def show_worldbuilding():
  """Display the world-building Q&A page."""
  st.title("🌍 World Building - Interactive Q&A")
  
  project = st.session_state.current_project
  agent = st.session_state.worldbuilding_agent
  audio_service = st.session_state.audio_service
  
  if not project or not agent:
    st.error("No active project. Please return to project manager.")
    return
  
  st.write(f"**Project:** {project.title}")
  
  # Show audio availability status
  if audio_service.is_available():
    st.success("🎤 Audio input available - Click the 🎤 Audio button next to any text field")
  else:
    st.info("💡 Set GOOGLE_API_KEY in .env to enable audio input everywhere")
  
  # Check if coming from editor (has chapters)
  coming_from_editor = len(project.chapters) > 0
  
  # Initialize question tree if not exists
  if not agent.truth.question_tree:
    st.subheader("Let's start building your story!")
    
    initial_question = "What is your story about?"
    
    # Use universal text input with audio support
    initial_answer = universal_text_input(
        initial_question,
        "initial_story_answer",
        audio_service,
        input_type="text_area",
        height=150,
        help_text="Describe your story idea in a few sentences. You can type or use audio.",
        audio_prompt="Generate a detailed transcript of this story description."
    )
    
    if st.button("Start World Building", type="primary"):
      if initial_answer:
        progress_bar = st.progress(0, text="Initializing world-building...")
        try:
          progress_bar.progress(20, text="Analyzing your story...")
          agent.initialize_question_tree(initial_answer)
          
          progress_bar.progress(60, text="Generating follow-up questions...")
          agent.generate_follow_up_questions(
              initial_answer,
              agent.truth.question_tree.root_id
          )
          
          progress_bar.progress(90, text="Saving project...")
          project_manager.save_current_project()
          
          progress_bar.progress(100, text="Complete!")
          
          # Clear transcript
          if 'transcript_initial_story_answer' in st.session_state:
            del st.session_state['transcript_initial_story_answer']
          st.toast("✅ Question tree initialized!", icon="✅")
          st.rerun()
        except Exception as e:
          progress_bar.empty()
          error_msg = st.session_state.llm_service.get_error_message(e)
          st.error(f"❌ Failed to initialize world-building: {error_msg}")
          if st.button("🔄 Retry Initialization", key="retry_init"):
            st.rerun()
      else:
        st.error("Please provide an answer to get started.")
  else:
    # Show question tree visualization
    if coming_from_editor:
      st.subheader("Continue building your story's Truth")
      st.info("💡 Answer more questions to expand your world and deepen your story's foundation")
    else:
      st.subheader("Question Tree Navigation")
    
    # Display current questions
    pending_questions = agent.truth.question_tree.get_pending_questions()
    answered_questions = agent.truth.question_tree.get_answered_questions()
    
    # Visual tree representation
    st.markdown("### 📊 Question Tree Structure")
    
    # View mode selector
    view_options = ["Mind Map", "Tree View", "List by Category", "Timeline"]
    if not AGRAPH_AVAILABLE:
      view_options.remove("Mind Map")
      st.info("💡 Install streamlit-agraph for interactive mind map: `pip install streamlit-agraph`")
    
    view_mode = st.radio(
        "View Mode:",
        view_options,
        horizontal=True,
        key="tree_view_mode"
    )
    
    if view_mode == "Mind Map":
      # Interactive mind map visualization
      st.markdown("#### 🧠 Interactive Mind Map")
      st.markdown(get_mindmap_legend(), unsafe_allow_html=True)
      
      # Render the mind map
      selected_node_id = render_mindmap(agent.truth.question_tree)
      
      # If a node was clicked, navigate to it
      if selected_node_id:
        selected_node = agent.truth.question_tree.get_node(selected_node_id)
        if selected_node and selected_node.status.value == 'pending':
          st.session_state.selected_question_id = selected_node_id
          st.info(f"Selected: {selected_node.question}")
          if st.button("Answer This Question", key="mindmap_answer"):
            st.rerun()
    
    elif view_mode == "List by Category":
      # Group questions by entity type
      st.markdown("#### Questions by Category")
      
      categories = {
          'character': {'icon': '👤', 'name': 'Characters', 'questions': []},
          'plot_event': {'icon': '📖', 'name': 'Plot Events', 'questions': []},
          'setting': {'icon': '🗺️', 'name': 'Settings & World', 'questions': []}
      }
      
      # Categorize all questions
      for node in agent.truth.question_tree.nodes.values():
        entity_type = node.entity_type.value
        if entity_type in categories:
          categories[entity_type]['questions'].append(node)
      
      # Display by category
      for cat_key, cat_data in categories.items():
        if cat_data['questions']:
          with st.expander(f"{cat_data['icon']} {cat_data['name']} ({len(cat_data['questions'])} questions)", expanded=True):
            for node in cat_data['questions']:
              status_icon = "✅" if node.status.value == 'answered' else "⏳"
              col_q1, col_q2 = st.columns([4, 1])
              with col_q1:
                st.write(f"{status_icon} {node.question}")
                if node.answer:
                  st.caption(f"Answer: {node.answer[:100]}...")
              with col_q2:
                if node.status.value == 'pending':
                  if st.button("Answer", key=f"cat_ans_{node.id}"):
                    st.session_state.selected_question_id = node.id
                    st.rerun()
    
    elif view_mode == "Timeline":
      # Show questions in order they were created/answered
      st.markdown("#### Question Timeline")
      
      all_nodes = list(agent.truth.question_tree.nodes.values())
      # Sort by creation (using ID as proxy for creation order)
      all_nodes.sort(key=lambda n: n.id)
      
      for i, node in enumerate(all_nodes):
        status_icon = "✅" if node.status.value == 'answered' else "⏳"
        entity_icons = {'character': '👤', 'plot_event': '📖', 'setting': '🗺️'}
        entity_icon = entity_icons.get(node.entity_type.value, '❓')
        
        col_t1, col_t2, col_t3 = st.columns([1, 5, 1])
        with col_t1:
          st.write(f"**{i+1}**")
        with col_t2:
          st.write(f"{status_icon} {entity_icon} {node.question}")
          if node.answer:
            with st.expander("View Answer"):
              st.write(node.answer)
        with col_t3:
          if node.status.value == 'pending':
            if st.button("→", key=f"time_ans_{node.id}", help="Answer this"):
              st.session_state.selected_question_id = node.id
              st.rerun()
        
        if i < len(all_nodes) - 1:
          st.markdown("↓")
    
    else:  # Tree View
      # Create expandable tree view
      def render_tree_node(node_id: str, level: int = 0):
        """Recursively render tree nodes."""
        node = agent.truth.question_tree.get_node(node_id)
        if not node:
          return
        
        # Determine status icon
        if node.status.value == 'answered':
          status_icon = "✅"
        elif node.status.value == 'pending':
          status_icon = "⏳"
        else:
          status_icon = "❓"
        
        # Determine entity icon
        entity_icons = {
            'character': '👤',
            'plot_event': '📖',
            'setting': '🗺️'
        }
        entity_icon = entity_icons.get(node.entity_type.value, '❓')
        
        # Create indentation
        indent = "　" * level  # Using full-width space for better indentation
        
        # Create expander for this node
        with st.expander(f"{indent}{status_icon} {entity_icon} {node.question}", expanded=(level == 0)):
          if node.answer:
            st.write(f"**Answer:** {node.answer}")
          else:
            st.write("*Not yet answered*")
          
          # Show entity type and status
          st.caption(f"Type: {node.entity_type.value} | Status: {node.status.value}")
          
          # Button to jump to this question
          if node.status.value == 'pending':
            if st.button(f"Answer This Question", key=f"jump_{node.id}"):
              st.session_state.selected_question_id = node.id
              st.rerun()
          
          # Render children
          if node.children_ids:
            st.markdown(f"**Follow-up questions ({len(node.children_ids)}):**")
            for child_id in node.children_ids:
              render_tree_node(child_id, level + 1)
    
      # Render the tree starting from root
      if agent.truth.question_tree.root_id:
        render_tree_node(agent.truth.question_tree.root_id)
    
    st.divider()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
      st.write(f"**Answered:** {len(answered_questions)} | "
               f"**Pending:** {len(pending_questions)}")
      
      if pending_questions:
        st.subheader("Answer Questions")
        
        # Select a question to answer
        question_options = {
            q.id: f"{q.question} ({q.entity_type.value})"
            for q in pending_questions
        }
        
        # Use selected question from tree if available
        default_index = 0
        if 'selected_question_id' in st.session_state and st.session_state.selected_question_id in question_options:
          default_index = list(question_options.keys()).index(st.session_state.selected_question_id)
        
        selected_q_id = st.selectbox(
            "Select a question to answer:",
            options=list(question_options.keys()),
            format_func=lambda x: question_options[x],
            index=default_index,
            key="question_selector"
        )
        
        # Clear the selected question after using it
        if 'selected_question_id' in st.session_state:
          del st.session_state.selected_question_id
        
        if selected_q_id:
          selected_node = agent.truth.question_tree.get_node(selected_q_id)
          
          # Show breadcrumb navigation (path from root to current question)
          def get_path_to_node(node_id: str) -> list[QuestionNode]:
            """Get the path from root to a specific node."""
            path = []
            current = agent.truth.question_tree.get_node(node_id)
            while current:
              path.insert(0, current)
              if current.parent_id:
                current = agent.truth.question_tree.get_node(current.parent_id)
              else:
                break
            return path
          
          path = get_path_to_node(selected_q_id)
          if len(path) > 1:
            st.markdown("**Question Path:**")
            breadcrumb = " → ".join([f"{node.entity_type.value[:4].upper()}" for node in path[:-1]])
            st.caption(f"{breadcrumb} → **Current**")
          
          # Use universal text input with audio support
          answer = universal_text_input(
              selected_node.question,
              f"answer_{selected_q_id}",
              audio_service,
              input_type="text_area",
              height=150,
              help_text="Type your answer or use audio to dictate",
              audio_prompt=f"Generate a detailed transcript answering: {selected_node.question}"
          )
          
          if st.button("Submit Answer", key=f"submit_{selected_q_id}", type="primary"):
            if answer:
              progress_bar = st.progress(0, text="Processing your answer...")
              try:
                progress_bar.progress(30, text="Extracting entities from your answer...")
                new_questions = agent.answer_question(selected_q_id, answer)
                
                progress_bar.progress(80, text="Saving project...")
                project_manager.save_current_project()
                
                progress_bar.progress(100, text="Complete!")
                
                st.toast(
                    f"✅ Answer recorded! Generated {len(new_questions)} follow-up questions.",
                    icon="✅"
                )
                st.rerun()
              except Exception as e:
                progress_bar.empty()
                error_msg = st.session_state.llm_service.get_error_message(e)
                st.error(f"❌ Failed to process answer: {error_msg}")
                if st.button("🔄 Retry Submit", key=f"retry_submit_{selected_q_id}"):
                  st.rerun()
            else:
              st.error("Please provide an answer.")
      else:
        st.success("All questions answered!")
    
    with col2:
      st.subheader("Progress")
      total = len(agent.truth.question_tree.nodes)
      answered = len(answered_questions)
      progress = answered / total if total > 0 else 0
      st.progress(progress)
      st.write(f"{answered}/{total} questions answered")
      
      # Change button text based on whether coming from editor
      button_text = "🚀 Return to Editor" if coming_from_editor else "🚀 Start Writing"
      if st.button(button_text, type="primary"):
        # Save project before returning
        try:
          project_manager.save_current_project()
        except Exception as e:
          st.error(f"Failed to save project: {str(e)}")
        
        st.session_state.current_page = 'editor'
        # Ensure editing agent is initialized
        if not st.session_state.editing_agent:
          st.session_state.editing_agent = EditingAgent(
              project.truth,
              st.session_state.llm_service
          )
        st.rerun()


def show_editor():
  """Display the text editor page."""
  st.title("✍️ Novel Editor")
  
  project = st.session_state.current_project
  
  if not project:
    st.error("No active project. Please return to project manager.")
    return
  
  # Sidebar for navigation
  with st.sidebar:
    st.header(f"📖 {project.title}")
    
    # Auto-save indicator
    if st.session_state.last_save_time:
      import datetime
      time_diff = datetime.datetime.now() - st.session_state.last_save_time
      if time_diff.total_seconds() < 5:
        st.success("💾 Auto-saved just now")
      elif time_diff.total_seconds() < 60:
        st.info(f"💾 Last saved {int(time_diff.total_seconds())}s ago")
      else:
        minutes = int(time_diff.total_seconds() / 60)
        st.info(f"💾 Last saved {minutes}m ago")
    
    if st.button("← Back to Projects"):
      st.session_state.current_page = 'project_manager'
      st.rerun()
    
    st.divider()
    
    # Chapter management
    st.subheader("Chapters")
    chapters = project.get_sorted_chapters()
    
    if chapters:
      for chapter in chapters:
        if st.button(
            f"Ch {chapter.number}: {chapter.title}",
            key=f"ch_{chapter.id}"
        ):
          st.session_state.current_chapter_id = chapter.id
          st.rerun()
    
    st.divider()
    
    # Add new chapter
    st.subheader("Add Chapter")
    new_ch_num = len(chapters) + 1
    new_ch_title = universal_text_input(
        f"Chapter {new_ch_num} Title",
        "new_chapter_title",
        st.session_state.audio_service,
        input_type="text_input",
        help_text="Enter chapter title",
        audio_prompt="Transcribe the chapter title."
    )
    if st.button("Add Chapter", key="add_chapter_btn"):
      if new_ch_title:
        chapter = project_manager.add_chapter(new_ch_num, new_ch_title)
        st.session_state.current_chapter_id = chapter.id
        # Clear transcript
        if 'transcript_new_chapter_title' in st.session_state:
          del st.session_state['transcript_new_chapter_title']
        st.success(f"Chapter {new_ch_num} added!")
        st.rerun()
    
    st.divider()
    
    # World-building navigation
    if st.button("🌍 Continue World-Building", help="Answer more questions to expand your Truth"):
      # Save current project before navigation
      try:
        project_manager.save_current_project()
      except Exception as e:
        st.error(f"Failed to save project: {str(e)}")
      st.session_state.current_page = 'worldbuilding'
      st.rerun()
    
    st.divider()
    
    # Truth viewers
    st.subheader("Truth Viewers")
    if st.button("👥 View Characters"):
      st.session_state.show_truth_viewer = 'characters'
    if st.button("📅 View Timeline"):
      st.session_state.show_truth_viewer = 'timeline'
    if st.button("🗺️ View Settings"):
      st.session_state.show_truth_viewer = 'settings'
    if st.button("🔍 Search Truth"):
      st.session_state.show_truth_viewer = 'search'
    
    st.divider()
    
    # Create Truth Entity section
    st.subheader("Create Truth Entity")
    if st.button("➕ New Character"):
      st.session_state.show_truth_editor = 'character'
      st.session_state.editor_entity_id = None
      st.rerun()
    if st.button("➕ New Event"):
      st.session_state.show_truth_editor = 'event'
      st.session_state.editor_entity_id = None
      st.rerun()
    if st.button("➕ New Setting"):
      st.session_state.show_truth_editor = 'setting'
      st.session_state.editor_entity_id = None
      st.rerun()
  
  # Main editor area
  if st.session_state.current_chapter_id:
    chapter = project.chapters.get(st.session_state.current_chapter_id)
    if chapter:
      st.subheader(f"Chapter {chapter.number}: {chapter.title}")
      
      # Editor with audio support
      content = universal_text_input(
          "Chapter Content",
          f"chapter_content_{chapter.id}",
          st.session_state.audio_service,
          input_type="text_area",
          height=400,
          help_text="Write your chapter here or use audio to dictate",
          audio_prompt="Transcribe the chapter content in detail.",
          default_value=chapter.content
      )
      
      col_save1, col_save2 = st.columns([3, 1])
      with col_save1:
        if st.button("💾 Save Chapter", use_container_width=True):
          try:
            project_manager.update_chapter_content(chapter.id, content)
            import datetime
            st.session_state.last_save_time = datetime.datetime.now()
            st.toast("✅ Chapter saved successfully!", icon="✅")
          except Exception as e:
            st.error(f"❌ Failed to save chapter: {str(e)}")
            st.info("💡 Your changes are still in memory. Try saving again or check the logs.")
      
      with col_save2:
        # Auto-save toggle
        auto_save = st.checkbox("Auto-save", value=st.session_state.auto_save_enabled, key="auto_save_toggle")
        st.session_state.auto_save_enabled = auto_save
      
      # AI editing tools
      st.subheader("AI Editing Tools")
      
      # Check if AI is available
      if not st.session_state.llm_service.is_available():
        st.warning("⚠️ AI features require GOOGLE_API_KEY. Set it in .env file.")
      
      # Text selection for editing with audio support
      selected_text = universal_text_input(
          "Select text to edit (or leave empty to edit entire chapter)",
          "text_to_edit",
          st.session_state.audio_service,
          input_type="text_area",
          height=100,
          help_text="Paste or dictate the text you want to edit",
          audio_prompt="Transcribe the text to be edited.",
          default_value=st.session_state.selected_text
      )
      
      col1, col2, col3, col4 = st.columns(4)
      
      with col1:
        if st.button("✨ Improve", disabled=not st.session_state.llm_service.is_available()):
          with st.spinner("Improving text... (this may take a moment)"):
            try:
              text_to_improve = selected_text if selected_text else content
              all_chapters = project.get_sorted_chapters()
              result = st.session_state.editing_agent.improve_text(
                  text_to_improve,
                  chapter,
                  all_chapters
              )
              st.session_state.ai_result = result
              st.toast("✅ Text improved successfully!", icon="✅")
              st.rerun()
            except Exception as e:
              error_msg = st.session_state.llm_service.get_error_message(e)
              st.error(f"❌ {error_msg}")
              if st.button("🔄 Retry Improve", key="retry_improve"):
                st.rerun()
      
      with col2:
        if st.button("📝 Expand", disabled=not st.session_state.llm_service.is_available()):
          with st.spinner("Expanding text... (this may take a moment)"):
            try:
              text_to_expand = selected_text if selected_text else content
              all_chapters = project.get_sorted_chapters()
              result = st.session_state.editing_agent.expand_text(
                  text_to_expand,
                  chapter,
                  all_chapters
              )
              st.session_state.ai_result = result
              st.toast("✅ Text expanded successfully!", icon="✅")
              st.rerun()
            except Exception as e:
              error_msg = st.session_state.llm_service.get_error_message(e)
              st.error(f"❌ {error_msg}")
              if st.button("🔄 Retry Expand", key="retry_expand"):
                st.rerun()
      
      with col3:
        if st.button("🔄 Rephrase", disabled=not st.session_state.llm_service.is_available()):
          with st.spinner("Rephrasing text... (this may take a moment)"):
            try:
              text_to_rephrase = selected_text if selected_text else content
              all_chapters = project.get_sorted_chapters()
              result = st.session_state.editing_agent.rephrase_text(
                  text_to_rephrase,
                  chapter,
                  all_chapters
              )
              st.session_state.ai_result = result
              st.toast("✅ Text rephrased successfully!", icon="✅")
              st.rerun()
            except Exception as e:
              error_msg = st.session_state.llm_service.get_error_message(e)
              st.error(f"❌ {error_msg}")
              if st.button("🔄 Retry Rephrase", key="retry_rephrase"):
                st.rerun()
      
      with col4:
        if st.button("💡 Suggest Next", disabled=not st.session_state.llm_service.is_available()):
          with st.spinner("Generating suggestion... (this may take a moment)"):
            try:
              all_chapters = project.get_sorted_chapters()
              result = st.session_state.editing_agent.suggest_next_chapter(
                  all_chapters
              )
              st.session_state.ai_result = result
              st.toast("✅ Suggestion generated successfully!", icon="✅")
              st.rerun()
            except Exception as e:
              error_msg = st.session_state.llm_service.get_error_message(e)
              st.error(f"❌ {error_msg}")
              if st.button("🔄 Retry Suggest", key="retry_suggest"):
                st.rerun()
      
      # Display AI result
      if st.session_state.ai_result:
        st.subheader("AI Result")
        st.write(st.session_state.ai_result)
        
        col_a, col_b = st.columns(2)
        with col_a:
          if st.button("✅ Use This"):
            try:
              if selected_text and selected_text in content:
                # Replace selected text
                new_content = content.replace(selected_text, st.session_state.ai_result)
                project_manager.update_chapter_content(chapter.id, new_content)
              else:
                # Append to chapter
                new_content = content + "\n\n" + st.session_state.ai_result
                project_manager.update_chapter_content(chapter.id, new_content)
              
              import datetime
              st.session_state.last_save_time = datetime.datetime.now()
              st.session_state.ai_result = None
              st.session_state.selected_text = ""
              st.toast("✅ Applied AI suggestion!", icon="✅")
              st.rerun()
            except Exception as e:
              st.error(f"❌ Failed to apply suggestion: {str(e)}")
        
        with col_b:
          if st.button("❌ Discard"):
            st.session_state.ai_result = None
            st.toast("Suggestion discarded", icon="ℹ️")
            st.rerun()
  else:
    st.info("Select or create a chapter to start writing.")
  
  # Truth viewer modal
  if 'show_truth_viewer' in st.session_state:
    viewer_type = st.session_state.show_truth_viewer
    
    st.divider()
    
    # Close button
    if st.button("✖ Close Viewer"):
      del st.session_state.show_truth_viewer
      if 'selected_entity_id' in st.session_state:
        del st.session_state.selected_entity_id
      st.rerun()
    
    if viewer_type == 'characters':
      render_character_viewer(project)
    
    elif viewer_type == 'timeline':
      render_timeline_viewer(project)
    
    elif viewer_type == 'settings':
      render_settings_viewer(project)
    
    elif viewer_type == 'search':
      render_global_search(project)
  
  # Truth editor modal
  if 'show_truth_editor' in st.session_state:
    editor_type = st.session_state.show_truth_editor
    entity_id = st.session_state.get('editor_entity_id')
    
    st.divider()
    
    # Close button
    if st.button("✖ Close Editor"):
      del st.session_state.show_truth_editor
      if 'editor_entity_id' in st.session_state:
        del st.session_state.editor_entity_id
      st.rerun()
    
    # Define save and delete callbacks
    def save_character(character):
      if entity_id:
        project.truth.update_character(entity_id, character)
      else:
        project.truth.add_character(character)
      project_manager.save_current_project()
      del st.session_state.show_truth_editor
      if 'editor_entity_id' in st.session_state:
        del st.session_state.editor_entity_id
    
    def delete_character(char_id):
      project.truth.delete_character(char_id)
      project_manager.save_current_project()
      del st.session_state.show_truth_editor
      if 'editor_entity_id' in st.session_state:
        del st.session_state.editor_entity_id
    
    def save_plot_event(event):
      if entity_id:
        project.truth.update_plot_event(entity_id, event)
      else:
        project.truth.add_plot_event(event)
      project_manager.save_current_project()
      del st.session_state.show_truth_editor
      if 'editor_entity_id' in st.session_state:
        del st.session_state.editor_entity_id
    
    def delete_plot_event(event_id):
      project.truth.delete_plot_event(event_id)
      project_manager.save_current_project()
      del st.session_state.show_truth_editor
      if 'editor_entity_id' in st.session_state:
        del st.session_state.editor_entity_id
    
    def save_setting(setting):
      if entity_id:
        project.truth.update_setting(entity_id, setting)
      else:
        project.truth.add_setting(setting)
      project_manager.save_current_project()
      del st.session_state.show_truth_editor
      if 'editor_entity_id' in st.session_state:
        del st.session_state.editor_entity_id
    
    def delete_setting(setting_id):
      project.truth.delete_setting(setting_id)
      project_manager.save_current_project()
      del st.session_state.show_truth_editor
      if 'editor_entity_id' in st.session_state:
        del st.session_state.editor_entity_id
    
    # Render appropriate editor
    if editor_type == 'character':
      render_character_editor(
          character_id=entity_id,
          characters=project.truth.characters,
          audio_service=st.session_state.audio_service,
          on_save=save_character,
          on_delete=delete_character if entity_id else None
      )
    
    elif editor_type == 'event':
      render_plot_event_editor(
          event_id=entity_id,
          plot_events=project.truth.plot_events,
          characters=project.truth.characters,
          audio_service=st.session_state.audio_service,
          on_save=save_plot_event,
          on_delete=delete_plot_event if entity_id else None
      )
    
    elif editor_type == 'setting':
      render_setting_editor(
          setting_id=entity_id,
          settings=project.truth.settings,
          characters=project.truth.characters,
          plot_events=project.truth.plot_events,
          audio_service=st.session_state.audio_service,
          on_save=save_setting,
          on_delete=delete_setting if entity_id else None
      )


# Main app routing
def main():
  """Main application entry point."""
  
  # Check for API key
  if not os.getenv('GOOGLE_API_KEY'):
    st.error(
        "⚠️ GOOGLE_API_KEY not found! Please set it in your .env file."
    )
    st.info(
        "Copy .env.example to .env and add your Google AI API key."
    )
    return
  
  # Route to appropriate page
  if st.session_state.current_page == 'project_manager':
    show_project_manager()
  elif st.session_state.current_page == 'worldbuilding':
    show_worldbuilding()
  elif st.session_state.current_page == 'editor':
    show_editor()


if __name__ == "__main__":
  main()
