"""Mind map visualization for question tree."""

from __future__ import annotations

from typing import TYPE_CHECKING

try:
  from streamlit_agraph import agraph, Node, Edge, Config
  AGRAPH_AVAILABLE = True
except ImportError:
  AGRAPH_AVAILABLE = False

if TYPE_CHECKING:
  from ..models.truth import QuestionTree, QuestionNode


def create_mindmap_visualization(question_tree: QuestionTree) -> tuple[list, list, dict]:
  """Create nodes and edges for mind map visualization.
  
  Args:
    question_tree: The question tree to visualize.
    
  Returns:
    Tuple of (nodes, edges, config) for agraph.
  """
  if not AGRAPH_AVAILABLE:
    return [], [], {}
  
  nodes = []
  edges = []
  
  # Color scheme
  colors = {
      'character': '#FF6B6B',      # Red
      'plot_event': '#4ECDC4',     # Teal
      'setting': '#95E1D3',        # Light green
      'answered': '#51CF66',       # Green
      'pending': '#FFD93D',        # Yellow
  }
  
  # Entity type labels
  entity_labels = {
      'character': '👤',
      'plot_event': '📖',
      'setting': '🗺️',
  }
  
  def add_node_recursive(node_id: str, level: int = 0):
    """Recursively add nodes and edges."""
    node = question_tree.get_node(node_id)
    if not node:
      return
    
    # Determine node color based on status and entity type
    if node.status.value == 'answered':
      color = colors['answered']
      status_icon = '✅'
    else:
      color = colors.get(node.entity_type.value, colors['pending'])
      status_icon = '⏳'
    
    entity_icon = entity_labels.get(node.entity_type.value, '❓')
    
    # Create node label (truncate long questions)
    label = node.question
    if len(label) > 50:
      label = label[:47] + "..."
    
    # Add status and entity icons
    label = f"{status_icon} {entity_icon} {label}"
    
    # Calculate node size based on level (root is larger)
    size = 30 if level == 0 else 20 if level == 1 else 15
    
    # Create node
    nodes.append(
        Node(
            id=node.id,
            label=label,
            size=size,
            color=color,
            shape="box" if level == 0 else "ellipse",
            title=node.question,  # Tooltip shows full question
        )
    )
    
    # Add edges to children
    for child_id in node.children_ids:
      edges.append(
          Edge(
              source=node.id,
              target=child_id,
              type="CURVE_SMOOTH",
          )
      )
      
      # Recursively add child nodes
      add_node_recursive(child_id, level + 1)
  
  # Start from root
  if question_tree.root_id:
    add_node_recursive(question_tree.root_id)
  
  # Configuration for the graph
  config = Config(
      width="100%",
      height=600,
      directed=True,
      physics=True,
      hierarchical=True,
      nodeHighlightBehavior=True,
      highlightColor="#F7A7A6",
      collapsible=False,
      node={
          'labelProperty': 'label',
          'renderLabel': True,
          'fontSize': 12,
          'fontColor': '#000000',
      },
      link={
          'labelProperty': 'label',
          'renderLabel': False,
          'color': '#999999',
      },
      # Interactive features
      interaction={
          'hover': True,
          'navigationButtons': True,
          'keyboard': True,
          'zoomView': True,
          'dragView': True,
      },
      # Layout configuration
      layout={
          'hierarchical': {
              'enabled': True,
              'direction': 'UD',  # Up-Down (top to bottom)
              'sortMethod': 'directed',
              'levelSeparation': 150,
              'nodeSpacing': 200,
          }
      },
  )
  
  return nodes, edges, config


def render_mindmap(question_tree: QuestionTree, on_node_click=None):
  """Render the mind map visualization.
  
  Args:
    question_tree: The question tree to visualize.
    on_node_click: Optional callback when a node is clicked.
    
  Returns:
    The selected node ID if a node was clicked, None otherwise.
  """
  if not AGRAPH_AVAILABLE:
    return None
  
  nodes, edges, config = create_mindmap_visualization(question_tree)
  
  if not nodes:
    return None
  
  # Render the graph
  selected = agraph(nodes=nodes, edges=edges, config=config)
  
  return selected


def get_mindmap_legend() -> str:
  """Get HTML legend for the mind map.
  
  Returns:
    HTML string with legend.
  """
  return """
  <div style="padding: 10px; background-color: #f0f0f0; border-radius: 5px; margin-bottom: 10px;">
    <strong>🧠 Mind Map Legend:</strong><br/>
    <span style="color: #51CF66;">●</span> Answered Question &nbsp;
    <span style="color: #FFD93D;">●</span> Pending Question<br/>
    <span style="color: #FF6B6B;">●</span> Character &nbsp;
    <span style="color: #4ECDC4;">●</span> Plot Event &nbsp;
    <span style="color: #95E1D3;">●</span> Setting<br/>
    <br/>
    <strong>💡 How to Use:</strong><br/>
    <small>
    • <strong>Click</strong> on a node to select that question<br/>
    • <strong>Scroll</strong> to zoom in/out<br/>
    • <strong>Drag</strong> to pan around the map<br/>
    • <strong>Hover</strong> over nodes to see full question text
    </small>
  </div>
  """
