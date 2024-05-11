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
        
        # Stats:
        self.stats = {}
        self.stats["learned_actions"] = 0
        self.stats["exploration_actions"] = 0
        self.stats["plumps"] = 0

    def get_stats(self):
        return self.stats
    
    # state_to_index: given a state, return a unique index for that state
    def state_to_index(self, state):
        # Normalize the state dictionary
        # Convert cards on hand to a tuple of card hashes
        cards_on_hand = tuple(hash(card) for card in state["cards_on_hand"])
        
        # Convert guessed sticks to a tuple (None is hashable, so it's okay)
        guessed_sticks = tuple(state["guessed_sticks"])
        
        # Normalize won_sticks, ensure it's hashable
        won_sticks = hash(state["won_sticks"])

        # Create a composite hash of all components
        composite_state = (cards_on_hand, guessed_sticks, won_sticks)
        return hash(composite_state) % self.state_size

    # choose_action_card: given a state, return an action that represents which card to play
    def choose_action_card(self, state, deck_cards):
        state_index = self.state_to_index(state)
        
        # Choose a random card (explore):
        if np.random.rand() < self.epsilon:
            self.stats["exploration_actions"] += 1
            a = np.random.choice([i for i in range(len(state["cards_on_hand"]))])
            print(f"Agent is playing a random card")
            return a
        
        # Play the card with highest Q-value:
        else:
            # Get all possible actions based on the current hand
            valid_actions = []
            for idx, card in enumerate(state["cards_on_hand"]):
                for deck_idx, deck_card in enumerate(deck_cards):
                    if card == deck_card:
                        valid_actions.append((idx, self.Q[state_index][deck_idx]))
            # Choose the best valid action (has the highest Q value)
            valid_actions.sort(key=lambda x: x[1], reverse=True)  # Sort by Q value
            best_action = valid_actions[0][0]  # Take the index of the best action
            print(f"Agent is choosing a best valid action, index 0 in: {valid_actions}")
            self.stats["learned_actions"] += 1
            return best_action

    def choose_action_guess(self, state):
        state_index = self.state_to_index(state)
        
        # Guess randomly between 0-2 (explore):
        if np.random.rand() < self.epsilon:
            print(f"Agent is guessing randomly")
            return np.random.randint(3)
        
        # Choose the action with the highest Q-value:
        else:
            valid_actions_range = 3  # This defines the range of valid guesses (0-2)
            valid_q_values = self.Q[state_index][:valid_actions_range]  # Slice the Q-values to only consider valid actions
            best_action = np.argmax(valid_q_values)  # Find the index of the highest Q-value within the valid range
            print(f"Agent is choosing the best action based on Q-values: {valid_q_values}")
            return best_action

    # update_Q: given a state, the action taken in that state and the reward for ending up in next_state, update the Q matri
    # this should be called 'cards_on_hand' + 1 times in plump.py
    # EX (2 cards):
    
    # Guessing Phase         -->           1st card           -->        2nd card           -->        Reward
    #                                      update_Q(s0, a0, r=0, s1)     update_Q(s1, a1, r=0, s2)     update_Q(s2, a2, r=11, s3)
    # s0:            a0:                   s1:             a1:           s2:           a2:             s3:
    # hand: [x, y]   1                     hand: [x, y]    1             hand: [x]     0               hand: []
    # won: None                            won: 0                        won: 1                        won: 1
    # guessed_sticks: [None, None, None]   guessed_sticks: [1, 1, 1]     guessed_sticks: [1, 1, 1]     guessed_sticks: [1, 1, 1]          
    
    def update_Q(self, state, action, reward, next_state):
        state_index = self.state_to_index(state)
        next_state_index = self.state_to_index(next_state)
        best_next_action = np.argmax(self.Q[next_state_index])
        # Q learning equation 
        td_target = reward + self.gamma * self.Q[next_state_index][best_next_action]
        td_error = td_target - self.Q[state_index][action]
        self.Q[state_index][action] += self.alpha * td_error

    # eval_round: given the points for a round, calculate the reward
    # if plumped, no reward
    # otherwise, reward is proportionate to the amount of points
    def eval_round(self, points):
        reward = 0
        if points > 0:
            reward += points
        else: 
            self.stats["plumps"] += 1
        return reward
                

    