import graphviz

# Create a graph object
graph = graphviz.Digraph()

# Add nodes to the graph with different colors
graph.node('A', style='filled', fillcolor='gray10', fontcolor='white')
graph.node('B', style='filled', fillcolor='gray50', fontcolor='balck')
graph.node('C', style='filled', fillcolor='gray100')

# Add edges between the nodes
graph.edge('A', 'B')
graph.edge('B', 'C')
graph.edge('C', 'A')

# Save the graph as a PNG file
graph.render('colored_graph', format='png')
