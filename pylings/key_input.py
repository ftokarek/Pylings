"""pylings/pylings/key_input.py: Handles key input for pylings

This module manages user key inputs for the Pylings project using cross-platform support
with `msvcrt` on Windows and `termios` on Unix systems.

Classes:
    KeyInput: Handles the capturing of single key presses.

Functions:
    None
"""
from sys import platform, stdin

if platform.startswith('win'):
    import msvcrt
else:
    import termios
    import tty

class KeyInput:
    """Handles capturing single key inputs from the user with cross-platform support."""
    def __init__(self):
        """Initializes the KeyInput handler."""
        pass

    def get_key(self):
        if platform.startswith('win'):
            key = msvcrt.getch()
            if key in [b'\xe0', b'\x00']:
                key = msvcrt.getch()  # Get the actual key code after the prefix
            else:
                return key.decode('utf-8')
            return key
        else:
            fd = stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                key = stdin.read(1)
                if key == '\x1b':
                    key += stdin.read(2)  # Read full escape sequence for arrow keys
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return key.encode() if isinstance(key, str) else key