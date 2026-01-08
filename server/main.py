import socket
import threading
import json
from shared.protocol import *
from shared.utils import *
from server.lobby import Lobby
from server.game import Game

HOST = socket.gethostbyname(socket.gethostname())
PORT = 8000

lobby = Lobby()
game = None
clients = []

def lobbyUpdate():
    """Update de lobby a tots els jugadors connectats."""
    data = lobby.get_lobby_data()
    for p in lobby.players:
        send_message(p.conn, {
            TYPE: LOBBY_UPDATE,
            DATA: data
        })
def gameUpdate():
    """Update de l'estat del joc a tots els jugadors connectats."""
    for p in lobby.players:
        state = game.get_player_state(p)
        send_message(p.conn, {
            TYPE: GAME_STATE,
            DATA: state
        })

#Client thread
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

                if message[TYPE] == JOIN_REQUEST:
                    # Add player to lobby
                    if len(lobby.players) >= 4:
                        send_message(conn, {
                            TYPE: JOIN_REJECTED,
                            DATA: "Lobby is full (max 4 players)."
                        })
                        continue
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
                    
                    lobbyUpdate()
                elif message[TYPE] == START_GAME:
                    global game
                    if not game:
                        game = Game(lobby.players)
                        gameUpdate()
                elif message[TYPE] == PLAY_CARD and game:
                    card_data = message[DATA]['card']
                    chosen_color = message[DATA].get('chosen_color')

                    player = next((p for p in lobby.players if p.conn == conn), None)
                    card = next((c for c in player.hand if c.color == card_data['color'] and c.value == card_data['value']), None)

                    if not card:
                        print("Card not found in player's hand")
                        send_message(conn, {
                            TYPE: 'ERROR',
                            DATA: "Card not found"
                        })
                        continue
                    success, error = game.play_card(player, card, chosen_color)

                    if not success:
                        print("Error:", error)
                        send_message(conn, {
                            TYPE: INVALID_MOVE,
                            DATA: {"reason": error}
                        })
                        continue
                            
                    gameUpdate()
                    winner = game.check_winner()
                    if winner:
                        for p in lobby.players:
                            send_message(p.conn, {
                                TYPE: GAME_OVER,
                                DATA: {"winner_id": winner.id, "winner_username": winner.username}
                            })
                        
                        game = None

                        lobbyUpdate()
                elif message[TYPE] == DRAW_CARD and game:
                    success, error = game.draw_card(player)

                    if not success:
                        send_message(conn, {
                            TYPE: INVALID_MOVE,
                            DATA: {"reason": error}
                        })
                        continue

                    gameUpdate()
                elif message[TYPE] == DISCONNECT:
                    lobby.removePlayer(player.id)
                    lobbyUpdate()
                    return

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

