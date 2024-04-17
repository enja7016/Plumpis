import random

# Class defining a card with suit and rank
class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.rank} {self.suit}"

# Class defining a deck of cards, one card of each type (52 cards)
class Deck:
    def __init__(self):
        self.cards = []
        self.build()

    # Fill the list of cards
    def build(self):
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

# Class defining a player with name, hand of cards, and guessed stick
class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.guessed_stick = 0

    # Add card to hand
    def add_card(self, card):
        self.hand.append(card)

    # Play the chosen card from the hand if it exists
    def play_card(self, card_index):
        if 0 <= card_index < len(self.hand):
            return self.hand.pop(card_index)
        else:
            return None

    # Set the number of stick guessed by the player
    def guess_stick(self, guessed_stick):
        self.guessed_stick = guessed_stick

# Class defining the game of plump with deck, players, and stick
class PlumpGame:
    def __init__(self, players_count, cards_count):
        self.deck = Deck()
        self.deck.shuffle()
        self.players_count = players_count
        self.players = [Player(f"Player {i+1}") for i in range(players_count)]
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
        self.num_rounds = 1
        self.curr_round = 0

    # Deal number of cards to each player from the deck
    def deal_cards(self):
        for _ in range(self.cards_per_player):
            for player in self.players:
                card = self.deck.deal_card()
                if card:
                    player.add_card(card)

    # Start a new game by dealing and playing the round
    def start_game(self):
        self.deal_cards()
        # Guess number of stick for each player
        self.guess_stick()
        self.play_stick()

    # Play a stick
    def play_stick(self):
        # For each player:
        curr_player = 0
        while curr_player < self.players_count:
                # Get current player from index:
            current_player = self.players[self.current_player_index]
            print(f"{current_player.name}'s turn")
            print("Your hand:", [str(card) for card in current_player.hand])
            # Choose card:
            card_index = int(input("Enter the index of the card you want to play: "))
            # Play chosen card:
            played_card = current_player.play_card(card_index)
            # Add played card and player index to stick:
            if played_card:
                self.played_cards.append((played_card, self.current_player_index))
                # Go to next player:
                self.current_player_index = (self.current_player_index + 1) % len(self.players)
                curr_player += 1
            else:
                print("Invalid card index. Try again.")

        # Get result from stick:
        self.resolve_stick()

    # Guess number of stick for each player
    def guess_stick(self):
        for player in self.players:
            print(f"{player.name}, your hand is:", [str(card) for card in player.hand])
            guessed_stick = int(input("How many stick do you think you will win? "))
            player.guess_stick(guessed_stick)

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
        
        # Count the number of stick won by each player
        stick_counts = {player.name: 0 for player in self.players}
        for player in self.winner_of_stick:
            stick_counts[player.name] += 1
            
        player_idx = 0
        # Check if guessed number of wins matches actual number of wins for each player
        for player in self.players:
            print(f"{player.name} guessed {player.guessed_stick} stick and won {stick_counts[player.name]} stick.")
            if player.guessed_stick == stick_counts[player.name]:
                points_to_player = 0
                if player.guessed_stick == 0:
                    self.points[player_idx] += 5
                    points_to_player = 5
                else: 
                    self.points[player_idx] += player.guessed_stick*10
                    points_to_player = player.guessed_stick*10
                print(f"{player.name} guessed correctly and wins {points_to_player} points!")
                # You can modify this to award any number of points
            else:
                print(f"{player.name} Plumped.")
            player_idx += 1
        self.curr_round += 1
        if (self.curr_round == self.num_rounds):
            self.end_game()
        else: 
            self.start_game()
    
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

# Input number of players and cards per player
players_count = int(input("Enter the number of players: "))
cards_count = int(input("Enter the number of cards per player: "))
print("-----------------------------")

# Test the game
game = PlumpGame(players_count, cards_count)
game.start_game()
