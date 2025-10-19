"""Test script for mind map visualization."""

from src.models.truth import QuestionTree, QuestionNode, EntityType, QuestionStatus
from src.ui.mindmap import create_mindmap_visualization, AGRAPH_AVAILABLE

def test_mindmap():
  """Test mind map visualization with sample data."""
  print("Testing Mind Map Visualization...")
  print("-" * 50)
  
  # Check if agraph is available
  if not AGRAPH_AVAILABLE:
    print("❌ streamlit-agraph not installed")
    print("   Install with: pip install streamlit-agraph")
    return
  
  print("✅ streamlit-agraph is available")
  
  # Create a sample question tree
  tree = QuestionTree(root_id="root")
  
  # Root question
  root = QuestionNode(
      id="root",
      question="What is your story about?",
      entity_type=EntityType.PLOT_EVENT,
      status=QuestionStatus.ANSWERED,
      answer="A fantasy story about a young wizard"
  )
  tree.add_node(root)
  
  # Character questions
  char1 = QuestionNode(
      id="char1",
      question="What is the main character's name?",
      entity_type=EntityType.CHARACTER,
      status=QuestionStatus.ANSWERED,
      answer="Elena",
      parent_id="root"
  )
  tree.add_node(char1, "root")
  
  char2 = QuestionNode(
      id="char2",
      question="What are Elena's special powers?",
      entity_type=EntityType.CHARACTER,
      status=QuestionStatus.PENDING,
      parent_id="char1"
  )
  tree.add_node(char2, "char1")
  
  # Plot questions
  plot1 = QuestionNode(
      id="plot1",
      question="What is the central conflict?",
      entity_type=EntityType.PLOT_EVENT,
      status=QuestionStatus.ANSWERED,
      answer="She must stop a dark sorcerer",
      parent_id="root"
  )
  tree.add_node(plot1, "root")
  
  plot2 = QuestionNode(
      id="plot2",
      question="Who is the dark sorcerer?",
      entity_type=EntityType.CHARACTER,
      status=QuestionStatus.PENDING,
      parent_id="plot1"
  )
  tree.add_node(plot2, "plot1")
  
  # Setting questions
  setting1 = QuestionNode(
      id="setting1",
      question="Where does the story take place?",
      entity_type=EntityType.SETTING,
      status=QuestionStatus.ANSWERED,
      answer="A magical academy",
      parent_id="root"
  )
  tree.add_node(setting1, "root")
  
  setting2 = QuestionNode(
      id="setting2",
      question="What makes this academy special?",
      entity_type=EntityType.SETTING,
      status=QuestionStatus.PENDING,
      parent_id="setting1"
  )
  tree.add_node(setting2, "setting1")
  
  # Create visualization
  nodes, edges, config = create_mindmap_visualization(tree)
  
  print(f"\n📊 Mind Map Statistics:")
  print(f"   • Total nodes: {len(nodes)}")
  print(f"   • Total edges: {len(edges)}")
  print(f"   • Root node: {root.question}")
  
  print(f"\n🎨 Node Colors:")
  print(f"   • Character questions: Red (#FF6B6B)")
  print(f"   • Plot questions: Teal (#4ECDC4)")
  print(f"   • Setting questions: Light Green (#95E1D3)")
  print(f"   • Answered: Green (#51CF66)")
  print(f"   • Pending: Yellow (#FFD93D)")
  
  print(f"\n📝 Node Details:")
  for node in nodes:
    print(f"   • {node.label[:60]}...")
  
  print(f"\n🔗 Edges:")
  for edge in edges:
    print(f"   • {edge.source} → {edge.to}")
  
  print("\n" + "-" * 50)
  print("✅ Mind map visualization test complete!")
  print("\n💡 To see the interactive mind map:")
  print("   1. Run: streamlit run app.py")
  print("   2. Create a project")
  print("   3. Answer the initial question")
  print("   4. Select 'Mind Map' view mode")

if __name__ == "__main__":
  test_mindmap()
