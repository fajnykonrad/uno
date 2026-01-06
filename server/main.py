import socket
import threading
import json
from shared.protocol import JOIN_REQUEST, JOIN_ACCEPTED

HOST = '0.0.0.0'
PORT = 8000
clients = []

def handle_client(conn, addr):
    print(f"New connection from {addr}")
    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break

            msg = json.loads(data)
            print("Received:", msg)
            if msg['type'] == JOIN_REQUEST:
                response = {
                    'type' : JOIN_ACCEPTED,
                    "data": {"message": "Welcome to the server!"}
                }
                conn.sendall(json.dumps(response).encode())
        except Exception as e:
            print(f"Error handling client {addr}: {e}")
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