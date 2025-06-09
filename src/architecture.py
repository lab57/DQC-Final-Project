import networkx as nx

# Coupling graph for IBM Q 16 Guadalupe, from Figure 3 and IBM's documentation
GUADALUPE_COUPLING_GRAPH = [
    (0, 1), (1, 2), (1, 4), (2, 3), (3, 5), (4, 7), (5, 8),
    (6, 7), (7, 10), (8, 9), (8, 11), (10, 12), (11, 14),
    (12, 13), (12, 15), (13, 14)
]

def create_dqc_graph():
    """
    Creates the DQC architecture graph with two interconnected QPUs.

    The architecture consists of two 16-qubit Guadalupe QPUs.
    A single quantum link connects qubit 6 on the first QPU to qubit 6
    on the second QPU.

    Returns:
        nx.Graph: A networkx graph representing the full DQC architecture.
                  Nodes are integers 0-31. Edges have a 'type' attribute:
                  'local' for intra-QPU links, 'quantum' for the inter-QPU link.
    """
    g = nx.Graph()
    num_physical_qubits_per_qpu = 16

    # Add QPU 1 (nodes 0-15)
    for u, v in GUADALUPE_COUPLING_GRAPH:
        g.add_edge(u, v, type='local')

    # Add QPU 2 (nodes 16-31)
    for u, v in GUADALUPE_COUPLING_GRAPH:
        g.add_edge(u + num_physical_qubits_per_qpu, v + num_physical_qubits_per_qpu, type='local')

    # Add quantum link between QPU1's qubit 6 and QPU2's qubit 6
    # These are node 6 and node 16+6=22 in the combined graph.
    g.add_edge(6, 22, type='quantum')
    
    # Add self-loops to make sure all nodes are included, even if disconnected
    for i in range(2 * num_physical_qubits_per_qpu):
        if i not in g:
            g.add_node(i)

    return g

if __name__ == '__main__':
    # Example of how to create and inspect the graph
    dqc_graph = create_dqc_graph()
    print(f"Total number of physical qubits (nodes): {dqc_graph.number_of_nodes()}")
    print(f"Total number of links (edges): {dqc_graph.number_of_edges()}")

    local_links = [e for e, attr in dqc_graph.edges.items() if attr['type'] == 'local']
    quantum_links = [e for e, attr in dqc_graph.edges.items() if attr['type'] == 'quantum']

    print(f"Number of local links: {len(local_links)}")
    print(f"Number of quantum links: {len(quantum_links)}")
    print(f"Quantum link connects: {quantum_links[0]}")