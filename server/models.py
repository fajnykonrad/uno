import random

COLORS = ["r", "y", "g", "b"]
VALUES = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
          "skip", "rev", "+2"]
WILD_CARDS = ["change", "+4"]

class Player:
    def __init__(self, conn, addr, username, player_id):
        self.conn = conn
        self.addr = addr
        self.username = username
        self.id = player_id

class Card:
    def __init__(self, color, value):
        self.color = color  # Pot ser nul
        self.value = value

    def to_dict(self):
        return {"color": self.color, "value": self.value}

class Deck():
    def __init__(self):
        self.cards = []
        for color in COLORS:
            self.cards.append(Card(color, "0"))
            for v in VALUES[1:]:
                self.cards.extend([Card(color, v), Card(color, v)])
        for _ in range(4):
            for wild in WILD_CARDS:
                self.cards.append(Card(None, wild))
        random.shuffle(self.cards)

    def draw(self, n=1):
        drawn = self.cards[:n]
        self.cards = self.cards[n:]
        return drawn