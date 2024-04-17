class Round:
    def __init__(self,  num_players, np_random):
        ''' Initialize the round class

        Args:
            dealer (object): the object of UnoDealer
            num_players (int): the number of players in game
        '''
        self.np_random = np_random
        self.current_player = 0
        self.num_players = num_players
        self.played_cards = []
        self.is_over = False
        self.winner = None:
        