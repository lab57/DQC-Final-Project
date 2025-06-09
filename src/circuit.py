import numpy as np
import networkx as nx

class QuantumCircuit:
    """
    Represents a quantum circuit as a Directed Acyclic Graph (DAG).
    """
    def __init__(self, num_qubits: int, num_gates: int):
        self.num_qubits = num_qubits
        self.num_gates = num_gates
        self.gates = []
        self.dag = self._generate_random_circuit()
        self.initial_gate_count = self.dag.number_of_nodes()

    def _generate_random_circuit(self) -> nx.DiGraph:
        """
        Generates a random sequence of CNOT gates and creates a dependency DAG.

        Returns:
            nx.DiGraph: The circuit's dependency graph. Nodes are gate tuples
                        (gate_idx, 'cnot', q1, q2). Edges represent dependencies.
        """
        dag = nx.DiGraph()
        qubit_last_gate = {i: -1 for i in range(self.num_qubits)}

        for i in range(self.num_gates):
            # Choose two distinct random qubits
            q1, q2 = np.random.choice(self.num_qubits, 2, replace=False)
            gate = (i, 'cnot', int(q1), int(q2))
            self.gates.append(gate)
            dag.add_node(gate)

            # Add dependency edges from the last gate that used q1 or q2
            if qubit_last_gate[q1] != -1:
                dag.add_edge(self.gates[qubit_last_gate[q1]], gate)
            if qubit_last_gate[q2] != -1:
                dag.add_edge(self.gates[qubit_last_gate[q2]], gate)

            qubit_last_gate[q1] = i
            qubit_last_gate[q2] = i
            
        return dag

    def get_frontier(self) -> set:
        """
        Finds the set of executable gates (those with an in-degree of 0).

        Returns:
            set: A set of gate tuples that are ready to be executed.
        """
        return {node for node, in_degree in self.dag.in_degree() if in_degree == 0}

    def remove_gate(self, gate_to_remove: tuple):
        """
        Removes a gate from the DAG, freeing up subsequent gates.
        """
        if self.dag.has_node(gate_to_remove):
            self.dag.remove_node(gate_to_remove)

    def is_complete(self) -> bool:
        """
        Checks if all gates in the circuit have been executed.
        """
        return self.dag.number_of_nodes() == 0

if __name__ == '__main__':
    # Example of how to use the QuantumCircuit class
    circuit = QuantumCircuit(num_qubits=18, num_gates=30)
    print(f"Generated a circuit with {circuit.num_qubits} qubits and {circuit.initial_gate_count} gates.")
    
    frontier = circuit.get_frontier()
    print(f"Initial frontier size: {len(frontier)}")
    print(f"Example frontier gate: {next(iter(frontier)) if frontier else 'None'}")

    if frontier:
        gate_to_remove = next(iter(frontier))
        circuit.remove_gate(gate_to_remove)
        print(f"\nRemoved gate: {gate_to_remove}")
        new_frontier = circuit.get_frontier()
        print(f"New frontier size: {len(new_frontier)}")

    print(f"\nIs circuit complete? {circuit.is_complete()}")