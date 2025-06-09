import torch
from torch import nn
from gymnasium import spaces

class QNetworkWrapper(nn.Module):
    """
    A wrapper for a Q-network that handles action masking.
    It assumes the input observation is a flattened dictionary, where the
    action mask is appended to the end of the observation vector.
    """
    def __init__(self, q_network: nn.Module, observation_space: spaces.Space):
        super().__init__()
        self.q_network = q_network
        
        assert isinstance(observation_space, spaces.Box), "QNetworkWrapper requires a flattened Box observation space."
        
        # We still need to know the split point to find the mask later.
        self.main_obs_dim = 0 # This will be set from the training script

    def forward(self, flattened_obs: torch.Tensor) -> torch.Tensor:
        """
        This method intercepts the forward pass.
        1. Gets Q-values from the original network using the FULL observation.
        2. Extracts the action mask from the input observation vector.
        3. Applies the mask to the Q-values.
        4. Returns the masked Q-values.
        """
        # --- THE FIX IS HERE ---
        # 1. Get the original Q-values using the full observation vector.
        # The network was trained to expect the full vector as input.
        q_values = self.q_network(flattened_obs)
        
        # 2. Extract the mask, which is at the end of the observation vector.
        mask = flattened_obs[:, self.main_obs_dim:]
        
        # 3. Apply the mask: where the mask is 0, set Q-value to -infinity.
        # This ensures that an invalid action will never be chosen as the maximum.
        masked_q_values = q_values.masked_fill(mask == 0, -torch.inf)
        
        return masked_q_values