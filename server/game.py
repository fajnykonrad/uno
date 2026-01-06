from server.models import Player, Deck
import random

class Game:
    def __init__(self, players):
        self.players = players  # list of Player objects
        self.turn_index = 0
        self.deck = Deck()
        self.discard_pile = []

        for p in self.players:
            p.hand = self.deck.draw(7)

        # Pick first card for discard pile (must not be wild draw 4)
        while True:
            card = self.deck.draw()[0]
            if card.value not in ["Wild Draw Four", "Wild"]:
                self.discard_pile.append(card)
                break
            else:
                self.deck.cards.append(card)  # put it back
                random.shuffle(self.deck.cards)

    def current_player(self):
        return self.players[self.turn_index]

    def get_player_state(self, player):
        """Return game state for a specific player"""
        return {
            "current_card": self.discard_pile[-1].to_dict(),
            "players": [
                {"id": p.id,
                "username": p.username,
                "card_count": len(p.hand)}
                for p in self.players
            ],
            "your_hand": [c.to_dict() for c in player.hand],
            "current_turn": self.current_player().id
        }