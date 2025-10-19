"""Main Streamlit application for AI Novel Editor."""

from __future__ import annotations

import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

from src.services.storage import StorageService
from src.services.project_manager import ProjectManager
from src.services.llm_service import LLMService
from src.agents.worldbuilding_agent import WorldBuildingAgent
from src.agents.editing_agent import EditingAgent
from src.models.project import Project, Chapter
from src.models.truth import QuestionNode

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
if 'ai_result' not in st.session_state:
  st.session_state.ai_result = None
if 'selected_text' not in st.session_state:
  st.session_state.selected_text = ""


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
    with st.form("new_project_form"):
      title = st.text_input("Project Title*")
      description = st.text_area("Description")
      author = st.text_input("Author Name")
      genre = st.text_input("Genre")
      
      submitted = st.form_submit_button("Create Project")
      if submitted and title:
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
        st.success(f"Project '{title}' created!")
        st.rerun()
      elif submitted:
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
  
  if not project or not agent:
    st.error("No active project. Please return to project manager.")
    return
  
  st.write(f"**Project:** {project.title}")
  
  # Initialize question tree if not exists
  if not agent.question_tree:
    st.subheader("Let's start building your story!")
    initial_answer = st.text_area(
        "What is your story about?",
        height=150,
        help="Describe your story idea in a few sentences."
    )
    
    if st.button("Start World Building"):
      if initial_answer:
        agent.initialize_question_tree(initial_answer)
        agent.generate_follow_up_questions(
            initial_answer,
            agent.question_tree.root_id
        )
        project_manager.save_current_project()
        st.success("Question tree initialized!")
        st.rerun()
      else:
        st.error("Please provide an answer to get started.")
  else:
    # Show question tree visualization
    st.subheader("Question Tree")
    tree_summary = agent.get_question_tree_summary()
    
    # Display current questions
    pending_questions = agent.question_tree.get_pending_questions()
    answered_questions = agent.question_tree.get_answered_questions()
    
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
        
        selected_q_id = st.selectbox(
            "Select a question to answer:",
            options=list(question_options.keys()),
            format_func=lambda x: question_options[x]
        )
        
        if selected_q_id:
          selected_node = agent.question_tree.get_node(selected_q_id)
          
          answer = st.text_area(
              f"Your answer to: {selected_node.question}",
              height=150
          )
          
          if st.button("Submit Answer"):
            if answer:
              new_questions = agent.answer_question(selected_q_id, answer)
              project_manager.save_current_project()
              st.success(
                  f"Answer recorded! Generated {len(new_questions)} "
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
    with st.form("add_chapter"):
      new_ch_num = len(chapters) + 1
      new_ch_title = st.text_input("New Chapter Title")
      if st.form_submit_button("Add Chapter"):
        if new_ch_title:
          chapter = project_manager.add_chapter(new_ch_num, new_ch_title)
          st.session_state.current_chapter_id = chapter.id
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
      
      # Editor
      content = st.text_area(
          "Chapter Content",
          value=chapter.content,
          height=400,
          key="chapter_content"
      )
      
      if st.button("💾 Save Chapter"):
        project_manager.update_chapter_content(chapter.id, content)
        st.success("Chapter saved!")
      
      # AI editing tools
      st.subheader("AI Editing Tools")
      
      # Check if AI is available
      if not st.session_state.llm_service.is_available():
        st.warning("⚠️ AI features require GOOGLE_API_KEY. Set it in .env file.")
      
      # Text selection for editing
      selected_text = st.text_area(
          "Select text to edit (or leave empty to edit entire chapter):",
          value=st.session_state.selected_text,
          height=100,
          key="text_to_edit"
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
