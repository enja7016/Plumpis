# from plump import PlumpGame 
import numpy as np

class Agent:
    def __init__(self):
        ''' Initialize the round class

        Args:
            dealer (object): the object of UnoDealer
            num_players (int): the number of players in game
        '''
        # self.state = state 
        # self.hand = self.state["hand"]
        # self.guessed_sticks = self.state["guessed_sticks"]
        # self.legal_actions = self.state["legal_actions"]
        
        # continously updated
        self.state  
        self.hand 
        self.guessed_sticks
        self.legal_actions
        
        self.state_size = 2652  # Define properly based on your state encoding
        self.action_size = 52  # One for each card in a standard deck (adjust if needed)
        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 0.1
        self.Q_cards = np.zeros((self.state_size, self.action_size))
        self.Q_guess = np.zeros((self.state_size, 3)) # TODO fix state size later on (now we have 2 cards)

    def update_agent_state(self, state):
        self.state = state
        self.hand = self.state["hand"]
        self.guessed_sticks = self.state["guessed_sticks"]
        self.legal_actions = self.state["legal_actions"]

    def choose_action_cards(self, state, cards_per_player, deck):
        if np.random.rand() < self.epsilon:
            return np.random.randint(cards_per_player)
        else:
            card_idx = np.argmax(self.Q[state]) # card_idx = index of the card to play
            card = deck[card_idx] # card = what card to play
            idx = 0
            for c in state["cards_on_hand"]:
                if (c.rank == card.rank and c.suit == card.suit):
                    return idx
                idx += 1

    def choose_action_guess(self, state):
        if np.random.rand() < self.epsilon:
            return np.random.randint(3)
        else:
            return np.argmax(self.Q_guess[state]) # gives best index of 0-2
         
    def update_Q_cards(self, state, action, reward, next_state):
        best_next_action = np.argmax(self.Q_cards[next_state])
        td_target = reward + self.gamma * self.Q_cards[next_state][best_next_action]
        td_error = td_target - self.Q_cards[state][action]
        self.Q_cards[state][action] += self.alpha * td_error

    def update_Q_guess(self, state, action, reward, next_state):
        best_next_action = np.argmax(self.Q_guess[next_state])
        td_target = reward + self.gamma * self.Q_guess[next_state][best_next_action]
        td_error = td_target - self.Q_guess[state][action]
        self.Q_guess[state][action] += self.alpha * td_error

    def eval_round(self, points, max_round_points):
        reward = 0
        # winner
        if points == max_round_points:  
            reward += 1
        # did not plump
        if points > 0:
            reward += points
        # lost
        else: 
            reward = -(max_round_points)
        
                

    