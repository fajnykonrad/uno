import socket
import threading
import json
from shared.protocol import (
    JOIN_REQUEST,
    JOIN_ACCEPTED,
    LOBBY_UPDATE,
    GAME_STATE,
    START_GAME,
    TYPE,
    DATA
)
from shared.utils import send_message, receive_messages
from server.lobby import Lobby
from server.game import Game

HOST = '192.168.1.53'
PORT = 8000

lobby = Lobby()
game = None
clients = []

def lobbyUpdate():
    """Send LOBBY_UPDATE to all connected players."""
    data = lobby.get_lobby_data()
    for p in lobby.players:
        send_message(p.conn, {
            TYPE: LOBBY_UPDATE,
            DATA: data
        })


def handle_client(conn, addr):
    buffer = ""
    player = None
    print(f"New connection from {addr}")
    try:
        while True:
            messages, buffer = receive_messages(conn, buffer)
            if messages is None:
                continue

            for message in messages:
                print("Received:", message)

                if message[TYPE] == JOIN_REQUEST:
                    # Add player to lobby
                    username = message[DATA]['username']
                    player = lobby.addPlayer(conn, addr, username)
                    
                    #Confirm join to player
                    response = {
                        TYPE : JOIN_ACCEPTED,
                        DATA : {
                            'player_id': player.id,
                            'is_host': (player.id == lobby.host_id)
                        }
                    }
                    send_message(conn, response)
                    
                    #Update lobby for all players
                    lobbyUpdate()
                elif message[TYPE] == START_GAME:
                    global game
                    if not game:
                        game = Game(lobby.players)
                        # Initial game state
                        for p in lobby.players:
                            state = game.get_player_state(p)
                            send_message(p.conn, {
                                TYPE: GAME_STATE,
                                DATA: state
                            })
            
            

    except Exception as e:
        print(f"Client disconnected: {addr} - {e}")
    finally:
        if player:
            lobby.removePlayer(player.id)
            lobbyUpdate()
        if conn in clients:
            clients.remove(conn)
        conn.close()
        print(f"Connection from {addr} closed.")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server listening on {HOST}:{PORT}")

    try:
        while True:
            conn, addr = server.accept()
            clients.append(conn)
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
            print(f"Active connections: {threading.active_count() - 1}")
    except KeyboardInterrupt:
        print("Shutting down server...")
    finally:
        for c in clients:
            c.close()
        server.close()
        print("Server closed.")

if __name__ == "__main__":
    main()

