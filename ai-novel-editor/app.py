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
          
          with col_b:
            if st.button(f"Delete", key=f"delete_{project.id}"):
              project_manager.delete_project(project.id)
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
  
  # Initialize question tree if not exists
  if not agent.question_tree:
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
        agent.initialize_question_tree(initial_answer)
        agent.generate_follow_up_questions(
            initial_answer,
            agent.question_tree.root_id
        )
        project_manager.save_current_project()
        # Clear transcript
        if 'transcript_initial_story_answer' in st.session_state:
          del st.session_state['transcript_initial_story_answer']
        st.success("Question tree initialized!")
        st.rerun()
      else:
        st.error("Please provide an answer to get started.")
  else:
    # Show question tree visualization
    st.subheader("Question Tree Navigation")
    
    # Display current questions
    pending_questions = agent.question_tree.get_pending_questions()
    answered_questions = agent.question_tree.get_answered_questions()
    
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
      selected_node_id = render_mindmap(agent.question_tree)
      
      # If a node was clicked, navigate to it
      if selected_node_id:
        selected_node = agent.question_tree.get_node(selected_node_id)
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
      for node in agent.question_tree.nodes.values():
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
      
      all_nodes = list(agent.question_tree.nodes.values())
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
        node = agent.question_tree.get_node(node_id)
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
      if agent.question_tree.root_id:
        render_tree_node(agent.question_tree.root_id)
    
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
          selected_node = agent.question_tree.get_node(selected_q_id)
          
          # Show breadcrumb navigation (path from root to current question)
          def get_path_to_node(node_id: str) -> list[QuestionNode]:
            """Get the path from root to a specific node."""
            path = []
            current = agent.question_tree.get_node(node_id)
            while current:
              path.insert(0, current)
              if current.parent_id:
                current = agent.question_tree.get_node(current.parent_id)
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
              new_questions = agent.answer_question(selected_q_id, answer)
              project_manager.save_current_project()
              
              st.success(
                  f"✅ Answer recorded! Generated {len(new_questions)} "
                  "follow-up questions."
              )
              st.rerun()
            else:
              st.error("Please provide an answer.")
      else:
        st.success("All questions answered!")
    
    with col2:
      st.subheader("Progress")
      total = len(agent.question_tree.nodes)
      answered = len(answered_questions)
      progress = answered / total if total > 0 else 0
      st.progress(progress)
      st.write(f"{answered}/{total} questions answered")
      
      if st.button("🚀 Start Writing", type="primary"):
        st.session_state.current_page = 'editor'
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
    
    # Truth viewers
    if st.button("👥 View Characters"):
      st.session_state.show_truth_viewer = 'characters'
    if st.button("📅 View Timeline"):
      st.session_state.show_truth_viewer = 'timeline'
    if st.button("🗺️ View Settings"):
      st.session_state.show_truth_viewer = 'settings'
  
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
      
      if st.button("💾 Save Chapter"):
        project_manager.update_chapter_content(chapter.id, content)
        st.success("Chapter saved!")
      
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
          with st.spinner("Improving text..."):
            text_to_improve = selected_text if selected_text else content
            all_chapters = project.get_sorted_chapters()
            result = st.session_state.editing_agent.improve_text(
                text_to_improve,
                chapter,
                all_chapters
            )
            st.session_state.ai_result = result
            st.rerun()
      
      with col2:
        if st.button("📝 Expand", disabled=not st.session_state.llm_service.is_available()):
          with st.spinner("Expanding text..."):
            text_to_expand = selected_text if selected_text else content
            all_chapters = project.get_sorted_chapters()
            result = st.session_state.editing_agent.expand_text(
                text_to_expand,
                chapter,
                all_chapters
            )
            st.session_state.ai_result = result
            st.rerun()
      
      with col3:
        if st.button("🔄 Rephrase", disabled=not st.session_state.llm_service.is_available()):
          with st.spinner("Rephrasing text..."):
            text_to_rephrase = selected_text if selected_text else content
            all_chapters = project.get_sorted_chapters()
            result = st.session_state.editing_agent.rephrase_text(
                text_to_rephrase,
                chapter,
                all_chapters
            )
            st.session_state.ai_result = result
            st.rerun()
      
      with col4:
        if st.button("💡 Suggest Next", disabled=not st.session_state.llm_service.is_available()):
          with st.spinner("Generating suggestion..."):
            all_chapters = project.get_sorted_chapters()
            result = st.session_state.editing_agent.suggest_next_chapter(
                all_chapters
            )
            st.session_state.ai_result = result
            st.rerun()
      
      # Display AI result
      if st.session_state.ai_result:
        st.subheader("AI Result")
        st.write(st.session_state.ai_result)
        
        col_a, col_b = st.columns(2)
        with col_a:
          if st.button("✅ Use This"):
            if selected_text and selected_text in content:
              # Replace selected text
              new_content = content.replace(selected_text, st.session_state.ai_result)
              project_manager.update_chapter_content(chapter.id, new_content)
            else:
              # Append to chapter
              new_content = content + "\n\n" + st.session_state.ai_result
              project_manager.update_chapter_content(chapter.id, new_content)
            st.session_state.ai_result = None
            st.session_state.selected_text = ""
            st.success("Applied AI suggestion!")
            st.rerun()
        
        with col_b:
          if st.button("❌ Discard"):
            st.session_state.ai_result = None
            st.rerun()
  else:
    st.info("Select or create a chapter to start writing.")
  
  # Truth viewer modal
  if 'show_truth_viewer' in st.session_state:
    viewer_type = st.session_state.show_truth_viewer
    
    if viewer_type == 'characters':
      st.subheader("👥 Characters")
      for char in project.truth.characters.values():
        with st.expander(f"{char.name}"):
          st.write(f"**Description:** {char.description}")
          if char.traits:
            st.write(f"**Traits:** {', '.join(char.traits)}")
          if char.backstory:
            st.write(f"**Backstory:** {char.backstory}")
    
    elif viewer_type == 'timeline':
      st.subheader("📅 Timeline")
      events = sorted(
          project.truth.plot_events.values(),
          key=lambda e: e.order
      )
      for event in events:
        with st.expander(f"{event.title}"):
          st.write(event.description)
    
    elif viewer_type == 'settings':
      st.subheader("🗺️ Settings & World-Building")
      for setting in project.truth.settings.values():
        with st.expander(f"{setting.name}"):
          st.write(f"**Type:** {setting.type}")
          st.write(f"**Description:** {setting.description}")


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
