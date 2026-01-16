import socket
import threading
import time
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.console import Group

from shared.protocol import *
from shared.utils import *
from shared.uimodels import *

console = Console()

# Connexió al servidor
SERVER_IP = input("Server IP: ")
SERVER_PORT = 8000
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, SERVER_PORT))

username = input("Enter your username: ")
send_message(client, {TYPE: JOIN_REQUEST, DATA: {"username": username}})
console.clear()

# Variables globals
buffer = ""
my_id = None 
is_host = False
host_id = None
players = []
selected_index = 0
game_state = None
error_message = None
winner = None
state_lock = threading.Lock()
color_select_mode = False
color_options = ['r','g','b','y']
chosen_color = None
exitf = False

COLORS = {
    "r": "red",
    "g": "green",
    "y": "yellow",
    "b": "blue",
    None: "magenta"  
}

#MISSATGES DEL SERVIDOR
def receiver():
    global buffer, my_id, is_host, host_id, players, game_state, error_message, winner, selected_index, exitf
    while not exitf:
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
                        error_message = None
                        if "your_hand" in game_state:
                            if len(game_state['your_hand']) == 0:
                                selected_index = 0
                            else:
                                selected_index = min(selected_index, len(game_state['your_hand']) - 1)
                    elif msg[TYPE] == INVALID_MOVE:
                        error_message = msg[DATA]['reason']
                    elif msg[TYPE] == GAME_OVER:
                        winner_id = msg[DATA]['winner_id']
                        winner = next((p['username'] for p in players if p['id'] == winner_id), "Unknown")
                        game_state = None
                    elif msg[TYPE] == JOIN_REJECTED:
                        console.clear()
                        console.print("Cannot join lobby")
                        exitf = True
                        return
        except socket.timeout:
            continue
        except Exception:
            if not exitf:
                console.print(f"[red]Disconnected from server: {e}[/red]")
            break

# GRAFICA 
def graphics():
    global exitf
    with Live(console=console, refresh_per_second=10, screen = True) as live:
        while not exitf:
            with state_lock:
                panels = []

                #TOP
                top_text = ""
                if game_state and "current_card" in game_state:
                    c = game_state['current_card']
                    top_text += f"Current Card:\n{print_card(c)}\n\n"
                top_text += "Players:\n"
                for p in players:
                    you_marker = " (you)" if p['id'] == my_id else ""
                    turn_marker = ""
                    if game_state and p['id'] == game_state.get('current_turn'):
                        turn_marker = " <- Current Turn"
                        if game_state['direction'] == 1:
                            turn_marker += " ↓"
                        else:
                            turn_marker += " ↑"
                    top_text += f"- {p['username']}{you_marker}{turn_marker}\n"
                panels.append(Panel(top_text.strip(), title="UNO Top Box"))

                #MIDDLE
                middle_text = ""
                if game_state and "your_hand" in game_state:
                    middle_text += print_hand(game_state['your_hand'], selected_index)

                elif winner is not None:
                    middle_text = f"[green]Game Over! Winner: {winner}[/]"
                panels.append(Panel(middle_text.strip() or "Waiting for cards...", title="Your Hand"))

                #BOTTOM
                bottom_text = ""
                if not game_state:
                    bottom_text = "Waiting in lobby..."
                    if is_host and len(players) >= 2:
                        bottom_text += " Press ENTER to start the game."
                    elif is_host:
                        bottom_text += " Minimum 2 players to start."
                    bottom_text += "\n\n(q)uit"
                else:
                    if game_state.get('current_turn') == my_id:
                        if color_select_mode:
                            bottom_text = "Choose color: [red](r)ed[/], [green](g)reen[/], [blue](b)lue[/], [yellow](y)ellow[/]"
                            if error_message:
                                bottom_text += f"\n[red]Error: {error_message}[/red]"
                        else:
                            bottom_text = "← → select | ENTER play | D draw"
                            if error_message:
                                bottom_text += f"\n[red]Error: {error_message}[/red]"
                    else:
                        current_player = next((p['username'] for p in players if p['id']==game_state.get('current_turn')), "-")
                        bottom_text = f"{current_player}'s turn..."
                panels.append(Panel(bottom_text, title="Controls"))

                #UPDATE
                live.update(Group(*panels))

            time.sleep(0.2)

#INPUT I TRANSMISSIÓ A SERVIDOR
def inputloop():
    global game_state, selected_index, color_select_mode, chosen_color, exitf
    while not exitf:
        # Only allow host to start game when game_state is None
        if not game_state:
            key = get_key()
            if is_host and key == KEY_ENTER and len(players) >= 2:
                send_message(client, {TYPE: START_GAME, DATA: {}})
            elif key is not None and key == 'q':
                exitf = True
                try:
                    send_message(client, {TYPE: DISCONNECT, DATA: {}})
                    client.shutdown(socket.SHUT_RDWR)
                    client.close()
                except Exception:
                    pass
                break
        elif game_state and game_state.get('current_turn') == my_id:
            if not game_state.get('your_hand'):
                continue
            key = get_key()
            if color_select_mode:
                if key is None:
                    time.sleep(0.02)
                    continue
                if key in color_options:
                    chosen_color = key.lower()
                    card = game_state['your_hand'][selected_index]
                    send_message(client, {
                        TYPE: PLAY_CARD,
                        DATA: {
                            "card": card,
                            "chosen_color": chosen_color
                        }
                    })

                    color_select_mode = False
                    chosen_color = None
            else:
                if key is None:
                    continue
                if key == KEY_LEFT:
                    selected_index = (selected_index - 1) % len(game_state['your_hand'])
                elif key == KEY_RIGHT:
                    selected_index = (selected_index + 1) % len(game_state['your_hand'])
                elif key == KEY_ENTER:
                    card = game_state['your_hand'][selected_index]
                    if card['color'] is None:
                        color_select_mode = True
                    else:
                        send_message(client, {
                            TYPE: PLAY_CARD,
                            DATA: {
                                "card": card,
                                "chosen_color": None
                            }
                        })
                elif key == 'd':
                    send_message(client, {
                        TYPE: DRAW_CARD,
                        DATA: {}
                    })
        else:
            time.sleep(0.1)


threading.Thread(target=receiver, daemon=True).start()
threading.Thread(target=graphics, daemon=True).start()
threading.Thread(target=inputloop, daemon=True).start()

try:
    while not exitf:
        time.sleep(1)
except KeyboardInterrupt:
    exitf = True
    client.close()
    try:
        client.shutdown(socket.SHUT_RDWR)
        client.close()
    except Exception:
        pass
finally:
    console.clear()
    console.print("[green]Disconnected. Goodbye![/green]")
