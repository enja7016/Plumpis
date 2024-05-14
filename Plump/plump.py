import random
from bot import Bot
from agent import Agent
import copy
import logging

# Create game logs
# use game_logger.info("") to log something
game_logger = logging.getLogger('game_logger')
game_logger.setLevel(logging.DEBUG)  # Set the minimum logging level
game_handler = logging.FileHandler('games.log', mode='w')  # Create a file handler
game_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')  # Create a formatter
game_handler.setFormatter(game_formatter)  # Set the formatter for the handler
game_logger.addHandler(game_handler)  # Add the handler to the logger

# Class defining a card with suit and rank
class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.rank} {self.suit}"
    
    def __lt__(self, other):
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        return ranks.index(self.rank) > ranks.index(other.rank)
    def __eq__(self, other):
        return self.suit == other.suit and self.rank == other.rank

    def __hash__(self):
        return hash((self.rank, self.suit))
    
    
# Class defining a deck of cards, one card of each type (52 cards)
class Deck:
    def __init__(self):
        self.cards = []
        self.build()

    # Fill the list of cards
    def build(self):
        self.cards = [] 
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        for suit in suits:
            for rank in ranks:
                self.cards.append(Card(suit, rank))

    # Shuffle the cards in a random order
    def shuffle(self):
        random.shuffle(self.cards)

    # Deal the top card if there are any cards left
    def deal_card(self):
        if len(self.cards) > 0:
            return self.cards.pop()
        else:
            return None
        
    # Get a card's index in (unshuffled) deck
    def get_card_index(self, card):
        rank_order = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suit_order = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        rank_index = rank_order.index(card.rank)
        suit_index = suit_order.index(card.suit)
        return suit_index * len(rank_order) + rank_index  
    
    # Rebuild and shuffle the deck
    def reset_deck(self):
        self.build()  
        self.shuffle()  
    
    

# Class defining a player with name, hand of cards, and guessed stick
class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.guessed_stick = 0

    # Add card to hand
    def add_card(self, card):
        self.hand.append(card)

    # Play the chosen card from hand if it exists
    def play_card(self, card_index):
        if 0 <= card_index < len(self.hand):
            return self.hand.pop(card_index)
        else:
            return None

    # Set a player's guess 
    def set_guess(self, guessed_stick):
        self.guessed_stick = guessed_stick

# Class defining the game of plump with deck, players, and stick
class PlumpGame:
    def __init__(self, players_count, cards_count, num_rounds):
        # Deck things
        self.deck = Deck()          # playing deck
        self.deck.shuffle()
        self.deck_ordered = Deck()  # reference, unshuffled deck
        
        # Player things
        self.players = [Player(f"Player {i}") for i in range(players_count)]    # players[0] = Player 0 (agent)
        self.points = [0 for i in range(players_count)]                         # points[0] = Player 0's points
        self.winner_of_stick = []                                               # winner_of_stick[0] = 1, means player 1 won stick 0
        self.played_cards = []                                                  # played_cards[0] = (Card, Player 0), which card Player 0 played
        self.human_player = 0                                                   # play vs human?
        
        # Game setting things
        self.players_count = players_count      # how many players
        self.cards_per_player = cards_count     # how many cards in a stick
        self.num_rounds = num_rounds             # number of rounds to play
        
        # Counters
        self.curr_round = 0             # keeping track of the rounds
        self.current_player_index = 0   # keeping track of who's turn it is
        
        # Agent things
        self.agent = Agent()
        self.previous_state = None          # for update_Q
        self.previous_action = None         
        self.first_after_guess = True       
        self.is_last_stick = (len(self.winner_of_stick) == self.cards_per_player)

    # Deal number of cards to each player from the deck
    def deal_cards(self):
        for _ in range(self.cards_per_player):
            for player in self.players:
                card = self.deck.deal_card()
                if card:
                    player.add_card(card)
    
    # Each player guess how many sticks they will win:
    def guess_sticks(self):
        self.first_after_guess = True      # for Q update things
        # save (s0, a0) for Q update later   
        s0 = self.get_first_state()
        self.previous_state = copy.deepcopy(s0)                
        self.previous_action = self.agent.choose_action_guess(s0)
        if self.human_player:
            print("GUESSING PHASE")
            print(f"Agent guessed: {self.previous_action}")
            self.players[0].set_guess(self.previous_action)     # set agent's guess
            print(f"Your cards are: {[str(card) for card in self.players[1].hand]}")
            human_guess = int(input("How many sticks do you think you will win? "))
            self.players[1].set_guess(human_guess)
            print(f"You guessed: {human_guess}")
            player = self.players[2]
            bot = Bot(player.hand)
            bot.set_guess()
            player.set_guess(bot.guessed_sticks)
            print(f"Bot guessed: {player.guessed_stick}")
        else: 
            game_logger.info(f"\n       Agent's hand is: {[str(card) for card in self.players[0].hand]}\n       Agent guessed: {self.previous_action}")
            self.players[0].set_guess(self.previous_action)     # set agent's guess
            # bots turn
            for player in self.players[1:]:                     
                bot = Bot(player.hand)
                bot.set_guess()
                player.set_guess(bot.guessed_sticks)
                game_logger.info(f"\n       {player.name} guessed {player.guessed_stick} sticks.")

    # Get first state
    def get_first_state(self):
        state = {}
        state["cards_on_hand"] = self.players[0].hand
        state["guessed_sticks"] = [None, None, None]
        state["won_sticks"] = None
        return state
    
    # Get state 
    def get_state(self):
        state = {}
        state["cards_on_hand"] = self.players[0].hand
        state["guessed_sticks"] = []
        for player in self.players:
            state["guessed_sticks"].append(player.guessed_stick)
        #state["guessed_sticks"] = self.players[0].guessed_stick

        # Check how many times the agent won a stick
        wins = 0
        for p in self.winner_of_stick:
            if p.name == "Player 0":
                wins += 1
        state["won_sticks"] = wins
        return state

    # Play a stick
    def play_stick(self):
        
        if self.first_after_guess:      # means we are in s1
            # update_Q(s0, a0, 0, s1)
            self.agent.update_Q(self.previous_state, self.previous_action, 0, self.get_state())
            self.first_after_guess = False
            
        # choose card:
        card_index = self.agent.choose_action_card(self.get_state(), self.deck_ordered.cards)
        self.previous_state = copy.deepcopy(self.get_state())      # save state (could be s1 or s2)
        agent_hand = [str(card) for card in self.players[0].hand]
        
        # play the card:
        played_card = self.players[0].play_card(card_index)
        self.played_cards.append((played_card, 0))
        if self.human_player: 
            print("PLAY FOR STICKS PHASE")
        else: game_logger.info(f"\n       Agent's hand is: {agent_hand}\n       Agent played: {played_card}")
        
        # get deck index of the played card
        deck_index = self.deck.get_card_index(played_card)     
        self.previous_action = deck_index                          # save action (corresponds to the index of the played card in ordered deck)
        # Q-update for s1 -> s2 happens in resolve_stick()
        # Q-update for s2 -> s3 happens in end_round(), since reward should be given 
        if self.human_player:
            print(f"Agent played: {played_card}")
            self.current_player_index += 1
            print(f"Your cards are: {[str(card) for card in self.players[1].hand]}")
            human_card = int(input(("Which card do you want to play (index 0-1)? ")))
            while human_card < 0 or human_card >= len(self.players[1].hand):
                print("Invalid card index. Try again.")
                human_card = int(input(("Which card do you want to play (index 0-1)? ")))
            played_card = self.players[1].play_card(human_card)
            self.played_cards.append((played_card, self.current_player_index))
            print(f"You played: {played_card}")
            self.current_player_index += 1
            # Get current player from index:
            current_player = self.players[self.current_player_index]
            bot = Bot(current_player.hand)
            bot.update_cards(current_player.hand, self.played_cards)
            card_index = bot.choose_action_bot()
            # Play chosen card:
            played_card = current_player.play_card(card_index)
            print(f"Bot played: {played_card}")
            self.current_player_index = 0
        else: 
            # Go to next player:
            self.current_player_index += 1
            # For each player:
            curr_player = 1
            
            while curr_player < self.players_count:
                # Get current player from index:
                current_player = self.players[self.current_player_index]
                bot = Bot(current_player.hand)
                bot.update_cards(current_player.hand, self.played_cards)
                card_index = bot.choose_action_bot()
                # Play chosen card:
                played_card = current_player.play_card(card_index)
                # Add played card and player index to stick:
                if played_card:
                    game_logger.info(f"\n       {current_player.name} played {str(played_card)}")
                    self.played_cards.append((played_card, self.current_player_index))
                    # Go to next player:
                    self.current_player_index = (self.current_player_index + 1) % len(self.players)
                    curr_player += 1
                else:
                    print("Invalid card index. Try again.")

    # Resolve stick
    def resolve_stick(self):
        
        # Find winning card and its player index:
        winning_card, winning_player_index = self.highest_card(self.played_cards)
        # Get winning player:
        winning_player = self.players[winning_player_index]
        # Add winner to stick:
        self.winner_of_stick.append(winning_player)
        if self.human_player:
            print("Resolving stick...")
            winner = ""
            if winning_player.name == "Player 0":
                winner = "Agent"
            if winning_player.name == "Player 1":
                winner = "You"
            if winning_player.name == "Player 2": 
                winner = "Bot"
            print(f"{winner} wins the stick with {winning_card}")
        else: game_logger.info(f"\n       {winning_player.name} wins the stick with {winning_card}")
      
        # Reset current stick:
        self.played_cards = []
        

    # Method to find the highest ranked card in a list of cards
    def highest_card(self, cards):
        highest_rank = -1
        highest_index = None
        for i, (card, player_index) in enumerate(cards):
            rank_value = self.rank_value(card.rank)
            if rank_value > highest_rank:
                highest_rank = rank_value
                highest_index = i
        return cards[highest_index]

    # Method to assign a numerical value to each rank
    def rank_value(self, rank):
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        return ranks.index(rank)

    # Ending the round
    def end_round(self):
        if self.human_player:
            print(f"Round {self.curr_round} over!")
        else: game_logger.info(f"\n   Round {self.curr_round} over!")
        # Count the number of sticks won by each player
        stick_counts = {player.name: 0 for player in self.players}
        for player in self.winner_of_stick:
            stick_counts[player.name] += 1
            
        player_idx = 0
        # Check if guessed number of wins matches actual number of wins for each player
        max_round_points = 0
        points_to_player = 0
        agent_points = 0
        for player in self.players:
            if player.guessed_stick == stick_counts[player.name]:
                if player.guessed_stick == 0:
                    points_to_player = 0
                    self.points[player_idx] += 5
                    points_to_player = 5
                else: 
                    self.points[player_idx] += player.guessed_stick+10
                    points_to_player = player.guessed_stick+10
            else:
                points_to_player = 0
            if self.human_player:
                name = ""
                if player.name == "Player 0":
                    name = "Agent"
                if player.name == "Player 1":
                    name = "You"
                if player.name == "Player 2":
                    name = "Bot"
                print(f"{name} guessed {player.guessed_stick} sticks and won {stick_counts[player.name]} sticks.\n Points: {points_to_player}")
            else: game_logger.info(f"\n       {player.name} guessed {player.guessed_stick} sticks and won {stick_counts[player.name]} sticks.\n       Points: {points_to_player}")
            
            if (player_idx == 0):  # agent's points
                    agent_points = points_to_player
            # get winner of round:
            if points_to_player > max_round_points:
                max_round_points = points_to_player
            player_idx += 1
        
        reward = self.agent.eval_round(agent_points) # calculate reward
        # update_Q(s2, a2, r=points, s3)
        self.agent.update_Q(self.previous_state, self.previous_action, reward, self.get_state())
        # reset state and action
        self.previous_state = None
        self.previous_action = None
        self.curr_round += 1
      
    # reset the game after a round (only player points and agent remains)
    def reset(self):
        self.deck.reset_deck()
        self.winner_of_stick = []
        self.played_cards = []
        self.current_player_index = 0
        self.previous_state = None
        self.previous_action = None
    
    def end_game(self):
        if self.human_player:
            print("GAME OVER!")
        else: game_logger.info(f"\nGAME OVER!")
        player_idx = 0
        winner = 0
        max_player_points = 0
        for player in self.players:
            if self.human_player:
                if player.name == "Player 0":
                    name = "Agent"
                if player.name == "Player 1":
                    name = "You"
                if player.name == "Player 2":
                    name == "Bot"
                print(f"{name} score was {self.points[player_idx]}")
            else: game_logger.info(f"\n{player.name}'s score was {self.points[player_idx]}")
            if self.points[player_idx] > max_player_points:
                max_player_points = self.points[player_idx]
                winner = player.name
            player_idx += 1
        if self.human_player:
            if winner == " Player 0":
                    name = "Agent"
            if winner == " Player 1":
                    name = ""
            if winner == "Player 2":
                    name == " Bot"
            print(f"Congratulations{winner}, you won the game Plump!")
        else: game_logger.info(f"\nContratulations {winner}, you won the game Plump!")
    
    # clear after all rounds (num_rounds) has been played, only agent remains
    def clear(self):
        self.reset()
        self.curr_round = 0
        self.points = [0 for i in range(self.players_count)]
        
def train(game, num_games):
    # Number of players and cards per player   
    agent_plumps = []
    game_logger.info(f"\nTraining for 3 players with {game.cards_per_player} cards each, for {num_games} games with {game.num_rounds} rounds.")
    
    curr_game = 0
    while curr_game < num_games:
        game_logger.info(f"\nGAME {curr_game}")
        while game.curr_round < game.num_rounds: 
            # Start round
            game_logger.info(f"\n   Round {game.curr_round}")
            # Deal cards
            game.deal_cards()
            # Guessing phase
            game.guess_sticks()                                     # s0, a0
            while len(game.winner_of_stick) < game.cards_per_player-1:
                # Play one stick (= all players play a card)
                game.play_stick()                                   # update_Q(s0, a0, 0, s1)
                # Get result from stick (= who won the stick):
                game.resolve_stick()                               
                # update_Q(s1, a1, 0, s2)
                game.agent.update_Q(game.previous_state, game.previous_action, 0, game.get_state())
                
            game.play_stick()                                   
            game.resolve_stick()
            game.end_round()        # update_Q(s2, a2, pts, s3)
            game.reset()
        game.end_game()
        game.clear()
        curr_game += 1
        stats = game.agent.get_stats()
        agent_plumps.append(stats["plumps"])
        game.agent.stats["plumps"] = 0
        
    agent_stats = game.agent.get_stats()
    # Empty list to store the averages
    averages = []

    # Iterate over the large list in steps of 1000
    for i in range(0, len(agent_plumps), 100):
        # Extract the sublist
        sublist = agent_plumps[i:i+100]
        
        # Calculate the average of the sublist
        average = sum(sublist) / len(sublist)

        # Append the average to the list of averages
        averages.append(average)
   
    print("Averages of each 100-interval sublist:", averages)
    
    print(f"Agent stats: ")
    print(f"Learned actions taken: {agent_stats['learned_actions']}")
    print(f"Exploration actions taken: {agent_stats['exploration_actions']}")

def play(game):
    # Start round
    while game.curr_round < game.num_rounds: 
        print(f"Round {game.curr_round}")
        # Deal cards
        game.deal_cards()
        # Guessing phase
        game.guess_sticks()                                     # s0, a0
        while len(game.winner_of_stick) < game.cards_per_player-1:
            # Play one stick (= all players play a card)
            game.play_stick()                                   # update_Q(s0, a0, 0, s1)
            # Get result from stick (= who won the stick):
            game.resolve_stick()                               
            # update_Q(s1, a1, 0, s2)
            game.agent.update_Q(game.previous_state, game.previous_action, 0, game.get_state())
                
        game.play_stick()                                   
        game.resolve_stick()
        game.end_round()        # update_Q(s2, a2, pts, s3)
        game.reset()
        
    game.end_game()
    game.clear()

def main():
    print("Hello! Welcome to Plumpis, a reinforcement learning model for the card game Plump.")
    players_count = 3
    num_cards = 2
    num_rounds = 10
    print(f"Initializing game with {players_count}players, {num_cards} cards each, {num_rounds} per game.")
    game = PlumpGame(players_count, num_cards, num_rounds)
    cmd = 0
    while cmd != 3:
        cmd = int(input("What would you like to do? \n  1: Train \n  2: Play \n  3: Quit\n"))
        if cmd == 1: 
            game.human_player = 0
            print("Preparing to train the agent...")
            num_games = int(input("  How many games should the agent train on? "))
            print("Training...")
            train(game, num_games)
        if cmd == 2:
            game.human_player = 1
            print("Play one game vs the agent and one bot!")
            play(game)
            
        if cmd == 3:
            quit()
        else:
            print("Invalid command! Try again.")
    

if __name__ == '__main__':
    main()



