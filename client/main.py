import socket
import threading
import time
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.console import Group

from shared.protocol import *
from shared.utils import *

console = Console()

# --- Connect to server ---
SERVER_IP = input("Server IP: ")
SERVER_PORT = 8000
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, SERVER_PORT))

username = input("Enter your username: ")
send_message(client, {TYPE: JOIN_REQUEST, DATA: {"username": username}})

# --- Shared state ---
buffer = ""
my_id = None
is_host = False
host_id = None
players = []
selected_card_index = 0
game_state = None
state_lock = threading.Lock()

COLORS = {
    "r": "red",
    "g": "green",
    "y": "yellow",
    "b": "blue",
    "wild": "magenta"  # optional for wild cards
}

# --- Receiver thread ---
def receive_loop():
    global buffer, my_id, is_host, host_id, players, game_state
    while True:
        try:
            messages, buffer = receive_messages(client, buffer)
            for msg in messages:
                with state_lock:
                    if msg[TYPE] == JOIN_ACCEPTED:
                        my_id = msg[DATA]['player_id']
                        is_host = msg[DATA]['is_host']
                    elif msg[TYPE] == LOBBY_UPDATE:
                        players = msg[DATA]['players']
                        host_id = msg[DATA]['host_id']
                        is_host = (my_id == host_id)
                    elif msg[TYPE] == GAME_STATE:
                        game_state = msg[DATA]
        except Exception:
            console.print("[red]Disconnected from server[/red]")
            break

# --- Renderer thread ---
def render_loop():
    with Live(console=console, refresh_per_second=10, screen=False) as live:
        while True:
            with state_lock:
                panels = []

                # --- Top Box: Current card + players ---
                top_text = ""
                if game_state and "current_card" in game_state:
                    c = game_state['current_card']
                    top_text += f"Current Card: [{COLORS.get(c['color'],'white')}]{c['value']}[/{COLORS.get(c['color'],'white')}]\n"
                top_text += "Players:\n"
                for p in players:
                    host_marker = " (Host)" if p['id'] == host_id else ""
                    turn_marker = ""
                    if game_state and p['id'] == game_state.get('current_turn'):
                        turn_marker = " <- Current Turn"
                    top_text += f"- {p['username']}{host_marker}{turn_marker}\n"
                panels.append(Panel(top_text.strip(), title="UNO Top Box"))

                # --- Middle Box: Your Hand ---
                middle_text = ""
                if game_state and "your_hand" in game_state:
                    for card in game_state['your_hand']:
                        middle_text += f"[{COLORS.get(card['color'], 'white')}]{card['value']}[/{COLORS.get(card['color'], 'white')}]  "
                panels.append(Panel(middle_text.strip() or "Waiting for cards...", title="Your Hand"))

                # --- Bottom Box: Controls / Notifications ---
                bottom_text = ""
                if not game_state:
                    bottom_text = "Waiting in lobby..."
                    if is_host:
                        bottom_text += " Press ENTER to start the game."
                else:
                    if game_state.get('current_turn') == my_id:
                        bottom_text = "Your turn! (Later: arrow keys to select, ENTER to play)"
                    else:
                        current_player = next((p['username'] for p in players if p['id']==game_state.get('current_turn')), "-")
                        bottom_text = f"{current_player}'s turn..."
                panels.append(Panel(bottom_text, title="Controls"))

                # --- Update Live without flicker ---
                live.update(Group(*panels))

            time.sleep(0.2)

# --- Input thread ---
def input_loop():
    global game_state
    while True:
        # Only allow host to start game when game_state is None
        if is_host and not game_state:
            key = get_key()
            if key == '\r':
                send_message(client, {TYPE: START_GAME, DATA: {}})
        elif game_state and game_state.get('current_turn') == my_id:
            if not game_state.get('your_hand'):
                continue
            key = get_key()
            if key == "\x1b[D":  # left
                selected_index = (selected_index - 1) % len(game_state['your_hand'])
            elif key == "\x1b[C":  # right
                selected_index = (selected_index + 1) % len(game_state['your_hand'])


# --- Start threads ---
threading.Thread(target=receive_loop, daemon=True).start()
threading.Thread(target=render_loop, daemon=True).start()
threading.Thread(target=input_loop, daemon=True).start()

# --- Keep main thread alive ---
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    client.close()