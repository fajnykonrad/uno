#Standard

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

LOBBY_UPDATE = "lobby_update"
"""
Server → Client
{
    type: LOBBY_UPDATE
    data: {
        players: [
            {
                username: str,
                is_host: bool
            }
        ]
    }
}
"""