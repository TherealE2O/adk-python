"""Enhanced Truth viewer UI components."""

from __future__ import annotations

import streamlit as st
from src.models.truth import TruthKnowledgeBase, Character, PlotEvent, Setting
from src.models.project import Project


def render_character_viewer(project: Project):
    """
    Enhanced Character Sheet viewer with search, statistics, and relationships.
    
    Requirements: 10.1, 10.2, 10.3, 10.4, 10.5
    """
    st.subheader("👥 Character Sheets")
    
    characters = list(project.truth.characters.values())
    
    if not characters:
        st.info("No characters have been identified yet. Continue world-building to add characters.")
        return
    
    # Search functionality
    search_query = st.text_input(
        "🔍 Search characters",
        placeholder="Search by name, trait, or description...",
        key="char_search"
    )
    
    # Filter characters based on search
    if search_query:
        filtered_chars = [
            c for c in characters
            if search_query.lower() in c.name.lower()
            or search_query.lower() in c.description.lower()
            or any(search_query.lower() in trait.lower() for trait in c.traits)
            or search_query.lower() in c.backstory.lower()
        ]
    else:
        filtered_chars = characters
    
    # Character count and statistics
    st.write(f"**Total Characters:** {len(characters)} | **Showing:** {len(filtered_chars)}")
    
    if not filtered_chars:
        st.warning("No characters match your search.")
        return
    
    # Character selector
    char_names = {c.id: c.name for c in filtered_chars}
    selected_char_id = st.selectbox(
        "Select a character to view details:",
        options=list(char_names.keys()),
        format_func=lambda x: char_names[x],
        key="char_selector"
    )
    
    if selected_char_id:
        char = project.truth.characters[selected_char_id]
        
        # Display character details in organized format
        col_title, col_edit = st.columns([4, 1])
        with col_title:
            st.markdown(f"### {char.name}")
        with col_edit:
            if st.button("✏️ Edit", key=f"edit_char_{selected_char_id}"):
                st.session_state.show_truth_editor = 'character'
                st.session_state.editor_entity_id = selected_char_id
                del st.session_state.show_truth_viewer
                st.rerun()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Description
            st.markdown("#### Description")
            st.write(char.description)
            
            # Backstory
            if char.backstory:
                st.markdown("#### Backstory")
                st.write(char.backstory)
            
            # Traits
            if char.traits:
                st.markdown("#### Traits")
                st.write(", ".join(f"**{trait}**" for trait in char.traits))
            
            # Relationships
            if char.relationships:
                st.markdown("#### Relationships")
                for other_char_id, relationship in char.relationships.items():
                    other_char = project.truth.characters.get(other_char_id)
                    if other_char:
                        st.write(f"• **{other_char.name}:** {relationship}")
        
        with col2:
            # Related plot events
            st.markdown("#### Related Plot Events")
            related_events = [
                e for e in project.truth.plot_events.values()
                if char.id in e.characters_involved
            ]
            if related_events:
                for event in sorted(related_events, key=lambda e: e.order):
                    st.write(f"• {event.title}")
            else:
                st.caption("No related plot events")
            
            # Related settings
            st.markdown("#### Related Settings")
            related_settings = [
                s for s in project.truth.settings.values()
                if char.id in s.related_characters
            ]
            if related_settings:
                for setting in related_settings:
                    st.write(f"• {setting.name}")
            else:
                st.caption("No related settings")


def render_timeline_viewer(project: Project):
    """
    Enhanced Timeline viewer with filtering and visual markers.
    
    Requirements: 11.1, 11.2, 11.3, 11.4, 11.5
    """
    st.subheader("📅 Timeline")
    
    events = list(project.truth.plot_events.values())
    
    if not events:
        st.info("No plot events have been identified yet. Continue world-building to add events.")
        return
    
    # Sort events chronologically
    sorted_events = sorted(events, key=lambda e: e.order)
    
    # Filtering options
    st.markdown("#### Filters")
    col1, col2 = st.columns(2)
    
    with col1:
        # Filter by character
        all_chars = list(project.truth.characters.values())
        char_filter_options = ["All Characters"] + [c.name for c in all_chars]
        selected_char_filter = st.selectbox(
            "Filter by Character:",
            options=char_filter_options,
            key="timeline_char_filter"
        )
    
    with col2:
        # Filter by setting
        all_settings = list(project.truth.settings.values())
        setting_filter_options = ["All Settings"] + [s.name for s in all_settings]
        selected_setting_filter = st.selectbox(
            "Filter by Setting:",
            options=setting_filter_options,
            key="timeline_setting_filter"
        )
    
    # Apply filters
    filtered_events = sorted_events
    
    if selected_char_filter != "All Characters":
        char_id = next((c.id for c in all_chars if c.name == selected_char_filter), None)
        if char_id:
            filtered_events = [e for e in filtered_events if char_id in e.characters_involved]
    
    if selected_setting_filter != "All Settings":
        setting_id = next((s.id for s in all_settings if s.name == selected_setting_filter), None)
        if setting_id:
            # Filter by location field since PlotEvent doesn't have related_settings
            filtered_events = [e for e in filtered_events if e.location and setting_id in e.location]
    
    # Display event count
    st.write(f"**Total Events:** {len(sorted_events)} | **Showing:** {len(filtered_events)}")
    
    if not filtered_events:
        st.warning("No events match your filters.")
        return
    
    # Visual timeline display
    st.markdown("---")
    
    for i, event in enumerate(filtered_events):
        # Timeline marker
        col_marker, col_content = st.columns([1, 10])
        
        with col_marker:
            st.markdown(f"**{event.order}**")
            if i < len(filtered_events) - 1:
                st.markdown("↓")
        
        with col_content:
            with st.expander(f"**{event.title}**", expanded=False):
                st.write(event.description)
                
                # Significance
                if event.significance:
                    st.markdown(f"**Significance:** {event.significance}")
                
                # Character involvement
                if event.characters_involved:
                    char_names = [
                        project.truth.characters[cid].name
                        for cid in event.characters_involved
                        if cid in project.truth.characters
                    ]
                    if char_names:
                        st.markdown(f"**Characters:** {', '.join(char_names)}")
                
                # Location
                if event.location:
                    st.markdown(f"**Location:** {event.location}")
                
                # Edit button
                if st.button("✏️ Edit", key=f"edit_event_{event.id}"):
                    st.session_state.show_truth_editor = 'event'
                    st.session_state.editor_entity_id = event.id
                    del st.session_state.show_truth_viewer
                    st.rerun()


def render_settings_viewer(project: Project):
    """
    Enhanced Setting and World-Building viewer with filtering and organization.
    
    Requirements: 12.1, 12.2, 12.3, 12.4, 12.5
    """
    st.subheader("🗺️ Settings & World-Building")
    
    settings = list(project.truth.settings.values())
    
    if not settings:
        st.info("No settings have been identified yet. Continue world-building to add locations and world elements.")
        return
    
    # Group settings by type
    settings_by_type = {}
    for setting in settings:
        setting_type = setting.type
        if setting_type not in settings_by_type:
            settings_by_type[setting_type] = []
        settings_by_type[setting_type].append(setting)
    
    # Type filter
    type_options = ["All Types"] + list(settings_by_type.keys())
    selected_type = st.selectbox(
        "Filter by Type:",
        options=type_options,
        key="setting_type_filter"
    )
    
    # Display count
    if selected_type == "All Types":
        filtered_settings = settings
    else:
        filtered_settings = settings_by_type[selected_type]
    
    st.write(f"**Total Settings:** {len(settings)} | **Showing:** {len(filtered_settings)}")
    
    # Display settings organized by type
    if selected_type == "All Types":
        # Show tabs for each type
        if len(settings_by_type) > 1:
            tabs = st.tabs(list(settings_by_type.keys()))
            for tab, (setting_type, type_settings) in zip(tabs, settings_by_type.items()):
                with tab:
                    _render_setting_list(type_settings, project)
        else:
            # Only one type, show directly
            _render_setting_list(filtered_settings, project)
    else:
        # Show filtered type
        _render_setting_list(filtered_settings, project)


def _render_setting_list(settings: list[Setting], project: Project):
    """Helper function to render a list of settings."""
    for setting in settings:
        with st.expander(f"**{setting.name}** ({setting.type})"):
            st.write(setting.description)
            
            # Rules
            if setting.rules:
                st.markdown("**Rules:**")
                for rule in setting.rules:
                    st.write(f"• {rule}")
            
            # Related characters
            if setting.related_characters:
                char_names = [
                    project.truth.characters[cid].name
                    for cid in setting.related_characters
                    if cid in project.truth.characters
                ]
                if char_names:
                    st.markdown("**Related Characters:**")
                    st.write(", ".join(char_names))
            
            # Related events
            if setting.related_events:
                event_titles = [
                    project.truth.plot_events[eid].title
                    for eid in setting.related_events
                    if eid in project.truth.plot_events
                ]
                if event_titles:
                    st.markdown("**Related Events:**")
                    for title in event_titles:
                        st.write(f"• {title}")
            
            # Edit button
            if st.button("✏️ Edit", key=f"edit_setting_{setting.id}"):
                st.session_state.show_truth_editor = 'setting'
                st.session_state.editor_entity_id = setting.id
                del st.session_state.show_truth_viewer
                st.rerun()


def render_global_search(project: Project):
    """
    Global Truth search across all entities.
    
    Requirements: 13.1, 13.2, 13.3, 13.4, 13.5
    """
    st.subheader("🔍 Search Truth")
    
    search_query = st.text_input(
        "Search across all story facts:",
        placeholder="Search characters, events, settings...",
        key="global_truth_search"
    )
    
    if not search_query:
        st.info("Enter a search term to find information across your story's Truth.")
        return
    
    query_lower = search_query.lower()
    results = []
    
    # Search characters
    for char in project.truth.characters.values():
        if (query_lower in char.name.lower()
            or query_lower in char.description.lower()
            or any(query_lower in trait.lower() for trait in char.traits)
            or query_lower in char.backstory.lower()):
            results.append({
                'type': 'character',
                'icon': '👤',
                'name': char.name,
                'description': char.description,
                'id': char.id
            })
    
    # Search plot events
    for event in project.truth.plot_events.values():
        if (query_lower in event.title.lower()
            or query_lower in event.description.lower()
            or query_lower in event.significance.lower()):
            results.append({
                'type': 'plot_event',
                'icon': '📖',
                'name': event.title,
                'description': event.description,
                'id': event.id
            })
    
    # Search settings
    for setting in project.truth.settings.values():
        if (query_lower in setting.name.lower()
            or query_lower in setting.description.lower()
            or query_lower in setting.type.lower()
            or any(query_lower in rule.lower() for rule in setting.rules)):
            results.append({
                'type': 'setting',
                'icon': '🗺️',
                'name': setting.name,
                'description': setting.description,
                'id': setting.id
            })
    
    # Display results
    st.write(f"**Found {len(results)} results**")
    
    if not results:
        st.warning("No results found. Try a different search term.")
        return
    
    for result in results:
        with st.expander(f"{result['icon']} **{result['name']}** ({result['type']})"):
            st.write(result['description'])
            
            # View full entity button
            if st.button(f"View Full Details", key=f"view_{result['type']}_{result['id']}"):
                st.session_state.show_truth_viewer = result['type'] + 's'
                st.session_state.selected_entity_id = result['id']
                st.rerun()