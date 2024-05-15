# from plump import PlumpGame 
import numpy as np
import logging
import copy

# Create q-value logs
# use q_logger.info("") to log something
q_logger = logging.getLogger('q_logger')
q_logger.setLevel(logging.DEBUG)
q_handler = logging.FileHandler('q_values.log', mode='w')
q_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
q_handler.setFormatter(q_formatter)
q_logger.addHandler(q_handler)

class Agent:
    def __init__(self):
        self.state_size = 7956  # Define properly based on your state encoding
        self.action_size = 55  # One for each card in a standard deck (adjust if needed)
        self.alpha = 0.2   # modified: 0.1 before. just for experiment.
        self.gamma = 0.95
        self.epsilon = 0.1
        #self.Q = np.zeros((self.state_size, self.action_size))
        self.Q = {}
        self.found_state = 0
        # Stats:
        self.stats = {}
        self.stats["learned_actions"] = 0
        self.stats["exploration_actions"] = 0
        self.stats["plumps"] = 0
    
    def get_stats(self):
        return self.stats

    # Logging q values. Creates a file called q_values.log. Gets replaced when program is re-run.
    def log_q_values(self, state, action, q_value_before, reward, q_value_after, next_state, state_idx):
        # Determine if the action is a card or a guess
        if state["won_sticks"] == None:
            action_description = action
        else:
            action_description = self.idx_to_card(action)
        q_logger.info(f"\nState: {self.state_to_str(state)}\nAction: {action_description}, Reward: {reward}\nQ-Value before update: {q_value_before}, Q-Value after update: {q_value_after}")
    
    # for logging.
    def idx_to_card(self, card_idx):
        rank_order = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suit_order = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        num_ranks = len(rank_order)
        suit_index = card_idx // num_ranks
        rank_index = card_idx % num_ranks
        suit = suit_order[suit_index]
        rank = rank_order[rank_index]
        return f"{rank} {suit}"
    
    # for logging.
    def state_to_str(self, state):
        cards_on_hand = ', '.join(str(card) for card in state["cards_on_hand"])
        guessed_sticks = ', '.join(str(g) for g in state["guessed_sticks"])
        #guessed_sticks = str(state["guessed_sticks"])
        won_sticks = state["won_sticks"] if state["won_sticks"] is not None else 'None'
        return f"Hand: [{cards_on_hand}], Guessed Sticks: [{guessed_sticks}], Won Sticks: {won_sticks}"

    # for hashing attempts. did not work though.
    def card_to_index(self, card):
        rank_order = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suit_order = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        rank_index = rank_order.index(card.rank)
        suit_index = suit_order.index(card.suit)
        return suit_index * len(rank_order) + rank_index  

    def state_to_dict_key(self, state):
        ret_string = self.state_to_str(state)
        self.chk_new_state(ret_string)
        return ret_string
        
    def chk_new_state(self, state_index):
        if state_index not in self.Q.keys():
            self.Q[state_index] = [0] * self.action_size
        else:
            self.found_state += 1
        
    # choose_action_card: given a state, return an action that represents which card to play
    def choose_action_card(self, state, deck_cards):
        state_index = self.state_to_dict_key(state)
    
        # Choose a random card (explore):
        if np.random.rand() < self.epsilon:
            self.stats["exploration_actions"] += 1
            a = np.random.choice([i for i in range(len(state["cards_on_hand"]))])
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
            self.stats["learned_actions"] += 1
            return best_action

    def choose_action_guess(self, state):
        state_index = self.state_to_dict_key(state)
        
        # Guess randomly between 0-2 (explore):
        if np.random.rand() < self.epsilon:
            #print(f"Agent is guessing randomly")
            return np.random.randint(3)
        
        # Choose the action with the highest Q-value:
        else:
            valid_actions_range = 3  # This defines the range of valid guesses (0-2)
            valid_q_values = self.Q[state_index][:valid_actions_range]  # Slice the Q-values to only consider valid actions
            if all(x == valid_q_values[0] for x in valid_q_values):
                return np.random.randint(3)
            best_action = np.argmax(valid_q_values)  # Find the index of the highest Q-value within the valid range
            #print(f"Agent is choosing the best action based on Q-values: {valid_q_values}")
            return best_action

    # update_Q: given a state, the action taken in that state and the reward for ending up in next_state, update the Q matri
    # this should be called 'cards_on_hand' + 1 times in plump.py
    # EX (2 cards):
    
    # Guessing Phase         -->           1st card           -->        2nd card           -->        Reward
    #                                      update_Q(s0, a0, r=0, s1)     update_Q(s1, a1, r=0, s2)     update_Q(s2, a2, r=1, s3)
    # s0:            a0:                   s1:             a1:           s2:           a2:             s3:
    # hand: [x, y]   1                     hand: [x, y]    1             hand: [x]     0               hand: []
    # won: None                            won: 0                        won: 1                        won: 1
    # guessed_sticks: [None, None, None]   guessed_sticks: [1, 1, 1]     guessed_sticks: [1, 1, 1]     guessed_sticks: [1, 1, 1]          
    
    def update_Q(self, state, action, reward, next_state):
        state_index = self.state_to_dict_key(state)
        q_val_before = copy.deepcopy(self.Q[state_index][action])  # for logging
        
        next_state_index = self.state_to_dict_key(next_state)
        best_next_action = np.argmax(self.Q[next_state_index])
        # Q learning equation 
        td_target = reward + self.gamma * self.Q[next_state_index][best_next_action]
        td_error = td_target - self.Q[state_index][action]
        self.Q[state_index][action] += self.alpha * td_error
        
        # logging
        self.log_q_values(state, action, q_val_before, reward, self.Q[state_index][action], next_state, state_index)

    # eval_round: given the points for a round, calculate the reward
    # if plumped, no reward
    # otherwise, reward is proportionate to the amount of points
    def eval_round(self, points):
        reward = 0
        if points > 0:
            reward += 1         # modified: the reward was really big before. tried to balance a bit more.
            if points >= 11:
                reward += 0.1
            if points == 12:
                reward += 0.1
        else: 
            self.stats["plumps"] += 1
            reward -= 0.1       # small punishment. just for experiment. 
        return reward
