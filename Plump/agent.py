from plump import PlumpGame 
import numpy as np

class Agent:
    def __init__(self):
        ''' Initialize the round class

        Args:
            dealer (object): the object of UnoDealer
            num_players (int): the number of players in game
        '''
        self.state = PlumpGame.get_state() #TODO: Maybe dynamic id
        self.hand = self.state["hand"]
        self.guessed_sticks = self.state["guessed_sticks"]
        self.legal_actions = self.state["legal_actions"]
        
        self.state_size = 156  # Define properly based on your state encoding
        self.action_size = 52  # One for each card in a standard deck (adjust if needed)
        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 0.1
        self.Q = np.zeros((self.state_size, self.action_size))

    def choose_action(self, state):
        if np.random.rand() < self.epsilon:
            return np.random.randint(self.action_size)
        else:
            return np.argmax(self.Q[state])

    def update_Q(self, state, action, reward, next_state):
        best_next_action = np.argmax(self.Q[next_state])
        td_target = reward + self.gamma * self.Q[next_state][best_next_action]
        td_error = td_target - self.Q[state][action]
        self.Q[state][action] += self.alpha * td_error

    