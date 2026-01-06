import socket
import threading
import json
from shared.protocol import (
    JOIN_REQUEST,
    JOIN_ACCEPTED,
    LOBBY_UPDATE,
    TYPE,
    DATA
)
from shared.utils import send_message, receive_messages
from server.lobby import Lobby

HOST = '192.168.1.53'
PORT = 8000

lobby = Lobby()

def handle_client(conn, addr):
    buffer = ""
    leavingPlayer = None
    print(f"New connection from {addr}")
    try:
        while True:
            messages, buffer = receive_messages(conn, buffer)
            if not messages:
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
                        DATA : {"message": "Welcome to the server!"}
                    }
                    send_message(conn, response)
                    
                    #Update lobby for all players
                    for p in lobby.players:
                        lobbyUpdate()
            
            

    except Exception as e:
        print(f"Client disconnected: {addr} - {e}")
    finally:
        if leavingPlayer:
            lobby.removePlayer(leavingPlayer.id)
            for p in lobby.players:
                lobbyUpdate()
        conn.close()
        print(f"Connection from {addr} closed.")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
        print(f"Active connections: {threading.active_count() - 1}")

if __name__ == "__main__":
    main()

def lobbyUpdate():
    """Send LOBBY_UPDATE to all connected players."""
    data = lobby.get_lobby_data()
    for p in lobby.players:
        send_message(p.conn, {
            TYPE: LOBBY_UPDATE,
            DATA: data
        })
