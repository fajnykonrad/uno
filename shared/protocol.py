# Standard
TYPE = "type"
DATA = "data"

####################
# Connection Types #
####################

JOIN_REQUEST = "join_request"
"""
Client → Server
{
    type: JOIN_REQUEST
    data: {
        username: str
    }
}
"""

JOIN_ACCEPTED = "join_accepted"
"""
Server → Client
{
    type: JOIN_ACCEPTED
    data: {
        player_id: int,
        is_host: bool
    }
}
"""

PLAYER_LEFT = "player_left"
"""
Client → Server
{
    type: PLAYER_LEFT
    data: {}
}
"""

####################
# Lobby Types      #
####################

LOBBY_UPDATE = "lobby_update"
"""
Server → Client
{
    type: LOBBY_UPDATE
    data: {
        players: [
            {
                id: int,
                username: str,
                is_host: bool
            }
        ],
        host_id: int
    }
}
"""

START_GAME = "start_game"
"""
Client → Server (host only)
{
    type: START_GAME
    data: {}
}
"""

####################
# Game Types       #
####################

GAME_STATE = "game_state"
"""
Server → Client
{
    type: GAME_STATE
    data: {
        current_card: {color: str or None, value: str},
        players: [
            {
                id: int,
                username: str,
                card_count: int
            }
        ],
        your_hand: [
            {color: str or None, value: str}
        ],
        current_turn: int  # player_id of current turn
    }
}
"""

PLAY_CARD = "play_card"
"""
Client → Server
{
    type: PLAY_CARD
    data: {
        card: {color: str or None, value: str},
        chosen_color: str or None  # only for Wild cards
    }
}
"""

DRAW_CARD = "draw_card"
"""
Client → Server
{
    type: DRAW_CARD
    data: {}
}
"""

INVALID_MOVE = "invalid_move"
"""
Server → Client
{
    type: INVALID_MOVE
    data: {
        reason: str
    }
}
"""

####################
# Turn & Effects   #
####################

TURN_UPDATE = "turn_update"
"""
Server → Client
{
    type: TURN_UPDATE
    data: {
        current_turn: int  # player_id whose turn it is
    }
}
"""

CARD_PLAYED = "card_played"
"""
Server → Client
{
    type: CARD_PLAYED
    data: {
        player_id: int,
        card: {color: str or None, value: str},
        chosen_color: str or None  # if wild
    }
}
"""

####################
# Game End         #
####################

GAME_OVER = "game_over"
"""
Server → Client
{
    type: GAME_OVER
    data: {
        winner_id: int,
        winner_name: str
    }
}
"""
