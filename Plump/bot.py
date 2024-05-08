class Bot:
    def __init__(self, hand) -> None:
        self.hand = hand
        self.played_cards = []
        self.guessed_sticks = 0
    
    def __str__(self) -> str:
        return f"Hand {self.hand}\nGuessed Sticks {self.guessed_sticks}"

    def update_cards(self, hand, cards_in_play):
        self.hand = hand
        self.played_cards = cards_in_play

    # Method to assign a numerical value to each rank
    def rank_value(self, rank):
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        return ranks.index(rank)

    def set_guess(self):
        self.guessed_sticks = 0
        for card in self.hand:
            if self.rank_value(card.rank) > 8:
                self.guessed_sticks += 1

    def choose_action_bot(self):
        print([str(card) for card in self.hand])
        highest_rank = 0
        if self.played_cards == []:
            return self.hand.index(max(self.hand))
        for card in self.played_cards:
            rank = self.rank_value(card[0].rank)
            if rank > highest_rank:
                highest_rank = rank
        
        upper_bound = self.rank_value(self.hand[0].rank)
        current_card = self.hand[0]
        higher_exists = False
        for card in self.hand[1:]:
            diff = self.rank_value(card.rank) - highest_rank
            if diff > 0 and diff < upper_bound:
                upper_bound = self.rank_value(card.rank)
                current_card = card
                higher_exists = True
        if higher_exists:
            return self.hand.index(current_card)
        else:
            return self.hand.index(min(self.hand))