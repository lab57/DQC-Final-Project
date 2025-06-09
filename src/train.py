import os
import gymnasium as gym
import torch
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from stable_baselines3 import PPO, DQN
from stable_baselines3.common.monitor import Monitor
import gymnasium.wrappers

from quantum_env import QuantumCompilerEnv
from custom_policy import MaskableActorCriticPolicy
from q_network_wrapper import QNetworkWrapper # NEW: Import our wrapper

# plot_results function remains the same...

def main():
    parser = argparse.ArgumentParser(description="Train or Continue Training a DQC Compiler Agent")
    parser.add_argument("--algo", type=str, required=True, choices=["ppo", "ddqn"], help="RL algorithm to use")
    parser.add_argument("--timesteps", type=int, default=250000, help="Total training timesteps for this run")
    parser.add_argument("--load", type=str, default=None, help="Path to a saved model to continue training from")
    args = parser.parse_args()
    if torch.cuda.is_available():
        device = "cuda"
    elif torch.backends.mps.is_available():
        device = "mps"
    else:
        device = "cpu"
    print(f"Using device: {device}")
    
    log_dir = f"{args.algo}_dqc_logs/"
    os.makedirs(log_dir, exist_ok=True)

    # --- Environment Setup ---
    # Create the base environment first to get its properties
    base_env = QuantumCompilerEnv()
    
    # Get the number of actions for our wrapper
    num_actions = base_env.action_space.n

    env = gymnasium.wrappers.TimeLimit(base_env, max_episode_steps=2000)
    env = Monitor(env, log_dir, allow_early_resets=True)
    
    # FlattenObservation must be applied LAST for the wrapper to work correctly
    if args.algo == "ddqn":
        env = gymnasium.wrappers.FlattenObservation(env)

    # --- Agent Initialization or Loading ---
    model = None
    if args.load:
        # Loading is complex with this patch, focusing on creating a new model for now.
        # To continue training, you would load the model and then re-apply the patch.
        print("Loading models is not supported in this version of the script. Please create a new model.")
        return 
    else:
        print("Creating a new model...")
        if args.algo == "ppo":
            model = PPO(MaskableActorCriticPolicy, env, verbose=1, device=device,
                        tensorboard_log=f"./{args.algo}_dqc_tensorboard/",
                        policy_kwargs={'net_arch': [dict(pi=[140, 150], vf=[140, 150])]}
            )
        elif args.algo == "ddqn":
            dqn_params = {
                'learning_rate': 1e-5, 'buffer_size': 10000, 'learning_starts': 1000,
                'batch_size': 2560, 'tau': 0.001, 'gamma': 0.99,
                'train_freq': (5, 'step'), 'gradient_steps': 10,
                'exploration_fraction': 0.8, 'exploration_final_eps': 0.05,
                'policy_kwargs': {'net_arch': [140, 150]}
            }
            
            # Create the standard DQN model (it is DDQN by default)
            model = DQN("MlpPolicy", env, verbose=1, device=device,
                        tensorboard_log=f"./{args.algo}_dqc_tensorboard/", **dqn_params)
            
            # --- NEW: PATCH THE MODEL WITH OUR WRAPPER ---
            print("Patching the Q-network with action masking wrapper...")
            
            # Create an instance of our wrapper
            wrapped_q_net = QNetworkWrapper(model.q_net, env.observation_space)
            
            # Configure the wrapper with the dimensions
            # The mask dimension is the number of actions
            wrapped_q_net.mask_dim = num_actions
            # The main observation dimension is the total size minus the mask size
            wrapped_q_net.main_obs_dim = env.observation_space.shape[0] - num_actions
            
            # Replace the model's Q-network with our patched version
            model.q_net = wrapped_q_net
            # Also replace the target network for DDQN
            model.q_net_target = QNetworkWrapper(model.q_net_target, env.observation_space)
            model.q_net_target.mask_dim = num_actions
            model.q_net_target.main_obs_dim = env.observation_space.shape[0] - num_actions

    # --- Training ---
    print(f"Starting {args.algo.upper()} training on {device.upper()}...")
    model.learn(total_timesteps=args.timesteps, progress_bar=True, reset_num_timesteps=(not args.load))
    
    print("Training finished.")
    model_save_path = os.path.join(log_dir, f"{args.algo}_dqc_model.zip")
    model.save(model_save_path)
    print(f"Model saved to {model_save_path}")

    plot_results(log_dir, args.algo)

if __name__ == "__main__":
    main()