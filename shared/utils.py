import json
import sys
import termios
import tty

BUFFER_SIZE = 4096

def send_message(conn, message):
    # Nova linia per delimitar missatges
    data = json.dumps(message) + "\n"
    conn.sendall(data.encode())


def receive_messages(conn, buffer):
    #Llegeix dades del socket i les descompon en missatges JSON
    data = conn.recv(BUFFER_SIZE).decode()
    if not data:
        return [], buffer

    buffer += data
    messages = []

    while "\n" in buffer:
        line, buffer = buffer.split("\n", 1)
        if line.strip():
            messages.append(json.loads(line))

    return messages, buffer

def get_key():
    """Read single character keypress (blocking)."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == "\x1b":  # arrow keys start with ESC
            ch += sys.stdin.read(2)  # read next 2 chars
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)