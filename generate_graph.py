from graphviz import Digraph
from virtual_sales_agent.graph import builder  # Your existing graph builder

def generate_graph_visualization():
    """
    Generates a visual representation of the LangGraph workflow
    and saves it as graph.png in the assets directory.
    """
    dot = Digraph(comment='Virtual Sales Agent Workflow')
    
    # Set graph attributes
    dot.attr(rankdir='LR')  # Left to right layout
    
    # Add nodes
    dot.node('START', 'Start', shape='circle')
    dot.node('assistant', 'Assistant', shape='box')
    dot.node('safe_tools', 'Safe Tools', shape='box')
    dot.node('sensitive_tools', 'Sensitive Tools', shape='box')
    dot.node('END', 'End', shape='circle')
    
    # Add edges
    dot.edge('START', 'assistant')
    dot.edge('assistant', 'safe_tools')
    dot.edge('assistant', 'sensitive_tools')
    dot.edge('assistant', 'END')
    dot.edge('safe_tools', 'assistant')
    dot.edge('sensitive_tools', 'assistant')

    # Add color coding
    dot.node('safe_tools', 'Safe Tools', shape='box', style='filled', fillcolor='lightblue')
    dot.node('sensitive_tools', 'Sensitive Tools', shape='box', style='filled', fillcolor='lightpink')

    # Add tooltips
    dot.node('safe_tools', 'Safe Tools', tooltip='Read-only operations')
    dot.node('sensitive_tools', 'Sensitive Tools', tooltip='Operations requiring approval')

    # Add edge labels
    dot.edge('assistant', 'safe_tools', label='safe operation')
    dot.edge('assistant', 'sensitive_tools', label='needs approval')
    
    # Save the graph
    dot.render('assets/graph_2', format='png', cleanup=True)

if __name__ == "__main__":
    generate_graph_visualization()