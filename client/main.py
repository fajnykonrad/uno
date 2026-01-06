import socket
import json
from shared.protocol import (
    JOIN_REQUEST,
    JOIN_ACCEPTED,
    LOBBY_UPDATE,
    TYPE,
    DATA
)
from shared.utils import send_message, receive_messages

SERVER_IP = input("Enter server IP address: ")
SERVER_PORT = 8000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, SERVER_PORT))

username = input("Enter your username: ")

msg = {
    TYPE: JOIN_REQUEST,
    DATA: {'username': username}
}

send_message(client, msg)

buffer = ""

while True:
    messages, buffer = receive_messages(client, buffer)

    for message in messages:
        if message[TYPE] == JOIN_ACCEPTED:
            response = message
            print("Response from server:", response)
        if message[TYPE] == LOBBY_UPDATE:
            players = message[DATA]['players']
            print("Current players in lobby:")
