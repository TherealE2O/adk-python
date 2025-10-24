"""UI components for editing and creating Truth entities."""

import streamlit as st
from typing import Optional
from src.models.truth import Character, PlotEvent, Setting
from src.services.audio_service import AudioService


def render_character_editor(
    character_id: Optional[str],
    characters: dict[str, Character],
    audio_service: AudioService,
    on_save: callable,
    on_delete: Optional[callable] = None
) -> None:
    """Render character editor.
    
    Args:
        character_id: ID of character to edit, None for create mode
        characters: Dictionary of all characters for relationship selection
        audio_service: Audio service for voice input
        on_save: Callback function when save is clicked
        on_delete: Optional callback function when delete is clicked
    """
    is_edit_mode = character_id is not None
    character = characters.get(character_id) if is_edit_mode else None
    
    st.subheader("✏️ Edit Character" if is_edit_mode else "➕ Create Character")
    
    # Name field
    name = st.text_input(
        "Name *",
        value=character.name if character else "",
        key=f"char_name_{character_id or 'new'}"
    )
    
    # Description field
    description = st.text_area(
        "Description",
        value=character.description if character else "",
        height=100,
        key=f"char_desc_{character_id or 'new'}"
    )
    
    # Role field
    role = st.text_input(
        "Role",
        value=character.role if character else "",
        key=f"char_role_{character_id or 'new'}"
    )
    
    # Physical description
    physical_description = st.text_area(
        "Physical Description",
        value=character.physical_description if character else "",
        height=100,
        key=f"char_physical_{character_id or 'new'}"
    )
    
    # Backstory
    backstory = st.text_area(
        "Backstory",
        value=character.backstory if character else "",
        height=150,
        key=f"char_backstory_{character_id or 'new'}"
    )
    
    # Traits
    traits_input = st.text_input(
        "Traits (comma-separated)",
        value=", ".join(character.traits) if character else "",
        key=f"char_traits_{character_id or 'new'}"
    )
    
    # Motivations
    motivations_input = st.text_input(
        "Motivations (comma-separated)",
        value=", ".join(character.motivations) if character else "",
        key=f"char_motivations_{character_id or 'new'}"
    )
    
    # Relationships
    st.write("**Relationships**")
    other_characters = {cid: c for cid, c in characters.items() if cid != character_id}
    
    relationships = {}
    if other_characters:
        existing_relationships = character.relationships if character else {}
        
        for other_id, other_char in other_characters.items():
            rel_desc = st.text_input(
                f"Relationship with {other_char.name}",
                value=existing_relationships.get(other_id, ""),
                key=f"char_rel_{character_id or 'new'}_{other_id}"
            )
            if rel_desc:
                relationships[other_id] = rel_desc
    else:
        st.info("No other characters available for relationships")
    
    # Buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("💾 Save", use_container_width=True, key=f"save_char_{character_id or 'new'}"):
            if not name:
                st.error("Name is required")
            else:
                # Parse traits and motivations
                traits = [t.strip() for t in traits_input.split(",") if t.strip()]
                motivations = [m.strip() for m in motivations_input.split(",") if m.strip()]
                
                # Create or update character
                char_data = {
                    "name": name,
                    "description": description,
                    "role": role,
                    "physical_description": physical_description,
                    "backstory": backstory,
                    "traits": traits,
                    "motivations": motivations,
                    "relationships": relationships
                }
                
                if is_edit_mode:
                    char_data["id"] = character_id
                
                on_save(Character(**char_data))
                st.toast(f"✅ Character '{name}' saved successfully!", icon="✅")
                st.rerun()
    
    with col2:
        if is_edit_mode and on_delete:
            if st.button("🗑️ Delete", use_container_width=True, type="secondary", key=f"delete_char_{character_id}"):
                if st.session_state.get(f"confirm_delete_{character_id}"):
                    on_delete(character_id)
                    st.toast(f"✅ Character '{character.name}' deleted", icon="✅")
                    st.rerun()
                else:
                    st.session_state[f"confirm_delete_{character_id}"] = True
                    st.warning("Click delete again to confirm")
                    st.rerun()


def render_plot_event_editor(
    event_id: Optional[str],
    plot_events: dict[str, PlotEvent],
    characters: dict[str, Character],
    audio_service: AudioService,
    on_save: callable,
    on_delete: Optional[callable] = None
) -> None:
    """Render plot event editor.
    
    Args:
        event_id: ID of event to edit, None for create mode
        plot_events: Dictionary of all plot events
        characters: Dictionary of all characters for selection
        audio_service: Audio service for voice input
        on_save: Callback function when save is clicked
        on_delete: Optional callback function when delete is clicked
    """
    is_edit_mode = event_id is not None
    event = plot_events.get(event_id) if is_edit_mode else None
    
    st.subheader("✏️ Edit Event" if is_edit_mode else "➕ Create Event")
    
    # Title field
    title = st.text_input(
        "Title *",
        value=event.title if event else "",
        key=f"event_title_{event_id or 'new'}"
    )
    
    # Description field
    description = st.text_area(
        "Description",
        value=event.description if event else "",
        height=150,
        key=f"event_desc_{event_id or 'new'}"
    )
    
    # Significance field
    significance = st.text_area(
        "Significance",
        value=event.significance if event else "",
        height=100,
        key=f"event_sig_{event_id or 'new'}"
    )
    
    # Order field
    order = st.number_input(
        "Order (chronological position)",
        min_value=0,
        value=event.order if event else 0,
        key=f"event_order_{event_id or 'new'}"
    )
    
    # Location field
    location = st.text_input(
        "Location",
        value=event.location if event else "",
        key=f"event_location_{event_id or 'new'}"
    )
    
    # Timestamp field
    timestamp = st.text_input(
        "Timestamp (e.g., 'Day 1', 'Year 2050')",
        value=event.timestamp if event else "",
        key=f"event_timestamp_{event_id or 'new'}"
    )
    
    # Characters involved
    if characters:
        character_options = {cid: c.name for cid, c in characters.items()}
        selected_characters = st.multiselect(
            "Characters Involved",
            options=list(character_options.keys()),
            default=event.characters_involved if event else [],
            format_func=lambda x: character_options[x],
            key=f"event_chars_{event_id or 'new'}"
        )
    else:
        st.info("No characters available")
        selected_characters = []
    
    # Buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("💾 Save", use_container_width=True, key=f"save_event_{event_id or 'new'}"):
            if not title:
                st.error("Title is required")
            else:
                # Create or update event
                event_data = {
                    "title": title,
                    "description": description,
                    "significance": significance,
                    "order": order,
                    "location": location,
                    "timestamp": timestamp,
                    "characters_involved": selected_characters
                }
                
                if is_edit_mode:
                    event_data["id"] = event_id
                
                on_save(PlotEvent(**event_data))
                st.toast(f"✅ Event '{title}' saved successfully!", icon="✅")
                st.rerun()
    
    with col2:
        if is_edit_mode and on_delete:
            if st.button("🗑️ Delete", use_container_width=True, type="secondary", key=f"delete_event_{event_id}"):
                if st.session_state.get(f"confirm_delete_{event_id}"):
                    on_delete(event_id)
                    st.toast(f"✅ Event '{event.title}' deleted", icon="✅")
                    st.rerun()
                else:
                    st.session_state[f"confirm_delete_{event_id}"] = True
                    st.warning("Click delete again to confirm")
                    st.rerun()


def render_setting_editor(
    setting_id: Optional[str],
    settings: dict[str, Setting],
    characters: dict[str, Character],
    plot_events: dict[str, PlotEvent],
    audio_service: AudioService,
    on_save: callable,
    on_delete: Optional[callable] = None
) -> None:
    """Render setting editor.
    
    Args:
        setting_id: ID of setting to edit, None for create mode
        settings: Dictionary of all settings
        characters: Dictionary of all characters for selection
        plot_events: Dictionary of all plot events for selection
        audio_service: Audio service for voice input
        on_save: Callback function when save is clicked
        on_delete: Optional callback function when delete is clicked
    """
    is_edit_mode = setting_id is not None
    setting = settings.get(setting_id) if is_edit_mode else None
    
    st.subheader("✏️ Edit Setting" if is_edit_mode else "➕ Create Setting")
    
    # Name field
    name = st.text_input(
        "Name *",
        value=setting.name if setting else "",
        key=f"setting_name_{setting_id or 'new'}"
    )
    
    # Type field
    type_options = ["location", "magic_system", "organization", "object", "other"]
    default_index = 0
    if setting and setting.type in type_options:
        default_index = type_options.index(setting.type)
    
    type_value = st.selectbox(
        "Type",
        options=type_options,
        index=default_index,
        key=f"setting_type_{setting_id or 'new'}"
    )
    
    # Description field
    description = st.text_area(
        "Description",
        value=setting.description if setting else "",
        height=150,
        key=f"setting_desc_{setting_id or 'new'}"
    )
    
    # Rules
    st.write("**Rules**")
    rules_list = setting.rules if setting else []
    
    # Initialize rules in session state
    rules_key = f"rules_{setting_id or 'new'}"
    if rules_key not in st.session_state:
        st.session_state[rules_key] = rules_list if rules_list else [""]
    
    rules = []
    for i, rule in enumerate(st.session_state[rules_key]):
        col_rule, col_remove = st.columns([5, 1])
        with col_rule:
            rule_value = st.text_input(
                f"Rule {i+1}",
                value=rule,
                key=f"setting_rule_{setting_id or 'new'}_{i}",
                label_visibility="collapsed"
            )
            if rule_value:
                rules.append(rule_value)
        with col_remove:
            if len(st.session_state[rules_key]) > 1:
                if st.button("✖", key=f"remove_rule_{setting_id or 'new'}_{i}"):
                    st.session_state[rules_key].pop(i)
                    st.rerun()
    
    if st.button("➕ Add Rule", key=f"add_rule_{setting_id or 'new'}"):
        st.session_state[rules_key].append("")
        st.rerun()
    
    # Related characters
    if characters:
        character_options = {cid: c.name for cid, c in characters.items()}
        selected_characters = st.multiselect(
            "Related Characters",
            options=list(character_options.keys()),
            default=setting.related_characters if setting else [],
            format_func=lambda x: character_options[x],
            key=f"setting_chars_{setting_id or 'new'}"
        )
    else:
        st.info("No characters available")
        selected_characters = []
    
    # Related events
    if plot_events:
        event_options = {eid: e.title for eid, e in plot_events.items()}
        selected_events = st.multiselect(
            "Related Events",
            options=list(event_options.keys()),
            default=setting.related_events if setting else [],
            format_func=lambda x: event_options[x],
            key=f"setting_events_{setting_id or 'new'}"
        )
    else:
        st.info("No events available")
        selected_events = []
    
    # Buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("💾 Save", use_container_width=True, key=f"save_setting_{setting_id or 'new'}"):
            if not name:
                st.error("Name is required")
            else:
                # Create or update setting
                setting_data = {
                    "name": name,
                    "type": type_value,
                    "description": description,
                    "rules": rules,
                    "related_characters": selected_characters,
                    "related_events": selected_events
                }
                
                if is_edit_mode:
                    setting_data["id"] = setting_id
                
                on_save(Setting(**setting_data))
                st.toast(f"✅ Setting '{name}' saved successfully!", icon="✅")
                st.rerun()
    
    with col2:
        if is_edit_mode and on_delete:
            if st.button("🗑️ Delete", use_container_width=True, type="secondary", key=f"delete_setting_{setting_id}"):
                if st.session_state.get(f"confirm_delete_{setting_id}"):
                    on_delete(setting_id)
                    st.toast(f"✅ Setting '{setting.name}' deleted", icon="✅")
                    st.rerun()
                else:
                    st.session_state[f"confirm_delete_{setting_id}"] = True
                    st.warning("Click delete again to confirm")
                    st.rerun()
