# from plump import PlumpGame 
import numpy as np

class Agent:
    def __init__(self):
       
        # self.state = state 
        # self.hand = self.state["hand"]
        # self.guessed_sticks = self.state["guessed_sticks"]
        # self.legal_actions = self.state["legal_actions"]
        
        # continously updated
        self.state = {} 
        self.legal_actions = []
        
        self.state_size = 7956  # Define properly based on your state encoding
        self.action_size = 55  # One for each card in a standard deck (adjust if needed)
        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 0.1
        self.Q = np.zeros((self.state_size, self.action_size))

    def state_to_index(self, state):
        # Encode your state to an index
        # You can use a hash function or any method that uniquely represents a state as an integer
        # For demonstration purposes, let's assume state is a list
        # You may need to define a proper hash function for your specific state representation
        return hash(tuple(state)) % self.state_size

    def choose_action_card(self, state, cards_per_player, deck_cards):
        state_index = self.state_to_index(state)
        if np.random.rand() < self.epsilon:
            # Choose a random valid action
            return np.random.choice([i for i in range(len(state["cards_on_hand"]))])
        else:
            # Get all possible actions based on the current hand
            valid_actions = []
            for idx, card in enumerate(state["cards_on_hand"]):
                for deck_idx, deck_card in enumerate(deck_cards):
                    if card == deck_card:
                        valid_actions.append((idx, self.Q[state_index][deck_idx]))

            # Choose the best valid action (has the highest Q value)
            if valid_actions:
                valid_actions.sort(key=lambda x: x[1], reverse=True)  # Sort by Q value
                best_action = valid_actions[0][0]  # Take the index of the best action
                return best_action

        # If no valid actions found, default to random choice (fallback)
        return np.random.choice([i for i in range(len(state["cards_on_hand"]))])


    def choose_action_guess(self, state):
            state_index = self.state_to_index(state)
            if np.random.rand() < self.epsilon:
                return np.random.randint(2)
            else:
                return np.argmax(self.Q[state_index]) # gives best index of 0-2


    def update_Q(self, state, action, reward, next_state):
        state_index = self.state_to_index(state)
        next_state_index = self.state_to_index(next_state)
        best_next_action = np.argmax(self.Q[next_state_index])
        td_target = reward + self.gamma * self.Q[next_state_index][best_next_action]
        td_error = td_target - self.Q[state_index][action]
        self.Q[state_index][action] += self.alpha * td_error


    def eval_round(self, points):
        reward = 0
        if points > 0:
            reward += points
        return reward
                

    