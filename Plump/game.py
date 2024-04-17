from copy import deepcopy
import numpy as np

from Plump import Player
from card import Card
from Plump import Round

class PlumpGame:

    def __init__(self, num_cards=2, num_players=3):
        ''' Initialize the class Plump Game
        '''
        self.np_random = np.random.RandomState()
        self.num_cards = num_cards
        self.num_players = num_players
        self.bets = []
        self.scores = 0

    def configure(self, game_config):
        ''' Specifiy some game specific parameters, such as number of players
        '''
        self.num_cards = game_config['num_cards']

    def shuffle(self):
        ''' Shuffle the deck
        '''
        shuffle_deck = np.array(Card.init_standard_deck())
        self.np_random.shuffle(shuffle_deck)
        self.deck = list(shuffle_deck)
        
    def deal_card(self, player: Player):
        ''' Distribute one card to the player

        Args:
            player_id (int): the target player's id
        '''
        idx = self.np_random.choice(len(self.deck))
        card = self.deck[idx]
        card = self.deck.pop()
        player.hand.append(card)

    # Init for game round
    def init_game(self):
        ''' Initialilze the game

        Returns:
            state (dict): the first state of the game
            player_id (int): current player's id
        '''

        # List of players
        self.players = []
        for i in range(self.num_players):
            self.players.append(Player(i, self.np_random))

        # Deal cards to players
        for i in range(self.num_cards):
            for j in range(self.num_players):
                self.deal_card(self.players[j])

        # Keep track of turn
        self.game_pointer = 0

        return self.get_state(self.game_pointer), self.game_pointer

    def bet(self, bet):
        self.bets.append(bet)

    def init_next_round(self):
        for i in range(self.num_cards):
            for j in range(self.num_players):
                self.deal_card(self.players[j])
        self.bet()

    def step(self, action):
        ''' Get the next state

        Args:
            action (str): A specific action

        Returns:
            (tuple): Tuple containing:

                (dict): next player's state
                (int): next plater's id
        '''

        self.round.proceed_round(self.players, action)
        player_id = self.round.current_player
        state = self.get_state(player_id)
        return state, player_id

    def get_num_players(self):
        ''' Return the number of players in blackjack

        Returns:
            number_of_player (int): blackjack only have 1 player
        '''
        return self.num_players

    def get_num_actions(self):
        ''' Return the number of applicable actions

        Returns:
            number_of_actions (int): there are only two actions (hit and stand)
        '''
        return self.num_cards

    def get_player_id(self):
        ''' Return the current player's id

        Returns:
            player_id (int): current player's id
        '''
        return self.game_pointer

    def get_state(self, player_id):
        ''' Return player's state

        Args:
            player_id (int): player id

        Returns:
            state (dict): corresponding player's state
        '''
        '''
                before change state only have two keys (action, state)
                but now have more than 4 keys (action, state, player0 hand, player1 hand, ... , dealer hand)
                Although key 'state' have duplicated information with key 'player hand' and 'dealer hand', I couldn't remove it because of other codes
                To remove it, we need to change dqn agent too in my opinion
                '''
        state = {}
        state['actions'] = ('hit', 'stand')
        hand = [card.get_index() for card in self.players[player_id].hand]
        if self.is_over():
            dealer_hand = [card.get_index() for card in self.dealer.hand]
        else:
            dealer_hand = [card.get_index() for card in self.dealer.hand[1:]]

        for i in range(self.num_players):
            state['player' + str(i) + ' hand'] = [card.get_index() for card in self.players[i].hand]
        state['dealer hand'] = dealer_hand
        state['state'] = (hand, dealer_hand)

        return state

    def is_over(self):
        ''' Check if the game is over

        Returns:
            status (bool): True/False
        '''
        '''
                I should change here because judger and self.winner is changed too
                '''
        for i in range(self.num_players):
            if self.winner['player' + str(i)] == 0:
                return False

        return True