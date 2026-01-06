import socket
import threading
import json
from shared.protocol import (
    JOIN_REQUEST,
    JOIN_ACCEPTED,
    TYPE,
    DATA
)
from shared.utils import send_message, receive_messages

HOST = '192.168.1.53'
PORT = 8000
clients = []

def handle_client(conn, addr):
    buffer = ""
    print(f"New connection from {addr}")
    while True:
        try:
            messages, buffer = receive_messages(conn, buffer)
            if not messages:
                continue

            for message in messages:
                print("Received:", message)

                if message[TYPE] == JOIN_REQUEST:
                    response = {
                        TYPE : JOIN_ACCEPTED,
                        DATA : {"message": "Welcome to the server!"}
                }
                send_message(conn, response)
                
        except Exception as e:
            print(f"Error handling client {addr}: {e}")
            break
    conn.close()
    print(f"Connection from {addr} closed.")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        clients.append(conn)
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
        print(f"Active connections: {threading.active_count() - 1}")

if __name__ == "__main__":
    main()