from server.models import Player, Deck
import random

class Game:
    def __init__(self, players):
        self.players = players  
        self.turn_index = 0
        self.deck = Deck()
        self.discard_pile = []
        self.direction = 1
        self.draw = 0

        for p in self.players:
            p.hand = self.deck.draw(7)

        # Pick first card for discard pile (must not be wild draw 4)
        while True:
            card = self.deck.draw()[0]
            if card.value not in ["Wild Draw Four", "Wild"]:
                self.discard_pile.append(card)
                break
            else:
                self.deck.cards.append(card)  
                random.shuffle(self.deck.cards)
    # Funcions útils
    def current_player(self):
        return self.players[self.turn_index]
    
    def advance_turn(self, steps=1):
        self.turn_index = (
            self.turn_index + self.direction * steps
        ) % len(self.players)

    def top_card(self):
        return self.discard_pile[-1]

    # Validació joc
    def is_valid(self, card):
        top = self.top_card()
        return (
            card.color is None or
            card.color == top.color or
            card.value == top.value
        )

    def apply_card_effect(self, card, chosen_color):
        if card.color is None:
            card.color = chosen_color
        if card.value == "skip":
            self.advance_turn()
        elif card.value == "rev":
            self.direction *= -1
            if len(self.players) == 2:
                self.advance_turn()
        elif card.value == "+2":
            self.draw += 2
        elif card.value == "+4":
            self.draw += 4

    def check_winner(self):
        for p in self.players:
            if len(p.hand) == 0:
                return p
        return None
    ###################
    ##    Actions    ##
    ###################

    def play_card(self, player, card, chosen_color=None):
        if self.current_player().id != player.id:
            return False, "Not your turn"
        if card not in player.hand:
            return False, "You don't have that card"
        if not self.is_valid(card):
            return False, "Invalid move"  
        if card.color is None and chosen_color is None:
            return False, "Must choose color"
        # Play card
        player.hand.remove(card)
        self.discard_pile.append(card)

        self.apply_card_effect(card, chosen_color)
        # +2 i +4
        if self.draw > 0:
            self.advance_turn()
            next_player = self.current_player()
            self.reshuffle_discard()
            drawn_cards = self.deck.draw(self.draw)
            next_player.hand.extend(drawn_cards)
            self.draw = 0
        self.advance_turn()

        return True, None
    
    def draw_card(self, player):
        if self.current_player().id != player.id:
            return False, "Not your turn"
        
        self.reshuffle_discard()
        player.hand.extend(self.deck.draw(1))
        self.advance_turn()

        return True, None
    
    def reshuffle_discard(self):
        if len(self.deck.cards) > 5:
            return
        if len(self.discard_pile) <= 1:
            return 
        
        top_card = self.discard_pile[-1]

        self.deck.cards.extend(self.discard_pile[:-1])
        random.shuffle(self.deck.cards)
        self.discard_pile = [top_card]
    
    ################
    ## Game State ##
    ################    
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