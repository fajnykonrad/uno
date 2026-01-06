import socket
import json
from shared.protocol import (
    JOIN_REQUEST,
    JOIN_ACCEPTED,
    LOBBY_UPDATE,
    GAME_STATE,
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
        elif message[TYPE] == LOBBY_UPDATE:
            players = message[DATA]['players']
            print("Current players in lobby:")
        elif message[TYPE] == GAME_STATE:
            print("\n=== Game State ===")
            print("Current card on table:", message[DATA]['current_card'])
            print("Players: ")
            for p in message[DATA]['players']:
                if(p['id'] == message[DATA]['current_turn']):
                    print(f"* {p['username']} (ID: {p['id']}) - Current Turn")
                else:
                    print(f"- {p['username']} (ID: {p['id']})")
            print("Your hand:")
            for c in message[DATA]['your_hand']:
                print(f"{c['color']} {c['value']}")