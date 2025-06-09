import torch
from torch import nn
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
from stable_baselines3.common.policies import ActorCriticPolicy
from stable_baselines3.common.distributions import CategoricalDistribution
from typing import Dict, Tuple

class MaskableActorCriticPolicy(ActorCriticPolicy):
    """
    Custom policy for PPO to handle action masking.
    It assumes the observation space has a key 'action_mask'.
    """
    def __init__(self, *args, **kwargs):
        super(MaskableActorCriticPolicy, self).__init__(*args, **kwargs)

    def _build(self, lr_schedule):
        super()._build(lr_schedule)

    def get_distribution(self, obs: Dict[str, torch.Tensor]) -> CategoricalDistribution:
        """
        Overrides the default method to incorporate the action mask.
        
        :param obs: The observation dictionary.
        :return: A categorical distribution with invalid actions masked out.
        """
        features = self.extract_features(obs)
        latent_pi, _ = self.mlp_extractor(features)
        
        # Get the action mask from the observation
        action_mask = obs["action_mask"]
        
        # Apply the mask to the logits by setting masked actions to a large negative value
        # This makes their probability effectively zero after the softmax.
        logits = self.action_net(latent_pi)
        logits[action_mask == 0] = -1e8
        
        return CategoricalDistribution(logits=logits)

    def predict_values(self, obs: Dict[str, torch.Tensor]) -> torch.Tensor:
        """
        Predicts the value (critic) of a state.
        
        :param obs: The observation dictionary.
        :return: The predicted value.
        """
        features = self.extract_features(obs)
        _, latent_vf = self.mlp_extractor(features)
        return self.value_net(latent_vf)