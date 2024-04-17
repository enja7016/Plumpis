class Player:

    def __init__(self, player_id, np_random):
        ''' Initialize a player class

        Args:
            player_id (int): id for the player
        '''
        self.np_random = np_random
        self.player_id = player_id
        self.hand = []
        self.score = 0
        self.bet = 0
        self.sticks = 0

    def get_player_id(self):
        ''' Return player's id
        '''
        return self.player_id
    
    def get_player_hand(self):
        ''' Return player's hand
        '''
        return self.hand
    
    def add_card(self, card):
        ''' Adds card to player's hand
        '''
        self.hand.append(card)