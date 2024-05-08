import random
from bot import Bot
from agent import Agent

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
        
    def reset_deck(self):
        self.build()  # Rebuilds the deck from scratch
        self.shuffle()  # Shuffles the new deck

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
    def __init__(self, players_count, cards_count):
        self.deck = Deck()
        self.agent = Agent()
        self.deck.shuffle()
        self.players_count = players_count
        self.players = [Player(f"Player {i}") for i in range(players_count)]
        # winner_of_stick[0] = 1, means player 1 won stick 0
        self.winner_of_stick = []
        # played_cards[0] = (Card, Player 0)
        self.played_cards = []
        # current_player_index = who's turn
        self.current_player_index = 0
        self.cards_per_player = cards_count
        # points[0] = Player 0's points
        self.points = [0 for i in range(players_count)]
        # The number of rounds to play, hardcoded to 1 atm
        self.num_rounds = 100
        self.curr_round = 0
        
        self.previous_state = None
        self.previous_action = None
    
    # Start a new game:
    def start_game(self):
        print(f"Round {self.num_rounds}")
        self.deal_cards()
        self.guess_sticks()
        for player in self.players[1:]:
            print(f"{player.name} guessed {player.guessed_stick} sticks.")
        self.play_stick()


    # Deal number of cards to each player from the deck
    def deal_cards(self):
        for _ in range(self.cards_per_player):
            for player in self.players:
                card = self.deck.deal_card()
                if card:
                    player.add_card(card)
    
    # Each player guess how many sticks they will win:
    def guess_sticks(self):
        print(f"Agent's hand is:", [str(card) for card in self.players[0].hand])
        self.previous_action = self.agent.choose_action_guess(self.get_first_state())
        print(f"Agent guessed: {self.previous_action}")
        self.players[0].set_guess(self.previous_action)
        self.previous_state = self.get_first_state()
        
        for player in self.players[1:]:
            bot = Bot(player.hand)
            bot.set_guess()
            player.set_guess(bot.guessed_sticks)

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

        # Check how many times the agent won a stick
        wins = 0
        for p in self.winner_of_stick:
            if p == 0:
                wins += 1
        state["won_sticks"] = wins
        return state

    # Play a stick
    def play_stick(self):
        # Agent always start
        # Update Q from previous state, with the action that led to this state:
        self.agent.update_Q(self.previous_state, self.previous_action, 0, self.get_state())
        print("Agent's hand is:", [str(card) for card in self.players[0].hand])
        # Choose card:
        card_index = self.agent.choose_action_card(self.get_state(), self.cards_per_player, self.deck.cards)
        print(f"Agent chose action: {card_index}")
        
        self.previous_action = card_index
        self.previous_state = self.get_state()
        
        # Play the card:
        played_card = self.players[0].play_card(card_index)
        self.played_cards.append((played_card, 0))
        # Go to next player:
        self.current_player_index += 1
        # For each player:
        curr_player = 1
        while curr_player < self.players_count:
            # Get current player from index:
            current_player = self.players[self.current_player_index]
            print(f"{current_player.name} played:")
            bot = Bot(current_player.hand)
            bot.update_cards(current_player.hand, self.played_cards)
            card_index = bot.choose_action_bot()
            # Play chosen card:
            played_card = current_player.play_card(card_index)
            # Add played card and player index to stick:
            if played_card:
                print(played_card)
                self.played_cards.append((played_card, self.current_player_index))
                # Go to next player:
                self.current_player_index = (self.current_player_index + 1) % len(self.players)
                curr_player += 1
            else:
                print("Invalid card index. Try again.")
        # Get result from stick:
        self.resolve_stick()

    # Resolve stick
    def resolve_stick(self):
        # Find winning card and its player index:
        winning_card, winning_player_index = self.highest_card(self.played_cards)
        # Get winning player:
        winning_player = self.players[winning_player_index]
        # Add winner to stick:
        self.winner_of_stick.append(winning_player)
        print("-----------------------------")
        print(f"{winning_player.name} wins the stick with {winning_card}")
        print("-----------------------------")
        # Reset current stick:
        self.played_cards = []
        if len(self.winner_of_stick) < self.cards_per_player:
            self.play_stick()
        else:
            self.end_round()

    # Method to find the highest ranked card in a list of cards
    def highest_card(self, cards):
        highest_rank = 0
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

    # Ending the game
    def end_round(self):
        print("Round Over!")
        
        # Count the number of sticks won by each player
        stick_counts = {player.name: 0 for player in self.players}
        for player in self.winner_of_stick:
            stick_counts[player.name] += 1
            
        player_idx = 0
        # Check if guessed number of wins matches actual number of wins for each player
        max_round_points = 0
        points_to_player = 0
        for player in self.players:
            print(f"{player.name} guessed {player.guessed_stick} sticks and won {stick_counts[player.name]} sticks.")
            if player.guessed_stick == stick_counts[player.name]:
                if player.guessed_stick == 0:
                    points_to_player = 0
                    self.points[player_idx] += 5
                    points_to_player = 5
                else: 
                    self.points[player_idx] += player.guessed_stick+10
                    points_to_player = player.guessed_stick+10
                print(f"{player.name} guessed correctly and wins {points_to_player} points!")
                # You can modify this to award any number of points
            else:
                print(f"{player.name} Plumped.")
            # get winner of round:
            if points_to_player > max_round_points:
                max_round_points = points_to_player
            player_idx += 1
        self.curr_round += 1
        reward = self.agent.eval_round(self.points[0]) 
        self.agent.update_Q(self.previous_state, self.previous_action, reward, self.get_state())
        self.previous_state = None
        self.previous_action = None
        
        if (self.curr_round == self.num_rounds):
            self.end_game()
        else: 
            self.reset()
            self.start_game()
    
    def reset(self):
        self.deck.reset_deck()
        # winner_of_stick[0] = 1, means player 1 won stick 0
        self.winner_of_stick = []
        # played_cards[0] = (Card, Player 0)
        self.played_cards = []
        # current_player_index = who's turn
        self.current_player_index = 0
        self.previous_state = None
        self.previous_action = None
    
    def end_game(self):
        print("Game Over!")
        print("Scores:")
        player_idx = 0
        winner = 0
        max_player_points = 0
        for player in self.players:
            print(f"{player.name}'s score was {self.points[player_idx]}")
            if self.points[player_idx] > max_player_points:
                max_player_points = self.points[player_idx]
                winner = player.name
            player_idx += 1
        print(f"Contratulations {winner}, you won the game Plump!")

    def get_legal_actions(self):
        if self.curr_round == -1:
            # guess sticks state
            return list(range(self.cards_per_player + 1))
        else:
            # play card state
            return list(range(len(self.players[0].hand)))
        


# Input number of players and cards per player
players_count = 3
# int(input("Enter the number of players: "))
cards_count = 2
#int(input("Enter the number of cards per player: "))
print("Starting game for 3 players with 2 cards each")
print("-----------------------------")

# Test the game
game = PlumpGame(players_count, cards_count)
game.start_game()
