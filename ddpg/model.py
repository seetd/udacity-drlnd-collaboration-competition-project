import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F

def hidden_init(layer):
    fan_in = layer.weight.data.size()[0]
    lim = 1. / np.sqrt(fan_in)
    return (-lim, lim)

class Actor(nn.Module):
    """Actor (Policy) Model."""

    def __init__(self, config):
        """Initialize parameters and build model.
        Params
        ======
            config (dict)
                - "state_size": dimension of each state
                - "action_size": dimension of each action
                - "random_seed": random seed
                - "actor": actor specific config object
                    - "fc":  array of input sizes for hidden layers
        """
        super(Actor, self).__init__()
        seed = config["random_seed"]
        state_size = config["state_size"]
        action_size = config["action_size"]
        fc1_units = config["actor"]["fc"][0]
        fc2_units = config["actor"]["fc"][1]
        if seed is not None:
            torch.manual_seed(seed)
        self.fc1 = nn.Linear(state_size, fc1_units)
        self.bc1 = nn.BatchNorm1d(fc1_units)
        self.fc2 = nn.Linear(fc1_units, fc2_units)
        self.bc2 = nn.BatchNorm1d(fc2_units)
        self.fc3 = nn.Linear(fc2_units, action_size)
        self.reset_parameters()

    def reset_parameters(self):
        self.fc1.weight.data.uniform_(*hidden_init(self.fc1))
        self.fc2.weight.data.uniform_(*hidden_init(self.fc2))
        self.fc3.weight.data.uniform_(-3e-3, 3e-3)

    def forward(self, state):
        """Build an actor (policy) network that maps states -> actions."""
        x = F.relu(self.bc1(self.fc1(state)))
        x = F.relu(self.bc2(self.fc2(x)))
        return torch.tanh(self.fc3(x))


class Critic(nn.Module):
    """Critic (Value) Model."""

    def __init__(self, config):
        """Initialize parameters and build model.
        Params
        ======
            config (dict)
                - "state_size": dimension of each state
                - "action_size": dimension of each action
                - "random_seed": random seed
                - "critic": actor specific config object
                    - "fc":  array of input sizes for hidden layers
        """
        super(Critic, self).__init__()
        seed = config["random_seed"]
        state_size = config["state_size"]
        action_size = config["action_size"]
        fcs1_units = config["critic"]["fc"][0]
        fc2_units = config["critic"]["fc"][1]        
        if seed is not None:
            torch.manual_seed(seed)
        
        self.fcs1 = nn.Linear(state_size, fcs1_units)
        self.bc1 = nn.BatchNorm1d(fcs1_units)
        self.fc2 = nn.Linear(fcs1_units+action_size, fc2_units)
        self.bc2 = nn.BatchNorm1d(fc2_units)
        self.fc3 = nn.Linear(fc2_units, 1)
        self.reset_parameters()

    def reset_parameters(self):
        self.fcs1.weight.data.uniform_(*hidden_init(self.fcs1))
        self.fc2.weight.data.uniform_(*hidden_init(self.fc2))
        self.fc3.weight.data.uniform_(-3e-3, 3e-3)

    def forward(self, state, action):
        """Build a critic (value) network that maps (state, action) pairs -> Q-values."""
        xs = F.relu(self.bc1(self.fcs1(state)))
        x = torch.cat((xs, action), dim=1)
        x = F.relu(self.bc2(self.fc2(x)))
        return self.fc3(x)
