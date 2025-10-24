"""Tests for the EditingAgent."""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from src.agents.editing_agent import EditingAgent
from src.models.truth import TruthKnowledgeBase, Character, PlotEvent, Setting
from src.models.project import Chapter
from src.services.llm_service import LLMService


@pytest.fixture
def mock_llm_service():
    """Create a mock LLM service."""
    service = Mock(spec=LLMService)
    service.is_available.return_value = True
    service.generate_text.return_value = "Generated text"
    return service


@pytest.fixture
def truth_kb():
    """Create a Truth knowledge base with sample data."""
    truth = TruthKnowledgeBase()
    
    # Add a character
    character = Character(
        name="Alice",
        description="A brave adventurer",
        traits=["brave", "curious"],
        role="protagonist"
    )
    truth.add_character(character)
    
    # Add a plot event
    plot_event = PlotEvent(
        title="The Journey Begins",
        description="Alice sets out on her quest",
        order=1,
        significance="Inciting incident"
    )
    truth.add_plot_event(plot_event)
    
    # Add a setting
    setting = Setting(
        name="The Enchanted Forest",
        type="location",
        description="A mysterious forest filled with magic"
    )
    truth.add_setting(setting)
    
    return truth


@pytest.fixture
def sample_chapter():
    """Create a sample chapter."""
    chapter = Chapter(
        number=1,
        title="The Beginning",
        content="Alice walked into the forest. She felt nervous but excited."
    )
    chapter.update_word_count()
    return chapter


@pytest.fixture
def editing_agent(truth_kb, mock_llm_service):
    """Create an EditingAgent with mocked dependencies."""
    return EditingAgent(truth_kb, mock_llm_service)


def test_editing_agent_initialization(truth_kb, mock_llm_service):
    """Test EditingAgent initialization."""
    agent = EditingAgent(truth_kb, mock_llm_service)
    
    assert agent.truth == truth_kb
    assert agent.llm_service == mock_llm_service
    assert agent.is_ready() is True


def test_is_ready_with_unavailable_service(truth_kb):
    """Test is_ready returns False when LLM service is unavailable."""
    mock_service = Mock(spec=LLMService)
    mock_service.is_available.return_value = False
    
    agent = EditingAgent(truth_kb, mock_service)
    assert agent.is_ready() is False


def test_build_context(editing_agent, sample_chapter):
    """Test context building from Truth and chapters."""
    all_chapters = [sample_chapter]
    
    context = editing_agent.build_context(sample_chapter, all_chapters)
    
    # Check structure
    assert "truth" in context
    assert "previous_chapters" in context
    assert "current_chapter" in context
    
    # Check Truth content
    assert len(context["truth"]["characters"]) == 1
    assert context["truth"]["characters"][0]["name"] == "Alice"
    assert len(context["truth"]["plot_events"]) == 1
    assert len(context["truth"]["settings"]) == 1
    
    # Check previous chapters (should be empty for first chapter)
    assert len(context["previous_chapters"]) == 0
    
    # Check current chapter
    assert context["current_chapter"]["number"] == 1
    assert context["current_chapter"]["title"] == "The Beginning"


def test_build_context_with_previous_chapters(editing_agent):
    """Test context building with multiple chapters."""
    chapter1 = Chapter(number=1, title="Chapter 1", content="First chapter content")
    chapter2 = Chapter(number=2, title="Chapter 2", content="Second chapter content")
    chapter3 = Chapter(number=3, title="Chapter 3", content="Third chapter content")
    
    all_chapters = [chapter1, chapter2, chapter3]
    
    context = editing_agent.build_context(chapter3, all_chapters)
    
    # Should have 2 previous chapters
    assert len(context["previous_chapters"]) == 2
    assert context["previous_chapters"][0]["number"] == 1
    assert context["previous_chapters"][1]["number"] == 2
    
    # Current chapter should be chapter 3
    assert context["current_chapter"]["number"] == 3


def test_create_chapter_summary(editing_agent, sample_chapter):
    """Test chapter summary creation."""
    summary = editing_agent._create_chapter_summary(sample_chapter)
    
    assert isinstance(summary, str)
    assert len(summary) <= 503  # 500 chars + "..."
    assert "Alice walked into the forest" in summary


def test_create_chapter_summary_empty_chapter(editing_agent):
    """Test summary creation for empty chapter."""
    empty_chapter = Chapter(number=1, title="Empty", content="")
    
    summary = editing_agent._create_chapter_summary(empty_chapter)
    
    assert summary == "[Empty chapter]"


def test_improve_text(editing_agent, sample_chapter, mock_llm_service):
    """Test text improvement."""
    text = "She walked slowly."
    mock_llm_service.generate_text.return_value = "She walked with deliberate, measured steps."
    
    result = editing_agent.improve_text(text, sample_chapter, [sample_chapter])
    
    assert result == "She walked with deliberate, measured steps."
    mock_llm_service.generate_text.assert_called_once()


def test_expand_text(editing_agent, sample_chapter, mock_llm_service):
    """Test text expansion."""
    text = "The forest was dark."
    mock_llm_service.generate_text.return_value = (
        "The forest was dark, with towering trees blocking out the sunlight. "
        "Shadows danced between the trunks, and the air felt thick with mystery."
    )
    
    result = editing_agent.expand_text(text, sample_chapter, [sample_chapter])
    
    assert "towering trees" in result
    assert "shadows" in result.lower()
    mock_llm_service.generate_text.assert_called_once()


def test_rephrase_text(editing_agent, sample_chapter, mock_llm_service):
    """Test text rephrasing."""
    text = "Alice was scared."
    mock_llm_service.generate_text.return_value = "Fear gripped Alice's heart."
    
    result = editing_agent.rephrase_text(text, sample_chapter, [sample_chapter])
    
    assert result == "Fear gripped Alice's heart."
    mock_llm_service.generate_text.assert_called_once()


def test_suggest_completion(editing_agent, sample_chapter, mock_llm_service):
    """Test completion suggestion."""
    text = "Alice reached for the door handle and"
    mock_llm_service.generate_text.return_value = "hesitated, sensing something was wrong."
    
    result = editing_agent.suggest_completion(text, sample_chapter, [sample_chapter])
    
    assert result == "hesitated, sensing something was wrong."
    mock_llm_service.generate_text.assert_called_once()


def test_generate_paragraph(editing_agent, sample_chapter, mock_llm_service):
    """Test paragraph generation from instruction."""
    instruction = "Write about Alice discovering a magical artifact"
    mock_llm_service.generate_text.return_value = (
        "Alice's fingers brushed against something smooth and cold. "
        "She pulled it from the moss-covered ground—a crystal amulet "
        "that glowed with an inner light."
    )
    
    result = editing_agent.generate_paragraph(instruction, sample_chapter, [sample_chapter])
    
    assert "crystal amulet" in result
    mock_llm_service.generate_text.assert_called_once()


def test_suggest_next_chapter(editing_agent, sample_chapter, mock_llm_service):
    """Test next chapter suggestion."""
    mock_llm_service.generate_text.return_value = (
        "In the next chapter, Alice should encounter the first challenge "
        "in the Enchanted Forest, testing her bravery and revealing more "
        "about the forest's magical nature."
    )
    
    result = editing_agent.suggest_next_chapter([sample_chapter])
    
    assert "next chapter" in result.lower()
    assert "challenge" in result.lower()
    mock_llm_service.generate_text.assert_called_once()


def test_plan_chapter(editing_agent, sample_chapter, mock_llm_service):
    """Test chapter planning."""
    mock_llm_service.generate_text.return_value = (
        "Scene 1: Alice enters the forest\n"
        "Scene 2: She meets a mysterious guide\n"
        "Scene 3: The first obstacle appears"
    )
    
    result = editing_agent.plan_chapter(2, "The Guide", [sample_chapter])
    
    assert "Scene" in result
    assert "forest" in result.lower()
    mock_llm_service.generate_text.assert_called_once()


def test_edit_chapter(editing_agent, sample_chapter, mock_llm_service):
    """Test full chapter editing."""
    mock_llm_service.generate_text.return_value = (
        "Alice stepped into the forest with a mixture of trepidation and excitement. "
        "The towering trees seemed to whisper secrets as she passed."
    )
    
    result = editing_agent.edit_chapter(sample_chapter, [sample_chapter])
    
    assert len(result) > 0
    mock_llm_service.generate_text.assert_called_once()


def test_edit_chapter_empty_content(editing_agent, mock_llm_service):
    """Test editing empty chapter raises error."""
    empty_chapter = Chapter(number=1, title="Empty", content="")
    
    with pytest.raises(ValueError, match="Cannot edit empty chapter"):
        editing_agent.edit_chapter(empty_chapter, [empty_chapter])


def test_operations_fail_when_not_ready(truth_kb, sample_chapter):
    """Test that operations fail when agent is not ready."""
    mock_service = Mock(spec=LLMService)
    mock_service.is_available.return_value = False
    
    agent = EditingAgent(truth_kb, mock_service)
    
    with pytest.raises(ValueError, match="not ready"):
        agent.improve_text("text", sample_chapter, [sample_chapter])
    
    with pytest.raises(ValueError, match="not ready"):
        agent.expand_text("text", sample_chapter, [sample_chapter])
    
    with pytest.raises(ValueError, match="not ready"):
        agent.rephrase_text("text", sample_chapter, [sample_chapter])


def test_create_editing_prompt(editing_agent, sample_chapter):
    """Test editing prompt creation."""
    context = editing_agent.build_context(sample_chapter, [sample_chapter])
    
    prompt = editing_agent.create_editing_prompt("improve", "Test text", context)
    
    assert "Test text" in prompt
    assert "TASK" in prompt
    assert "Alice" in prompt  # Character from Truth
    assert "Enchanted Forest" in prompt  # Setting from Truth


def test_format_truth_context(editing_agent):
    """Test Truth context formatting."""
    truth_dict = {
        "characters": [{"name": "Alice", "description": "A hero", "traits": ["brave"], "role": "protagonist"}],
        "plot_events": [{"title": "Event 1", "description": "Something happens", "significance": "Important"}],
        "settings": [{"name": "Forest", "type": "location", "description": "Dark forest"}]
    }
    
    formatted = editing_agent._format_truth_context(truth_dict)
    
    assert "Alice" in formatted
    assert "Event 1" in formatted
    assert "Forest" in formatted


def test_format_previous_chapters(editing_agent):
    """Test previous chapters formatting."""
    prev_chapters = [
        {"number": 1, "title": "Chapter 1", "summary": "First chapter summary"},
        {"number": 2, "title": "Chapter 2", "summary": "Second chapter summary"}
    ]
    
    formatted = editing_agent._format_previous_chapters(prev_chapters)
    
    assert "Chapter 1" in formatted
    assert "Chapter 2" in formatted
    assert "First chapter summary" in formatted


def test_get_action_instructions(editing_agent):
    """Test action instructions retrieval."""
    improve_instructions = editing_agent._get_action_instructions("improve")
    expand_instructions = editing_agent._get_action_instructions("expand")
    rephrase_instructions = editing_agent._get_action_instructions("rephrase")
    
    assert "improve" in improve_instructions.lower()
    assert "expand" in expand_instructions.lower()
    assert "rephrase" in rephrase_instructions.lower()
