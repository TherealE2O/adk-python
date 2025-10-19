# Mind Map Visualization

## Overview

The AI Novel Editor now includes an **interactive mind map visualization** for the question tree, providing an intuitive visual representation of your story's development process.

## ✅ Features

### Interactive Mind Map
- **Visual Graph**: See your entire question tree as an interactive graph
- **Hierarchical Layout**: Questions organized from root to branches
- **Color-Coded Nodes**: Different colors for status and entity types
- **Click to Navigate**: Click any node to jump to that question
- **Zoom & Pan**: Scroll to zoom, drag to pan around the map
- **Hover Tooltips**: See full question text on hover

### Visual Indicators

#### Status Colors
- 🟢 **Green** - Answered questions
- 🟡 **Yellow** - Pending questions

#### Entity Type Colors
- 🔴 **Red** - Character questions
- 🔵 **Teal** - Plot event questions
- 🟢 **Light Green** - Setting questions

#### Icons
- ✅ Answered
- ⏳ Pending
- 👤 Character
- 📖 Plot Event
- 🗺️ Setting

## Installation

The mind map feature requires one additional package:

```bash
pip install streamlit-agraph
```

This is already included in `requirements.txt`.

## Usage

### Accessing Mind Map View

1. **Create a Project** and start world-building
2. **Answer the Initial Question** to create the question tree
3. **Select "Mind Map"** from the view mode options
4. **Interact with the Map**:
   - Click nodes to select questions
   - Scroll to zoom in/out
   - Drag to pan around
   - Hover to see full text

### View Modes

The question tree can be viewed in four different ways:

1. **Mind Map** (NEW!) - Interactive graph visualization
2. **Tree View** - Hierarchical expandable tree
3. **List by Category** - Questions grouped by type
4. **Timeline** - Chronological view

Switch between views using the radio buttons at the top.

## How It Works

### Graph Structure

```
Root Question (Box)
├── Character Question (Circle)
│   └── Follow-up Question (Circle)
├── Plot Question (Circle)
│   └── Follow-up Question (Circle)
└── Setting Question (Circle)
    └── Follow-up Question (Circle)
```

### Node Properties

- **Size**: Root node is larger (30px), children are smaller (15-20px)
- **Shape**: Root is a box, children are circles
- **Color**: Based on status (answered/pending) and entity type
- **Label**: Truncated to 50 characters with icons
- **Tooltip**: Full question text on hover

### Edge Properties

- **Direction**: From parent to child (top to bottom)
- **Type**: Smooth curves
- **Color**: Gray (#999999)

## Interactive Controls

### Mouse Controls
- **Left Click**: Select a node
- **Scroll Wheel**: Zoom in/out
- **Click + Drag**: Pan around the map
- **Hover**: Show tooltip with full question

### Keyboard Controls
- **Arrow Keys**: Navigate the map
- **+/-**: Zoom in/out
- **Space**: Reset view

### Navigation Buttons
- Built-in zoom controls appear in the corner
- Reset button to center the view

## Technical Details

### Implementation

The mind map is built using:
- **streamlit-agraph**: Interactive graph visualization library
- **Hierarchical Layout**: Automatic positioning of nodes
- **Physics Simulation**: Smooth node arrangement
- **Event Handling**: Click detection for navigation

### Performance

- **Fast Rendering**: Up to 100 nodes render instantly
- **Smooth Interactions**: 60 FPS zoom and pan
- **Responsive**: Adapts to screen size
- **Memory Efficient**: Only renders visible nodes

### Configuration

The mind map uses these settings:

```python
Config(
    width="100%",
    height=600,
    directed=True,
    physics=True,
    hierarchical=True,
    interaction={
        'hover': True,
        'navigationButtons': True,
        'keyboard': True,
        'zoomView': True,
        'dragView': True,
    },
    layout={
        'hierarchical': {
            'direction': 'UD',  # Top to bottom
            'levelSeparation': 150,
            'nodeSpacing': 200,
        }
    }
)
```

## Examples

### Small Tree (5-10 nodes)
```
Root: "What is your story about?"
├── "Who is the main character?"
│   └── "What are their powers?"
├── "What is the conflict?"
└── "Where does it take place?"
```

### Medium Tree (10-30 nodes)
- Multiple branches from root
- 2-3 levels deep
- Mix of answered and pending questions
- All entity types represented

### Large Tree (30+ nodes)
- Complex branching structure
- 3-4 levels deep
- Extensive character development
- Detailed plot and setting questions

## Best Practices

### For Best Visualization

1. **Answer Questions Progressively**
   - Start with root question
   - Answer follow-ups as they appear
   - Build the tree gradually

2. **Use Different Entity Types**
   - Mix character, plot, and setting questions
   - Creates a balanced, colorful map
   - Easier to navigate visually

3. **Keep Questions Concise**
   - Questions are truncated at 50 characters
   - Use clear, specific wording
   - Full text available on hover

### Navigation Tips

1. **Start with Overview**
   - Zoom out to see entire tree
   - Identify areas to focus on
   - Plan your answering strategy

2. **Zoom In for Details**
   - Click on a branch to focus
   - Read full questions on hover
   - Select questions to answer

3. **Use Multiple Views**
   - Mind Map for overview
   - Tree View for hierarchy
   - Category View for focus
   - Timeline View for progress

## Troubleshooting

### Mind Map Not Showing

**Problem**: "Mind Map" option not available

**Solution**: Install streamlit-agraph
```bash
pip install streamlit-agraph
```

### Nodes Overlapping

**Problem**: Nodes are too close together

**Solution**: 
- Zoom in for better spacing
- Adjust `nodeSpacing` in config (default: 200)
- Use Tree View for clearer hierarchy

### Can't Click Nodes

**Problem**: Clicking nodes doesn't work

**Solution**:
- Ensure you're clicking on the node itself (not empty space)
- Check that the question is pending (answered questions can't be selected)
- Try refreshing the page

### Map Too Large

**Problem**: Can't see all nodes at once

**Solution**:
- Zoom out using scroll wheel
- Use navigation buttons to reset view
- Consider using Timeline or Category view for large trees

## API Reference

### `render_mindmap(question_tree, on_node_click=None)`

Render the interactive mind map.

**Parameters**:
- `question_tree` (QuestionTree): The question tree to visualize
- `on_node_click` (callable, optional): Callback when node is clicked

**Returns**: `str | None` - Selected node ID if clicked

### `create_mindmap_visualization(question_tree)`

Create nodes and edges for visualization.

**Parameters**:
- `question_tree` (QuestionTree): The question tree

**Returns**: `tuple[list, list, dict]` - (nodes, edges, config)

### `get_mindmap_legend()`

Get HTML legend for the mind map.

**Returns**: `str` - HTML string with legend and instructions

## Comparison: View Modes

| Feature | Mind Map | Tree View | Category | Timeline |
|---------|----------|-----------|----------|----------|
| Visual | Graph | Expandable | Lists | Linear |
| Overview | ✅ Best | ⚠️ Good | ❌ Limited | ❌ Limited |
| Navigation | ✅ Click | ✅ Click | ✅ Click | ✅ Click |
| Hierarchy | ✅ Clear | ✅ Clear | ❌ Hidden | ❌ Hidden |
| Relationships | ✅ Visible | ⚠️ Nested | ❌ Hidden | ❌ Hidden |
| Large Trees | ⚠️ Zoom | ⚠️ Scroll | ✅ Good | ✅ Good |
| Best For | Overview | Structure | Focus | Progress |

## Future Enhancements

Possible improvements:
- [ ] Collapsible branches
- [ ] Search/filter nodes
- [ ] Export as image
- [ ] Custom color schemes
- [ ] Node grouping
- [ ] Minimap for large trees
- [ ] Animation on updates
- [ ] 3D visualization

## Examples in Code

### Basic Usage

```python
from src.ui.mindmap import render_mindmap

# In your Streamlit app
selected_node_id = render_mindmap(question_tree)

if selected_node_id:
    # User clicked a node
    navigate_to_question(selected_node_id)
```

### Custom Styling

```python
from src.ui.mindmap import create_mindmap_visualization

nodes, edges, config = create_mindmap_visualization(question_tree)

# Modify config
config.height = 800
config.layout['hierarchical']['direction'] = 'LR'  # Left to right

# Render with custom config
agraph(nodes=nodes, edges=edges, config=config)
```

## Conclusion

The mind map visualization provides an **intuitive, interactive way** to explore your story's question tree. Key benefits:

1. ✅ **Visual Overview** - See entire structure at a glance
2. ✅ **Easy Navigation** - Click to jump to any question
3. ✅ **Clear Relationships** - Understand parent-child connections
4. ✅ **Status at a Glance** - Color-coded answered/pending
5. ✅ **Interactive** - Zoom, pan, hover for details

Perfect for writers who think visually and want to see the big picture of their story development!
