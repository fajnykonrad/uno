import json
import sys
import os

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

import os

if os.name == "nt":
    import msvcrt
    def get_key():
        if not msvcrt.kbhit():
            return None

        ch = msvcrt.getwch()

        # Arrow keys come as two characters
        if ch in ("\x00", "\xe0"):
            ch2 = msvcrt.getwch()
            return ch + ch2

        return ch

    LEFT = ("\x00K", "\xe0K")
    RIGHT = ("\x00M", "\xe0M")
    ENTER = "\r"  
else:
    import termios
    import tty
    import select

    def get_key():
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            if not select.select([sys.stdin], [], [], 0.05)[0]:
                return None
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

    LEFT = "\x1b[D"
    RIGHT = "\x1b[C"
    ENTER = "\n"
