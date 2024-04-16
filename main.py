import Plump
from Plump import PlumpGame as Game
from Plump import Player

def main():
    # Define game settings
    # Number of players
    # Number of cards
    Game.init_game()
    while not(Game.is_over()):
        Game.init_next_round()
        while not(Game.round_is_done()):
            current_player = Game.get_player_id()
            action = current_player.get_action()
            next_state = Game.step(action)
            print(next_state)
        # give reward
    get_scores()
    quit()