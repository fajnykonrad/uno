import socket
import json
from shared.protocol import JOIN_REQUEST, JOIN_ACCEPTED

SERVER_IP = input("Enter server IP address: ")
SERVER_PORT = 8000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, SERVER_PORT))

username = input("Enter your username: ")

msg = {
    'type': JOIN_REQUEST,
    'data': {'username': username}
}

client.sendall(json.dumps(msg).encode())

response = client.recv(1024).decode()
print("Response from server:", response)

client.close()