from server.models import Player

class Lobby:
    def __init__(self):
        self.players = []
        self.host_id = None
        self.next_player_id = 1

    def addPlayer(self, conn, addr, username):
        player_id = self.next_player_id
        self.next_player_id += 1

        player = Player(conn, addr, username, player_id)
        self.players.append(player)

        if len(self.players) == 1:
            self.host_id = player_id  # first player is host

        return player

    def removePlayer(self, player_id):
        self.players = [p for p in self.players if p.id != player_id]
        if self.host_id == player_id and self.players:
            self.host_id = self.players[0].id  # new host

    def get_lobby_data(self):
        return {
            "players": [{"id": p.id, "username": p.username} for p in self.players],
            "host_id": self.host_id
        }