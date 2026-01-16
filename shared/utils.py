import json
import sys
import os
import atexit
import select

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

# =========================
# Cross-platform input
# =========================

KEY_LEFT = "LEFT"
KEY_RIGHT = "RIGHT"
KEY_ENTER = "ENTER"

if os.name == "nt":
    import msvcrt

    def get_key():
        if not msvcrt.kbhit():
            return None

        ch = msvcrt.getwch()

        if ch in ("\x00", "\xe0"):  # Special key
            ch2 = msvcrt.getwch()
            if ch2 == "K":
                return KEY_LEFT
            elif ch2 == "M":
                return KEY_RIGHT
            return None

        if ch == "\r":
            return KEY_ENTER

        return ch.lower()

else:
    # -------- Linux / macOS --------
    import termios
    import tty

    fd = sys.stdin.fileno()
    _orig_termios = termios.tcgetattr(fd)

    def _enable_raw():
        tty.setcbreak(fd)

    def _restore_terminal():
        termios.tcsetattr(fd, termios.TCSADRAIN, _orig_termios)
    
    def enable_input():
        _enable_raw()
    
    def disable_input():
        _restore_terminal()
    # Enable raw input ONCE

    _enable_raw()
    atexit.register(_restore_terminal)
    
    ESCAPE_MAP = {
        "\x1b[D": KEY_LEFT,
        "\x1b[C": KEY_RIGHT,
    }

    def get_key():
        if not select.select([sys.stdin], [], [], 0)[0]:
            return None

        ch = sys.stdin.read(1)

        if ch == "\x1b":
            ch += sys.stdin.read(2)
            return ESCAPE_MAP.get(ch)

        if ch in ("\n", "\r"):
            return KEY_ENTER

        return ch.lower()
    
