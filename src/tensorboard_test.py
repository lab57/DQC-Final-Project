# test_tensorboard.py
import gymnasium as gym
from stable_baselines3 import DQN

print("Creating a standard CartPole-v1 environment...")
env = gym.make("CartPole-v1")

print("Creating DQN model and logging to './cartpole_tensorboard_logs/'...")
model = DQN("MlpPolicy", env, verbose=1, tensorboard_log="./cartpole_tensorboard_logs/")

print("Starting training for 2000 steps...")
# We use 2000 steps to ensure multiple logs are written.
model.learn(total_timesteps=2000)

print("\nTraining complete.")
print("Log files should now be in the 'cartpole_tensorboard_logs' directory.")