import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from stealQueue import stealQueue
import random

# Define the DQN network
class DQN(nn.Module):
    def __init__(self, state_dim, action_dim):
        super(DQN, self).__init__() # batch x channelx w x... (32 x 16) 16
        self.fc1 = nn.Linear(state_dim, 64)
        self.bn1 = nn.BatchNorm1d(64)
        self.fc2 = nn.Linear(64, 64)
        self.fc21 = nn.Linear(64, 64)
        self.bn2 = nn.BatchNorm1d(64)
        self.fc3 = nn.Linear(64, action_dim)

    def forward(self, x):
        #x = torch.relu(self.bn1(self.fc1(x)))
        x = torch.relu(self.fc1(x))
        #x = torch.relu(self.bn2(self.fc2(x)))
        x = torch.relu(self.fc2(x))
        #x = torch.relu(self.fc21(x))
        x = self.fc3(x)
        return x # 8 x 2 x 3 = 48 

# Define the DQN agent
class DQNAgent:
    def __init__(self, state_dim, action_dim, lr, gamma, epsilon):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(self.device)
        self.policy_net = DQN(state_dim, action_dim).to(self.device)
        self.target_net = DQN(state_dim, action_dim).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=lr)
        self.loss_fn = nn.MSELoss()

    def act(self, state):
        # epsilon greedy is applied
        if np.random.rand() < self.epsilon:
            return np.random.randint(self.action_dim)
        state = torch.tensor(state, dtype=torch.float32).to(self.device)
        with torch.no_grad():
            q_values = self.policy_net(state)
        return torch.argmax(q_values).item()

    def train(self, replay_buffer, batch_size):
        if len(replay_buffer) < batch_size:
            return
        batch = replay_buffer.sample(batch_size)
        states, actions, rewards, next_states, dones = batch
        states = torch.tensor(states, dtype=torch.float32).to(self.device)
        actions = torch.tensor(actions, dtype=torch.int64).to(self.device)
        rewards = torch.tensor(rewards, dtype=torch.float32).to(self.device)
        next_states = torch.tensor(next_states, dtype=torch.float32).to(self.device)
        dones = torch.tensor(dones, dtype=torch.float32).to(self.device)
        q_values = self.policy_net(next_states)
        target_q_values = self.target_net(next_states)
        max_q_values = torch.max(target_q_values, dim=1)[0]
        target_q_values = rewards + (1 - dones) * self.gamma * max_q_values
        q_values = q_values.gather(dim=1, index=actions.unsqueeze(dim=1)).squeeze()
        loss = self.loss_fn(q_values, target_q_values)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        if len(replay_buffer) % 100 == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())
            
class ReplayBuffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self.buffer = []
        self.position = 0

    def add(self, state, action, reward, next_state, done):
        if len(self.buffer) < self.capacity:
            self.buffer.append(None)
        self.buffer[self.position] = (state, action, reward, next_state, done)
        self.position = (self.position + 1) % self.capacity

    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        return states, actions, rewards, next_states, dones

    def __len__(self):
        return len(self.buffer)

            
if __name__ == "__main__":
    env = stealQueue()
    state_dim = env.n_features
    action_dim = env.n_actions
    lr = 1e-3
    gamma = 0.99
    epsilon = 0.2
    agent = DQNAgent(state_dim, action_dim, lr, gamma, epsilon)
    replay_buffer = ReplayBuffer(10000)
    batch_size = 32
    num_episodes = 200 # should be 2000 here.
    for episode in range(num_episodes):
        state = env.reset()
        episode_reward = 0
        num_iter = 0
        while True:
            action = agent.act(state) # action space is , for wsq, 3x2x8
            next_state, reward, done = env.step(action)
            replay_buffer.add(state, action, reward, next_state, done)
            agent.train(replay_buffer, batch_size)
            state = next_state
            episode_reward += reward
            num_iter += 1
            if done:
                break
        print("Episode: {}, Reward: {}, num of iter: {}".format(episode, episode_reward, num_iter))
        print ("Total races discovered is ", str(len(env.discovered_dataraces)))