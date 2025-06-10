import gymnasium as gym # CHANGED: Using gymnasium aliased as gym
import numpy as np
import networkx as nx
from gymnasium import spaces # CHANGED: Importing spaces from gymnasium
from typing import Dict, Any

from architecture import create_dqc_graph
from circuit import QuantumCircuit

# Constants from paper
DEADLINE = 1500
NUM_LOGICAL_QUBITS = 18
NUM_GATES = 30
P_GEN = 0.95
COOLDOWN_SWAP = 3
COOLDOWN_TELE = 5
COOLDOWN_GEN = 5

class QuantumCompilerEnv(gym.Env):
    """
    A Gym environment for DQC compilation based on the paper's RL formulation.
    This version uses Gymnasium to be compatible with modern Stable-Baselines3.
    """
    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(QuantumCompilerEnv, self).__init__()

        # 1. DQC Architecture
        self.dqc_graph = create_dqc_graph()
        self.num_physical_qubits = self.dqc_graph.number_of_nodes()
        self.local_links = [e for e, attr in self.dqc_graph.edges.items() if attr['type'] == 'local']
        self.quantum_link = [e for e, attr in self.dqc_graph.edges.items() if attr['type'] == 'quantum'][0]
        
        # 2. Action Space Definition
        self.action_map = self._create_action_map()
        self.action_space = spaces.Discrete(len(self.action_map))

        # 3. Observation Space (State Space) Definition
        self.max_gates = NUM_GATES * 2 
        self.observation_space = spaces.Dict({
            "location": spaces.Box(low=-2, high=NUM_LOGICAL_QUBITS-1, shape=(self.num_physical_qubits,), dtype=np.int32),
            "dag_frontier": spaces.Box(low=0, high=NUM_LOGICAL_QUBITS-1, shape=(self.max_gates, 2), dtype=np.int32),
            "action_mask": spaces.Box(low=0, high=1, shape=(len(self.action_map),), dtype=np.int8)
        })

        # 4. Environment State Variables
        self.circuit = None
        self.qubit_locations = np.full(self.num_physical_qubits, -1, dtype=np.int32)
        self.cooldowns = np.zeros(self.num_physical_qubits, dtype=np.int32)
        self.epr_pairs = {} 
        self.time_elapsed = 0

    def _create_action_map(self):
        """Creates a mapping from action index to a descriptive tuple."""
        action_map = {0: ("stop",)}
        idx = 1
        for u, v in self.local_links:
            action_map[idx] = ("swap", u, v)
            idx += 1
        action_map[idx] = ("generate", self.quantum_link[0], self.quantum_link[1])
        idx += 1
        for p_qubit in range(self.num_physical_qubits):
            for neighbor in self.dqc_graph.neighbors(p_qubit):
                action_map[idx] = ("tele_qubit", p_qubit, neighbor)
                idx += 1
        return action_map

    def _get_obs(self) -> Dict[str, np.ndarray]:
        """Constructs the observation dictionary from the current state."""
        location_obs = self.qubit_locations.copy()

        frontier = self.circuit.get_frontier()
        dag_obs = np.full((self.max_gates, 2), -1, dtype=np.int32)
        for i, gate in enumerate(frontier):
            if i < self.max_gates:
                dag_obs[i] = [gate[2], gate[3]]
        
        action_mask = np.zeros(len(self.action_map), dtype=np.int8)
        action_mask[0] = 1 
        
        for idx, action in self.action_map.items():
            if idx == 0: continue
            action_type = action[0]
            
            if action_type == "swap":
                u, v = action[1], action[2]
                if self.cooldowns[u] == 0 and self.cooldowns[v] == 0 and self.qubit_locations[u] >= 0 and self.qubit_locations[v] >= 0:
                    action_mask[idx] = 1

            elif action_type == "generate":
                u, v = action[1], action[2]
                if self.cooldowns[u] == 0 and self.cooldowns[v] == 0 and self.qubit_locations[u] == -1 and self.qubit_locations[v] == -1:
                    action_mask[idx] = 1
            
            elif action_type == "tele_qubit":
                p1, p2 = action[1], action[2]
                is_logical_epr_pair = (self.qubit_locations[p1] >= 0 and self.qubit_locations[p2] == -2) or (self.qubit_locations[p1] == -2 and self.qubit_locations[p2] >= 0)
                if self.cooldowns[p1] == 0 and self.cooldowns[p2] == 0 and is_logical_epr_pair:
                     action_mask[idx] = 1

        return {"location": location_obs, "dag_frontier": dag_obs, "action_mask": action_mask}

    def reset(self, seed=None, options=None):
        """Resets the environment for a new episode."""
        super().reset(seed=seed)
        self.circuit = QuantumCircuit(NUM_LOGICAL_QUBITS, NUM_GATES)
        self.qubit_locations.fill(-1)
        physical_qubits = self.np_random.choice(self.num_physical_qubits, NUM_LOGICAL_QUBITS, replace=False)
        for i in range(NUM_LOGICAL_QUBITS):
            self.qubit_locations[physical_qubits[i]] = i
        self.cooldowns.fill(0)
        self.epr_pairs = {}
        self.time_elapsed = 0
        return self._get_obs(), {} # Gymnasium returns obs and info dict

    def step(self, action_idx: int) -> (Dict[str, np.ndarray], float, bool, bool, Dict[str, Any]):
        """Executes one action and updates the environment."""
        action_tuple = self.action_map[action_idx]
        action_type = action_tuple[0]
        reward = 0
        terminated = False # Use 'terminated' for goal-reached states
        truncated = False  # Use 'truncated' for time-limit states
        info = {}

        action_mask = self._get_obs()['action_mask']
        # if action_mask[action_idx] == 0:
        #     # Taking an invalid action is a waste of a step but not a terminal condition
        #     reward = -500 # Heavy penalty
        #     return self._get_obs(), reward, terminated, truncated, info

        if action_type == "stop":
            self.time_elapsed += 1
            reward += -20 
            self.cooldowns[self.cooldowns > 0] -= 1
            frontier = self.circuit.get_frontier()
            gates_to_remove = set()
            loc_map = {lq: pq for pq, lq in enumerate(self.qubit_locations) if lq >= 0}
            for gate in frontier:
                q1, q2 = gate[2], gate[3]
                if q1 not in loc_map or q2 not in loc_map: continue
                p1, p2 = loc_map[q1], loc_map[q2]
                if self.dqc_graph.has_edge(p1, p2) and self.dqc_graph.edges[p1, p2]['type'] == 'local':
                    if self.cooldowns[p1] == 0 and self.cooldowns[p2] == 0:
                        gates_to_remove.add(gate)
                        self.cooldowns[p1] = self.cooldowns[p2] = 1 
                        reward += 500 
            for gate in gates_to_remove:
                self.circuit.remove_gate(gate)
        
        elif action_type == "swap":
            u, v = action_tuple[1], action_tuple[2]
            self.qubit_locations[u], self.qubit_locations[v] = self.qubit_locations[v], self.qubit_locations[u]
            self.cooldowns[u] = self.cooldowns[v] = COOLDOWN_SWAP
            reward += 10 
        
        elif action_type == "generate":
            u, v = action_tuple[1], action_tuple[2]
            if self.np_random.random() < P_GEN:
                self.qubit_locations[u] = -2 
                self.qubit_locations[v] = -2
                self.epr_pairs[u] = v
                self.epr_pairs[v] = u
            self.cooldowns[u] = self.cooldowns[v] = COOLDOWN_GEN

        elif action_type == "tele_qubit":
            p1, p2 = action_tuple[1], action_tuple[2]
            logical_pq = p1 if self.qubit_locations[p1] >= 0 else p2
            epr_pq = p2 if self.qubit_locations[p1] >= 0 else p1
            other_epr_pq = self.epr_pairs.pop(epr_pq)
            self.epr_pairs.pop(other_epr_pq, None) # Use .pop(key, None) for safety
            self.qubit_locations[other_epr_pq] = self.qubit_locations[logical_pq]
            self.qubit_locations[logical_pq] = -1 
            self.qubit_locations[epr_pq] = -1
            self.cooldowns[logical_pq] = self.cooldowns[epr_pq] = self.cooldowns[other_epr_pq] = COOLDOWN_TELE
            reward += 20
            
        if self.circuit.is_complete():
            terminated = True
            reward += -3000
            info['is_success'] = True
        
        if self.time_elapsed >= DEADLINE:
            truncated = True
            if not self.circuit.is_complete():
                reward += 3000
                info['is_success'] = False
        
        info['time_elapsed'] = self.time_elapsed
        return self._get_obs(), reward, terminated, truncated, info