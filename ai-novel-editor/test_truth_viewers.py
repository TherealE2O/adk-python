"""Quick test to verify truth viewers work."""

from src.models.truth import TruthKnowledgeBase, Character, PlotEvent, Setting
from src.models.project import Project

# Create a test project with some truth data
truth = TruthKnowledgeBase()

# Add test character
char1 = Character(
    id="char_1",
    name="Alice",
    description="A brave adventurer",
    traits=["brave", "curious"],
    backstory="Grew up in a small village"
)
truth.add_character(char1)

# Add test plot event
event1 = PlotEvent(
    id="event_1",
    title="The Journey Begins",
    description="Alice sets out on her adventure",
    order=1,
    characters_involved=["char_1"],
    significance="Starting point of the story"
)
truth.add_plot_event(event1)

# Add test setting
setting1 = Setting(
    id="setting_1",
    name="The Village",
    type="location",
    description="A peaceful village in the countryside",
    related_characters=["char_1"]
)
truth.add_setting(setting1)

# Create test project
project = Project(
    id="test_project",
    title="Test Novel",
    description="A test novel",
    author="Test Author",
    genre="Fantasy",
    truth=truth
)

print("✓ Test project created successfully")
print(f"  - Characters: {len(project.truth.characters)}")
print(f"  - Plot Events: {len(project.truth.plot_events)}")
print(f"  - Settings: {len(project.truth.settings)}")

# Test that the viewer functions can be imported
try:
    from src.ui.truth_viewers import (
        render_character_viewer,
        render_timeline_viewer,
        render_settings_viewer,
        render_global_search
    )
    print("✓ All truth viewer functions imported successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
