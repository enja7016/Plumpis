from plump import Card

class Bot:
    def __init__(self) -> None:
        self.hand = []
        self.board = []
        self.guessed_sticks = 0
    
    def update_cards(self, hand, cards_in_play):
        self.hand = hand
        self.board = cards_in_play

    def set_guess(self):
        self.guessed_sticks = 0
        for card in self.hand:
            if card.suit > 10:
                self.guessed_sticks += 1

    def play_card(self):
        highest_rank = 0
        if self.board == []:
            return self.hand.index(max(self.hand))
        for card in self.board:
            if card.suit > highest_rank:
                highest_rank = card.suit
        
        upper_bound = self.hand[0].suit
        current_card = self.hand[0]
        higher_exists = False
        for card in self.hand[1:]:
            diff = card.suit - highest_rank
            if diff > 0 and diff < upper_bound:
                upper_bound = card.suit
                current_card = card
                higher_exists = True
        if higher_exists:
            return self.hand.index(current_card)
        else:
            return self.hand.index(min(card))