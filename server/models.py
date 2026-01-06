class Player:
    def __init__(self, conn, addr, nickname, player_id):
        self.conn = conn
        self.addr = addr
        self.nickname = nickname
        self.id = player_id
