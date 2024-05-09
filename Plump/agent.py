# from plump import PlumpGame 
import numpy as np

class Agent:
    def __init__(self):
        
        self.state_size = 7956  # Define properly based on your state encoding
        self.action_size = 55  # One for each card in a standard deck (adjust if needed)
        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 0.1
        self.Q = np.zeros((self.state_size, self.action_size))
        
        self.stats = {}
        self.stats["learned_actions"] = 0
        self.stats["fallback_actions"] = 0
        self.stats["exploration_actions"] = 0

    def get_stats(self):
        return self.stats
    
    def state_to_index(self, state):
        # Encode your state to an index
        # You can use a hash function or any method that uniquely represents a state as an integer
        # For demonstration purposes, let's assume state is a list
        # You may need to define a proper hash function for your specific state representation
        return hash(tuple(state)) % self.state_size

    def choose_action_card(self, state, deck_cards):
        state_index = self.state_to_index(state)
        if np.random.rand() < self.epsilon:
            self.stats["exploration_actions"] += 1
            # Choose a random valid action
            a =  np.random.choice([i for i in range(len(state["cards_on_hand"]))])
            print(f"Agent is choosing a random card to play: {a}")
            return a
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
                print(f"Agent is choosing a best valid action, index 0 in: {valid_actions}")
                self.stats["learned_actions"] += 1
                return best_action

        # If no valid actions found, default to random choice (fallback)
        b = np.random.choice([i for i in range(len(state["cards_on_hand"]))])
        self.stats["fallback_actions"] += 1
        print(f"Agent did not find a valid action, and falls back on random action: {b}")
        return b


    def choose_action_guess(self, state):
            state_index = self.state_to_index(state)
            if np.random.rand() < self.epsilon:
                print(f"Agent is guessing randomly")
                return np.random.randint(3)
            else:
                print("Agent is choosing the best action in: {self.Q[state_index]}")
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
                

    