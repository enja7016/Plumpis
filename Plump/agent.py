from plump import PlumpGame 

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

    