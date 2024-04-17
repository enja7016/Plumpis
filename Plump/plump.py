import random

# Class defining a card with suit and rank
class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.rank} of {self.suit}"

# Class defining a deck of cards, one card of each type (52 cards)
class Deck:
    def __init__(self):
        self.cards = []
        self.build()

    # Fill the list of cards
    def build(self):
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
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

# Class defining a player with name, hand of cards, and guessed tricks
class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.guessed_tricks = 0

    # Add card to hand
    def add_card(self, card):
        self.hand.append(card)

    # Play the chosen card from the hand if it exists
    def play_card(self, card_index):
        if 0 <= card_index < len(self.hand):
            return self.hand.pop(card_index)
        else:
            return None

    # Set the number of tricks guessed by the player
    def guess_tricks(self, guessed_tricks):
        self.guessed_tricks = guessed_tricks

# Class defining the game of plump with deck, players, and tricks
class PlumpGame:
    def __init__(self, players_count, cards_count):
        self.deck = Deck()
        self.deck.shuffle()
        self.players_count = players_count
        self.players = [Player(f"Player {i+1}") for i in range(players_count)]
        self.tricks = []
        self.current_trick = []
        self.current_player_index = 0
        self.cards_per_player = cards_count

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
        # Guess number of tricks for each player
        self.guess_tricks()
        self.play_trick()

    # Play a trick
    def play_trick(self):
        # For each player:
        for _ in range(self.players_count):
            # Get current player from index:
            current_player = self.players[self.current_player_index]
            print(f"{current_player.name}'s turn")
            print("Your hand:", [str(card) for card in current_player.hand])
            # Choose card:
            card_index = int(input("Enter the index of the card you want to play: "))
            # Play chosen card:
            played_card = current_player.play_card(card_index)
            # Add played card and player index to trick:
            if played_card:
                self.current_trick.append((played_card, self.current_player_index))
                # Go to next player:
                self.current_player_index = (self.current_player_index + 1) % len(self.players)
            else:
                print("Invalid card index. Try again.")
        # Get result from trick:
        self.resolve_trick()

    # Guess number of tricks for each player
    def guess_tricks(self):
        for player in self.players:
            print(f"{player.name}, your hand is:", [str(card) for card in player.hand])
            guessed_tricks = int(input("How many tricks do you think you will win? "))
            player.guess_tricks(guessed_tricks)

    # Resolve trick
    def resolve_trick(self):
        # Find winning card and its player index:
        winning_card, winning_player_index = max(self.current_trick, key=lambda item: (item[0].rank, item[0].suit))
        # Get winning player:
        winning_player = self.players[winning_player_index]
        # Add winner to trick:
        self.tricks.append(winning_player)
        print("-----------------------------")
        print(f"{winning_player.name} wins the trick with {winning_card}")
        print("-----------------------------")
        # Reset current trick:
        self.current_trick = []
        if len(self.tricks) < self.cards_per_player:
            self.play_trick()
        else:
            self.end_game()

    # Ending the game
    def end_game(self):
        print("Game Over!")
        
        # Count the number of tricks won by each player
        trick_counts = {player.name: 0 for player in self.players}
        for player in self.tricks:
            trick_counts[player.name] += 1
        
        # Check if guessed number of wins matches actual number of wins for each player
        for player in self.players:
            print(f"{player.name} guessed {player.guessed_tricks} tricks and won {trick_counts[player.name]} tricks.")
            if player.guessed_tricks == trick_counts[player.name]:
                print(f"{player.name} guessed correctly and wins 10 points!")
                # You can modify this to award any number of points
            else:
                print(f"{player.name} did not guess correctly.")

# Input number of players and cards per player
players_count = int(input("Enter the number of players: "))
cards_count = int(input("Enter the number of cards per player: "))
print("-----------------------------")

# Test the game
game = PlumpGame(players_count, cards_count)
game.start_game()
