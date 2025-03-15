from shutil import get_terminal_size
from sys import stdout, platform
import signal

import threading
import time

from pylings.constants import (
    CLEAR_SCREEN, CHECK, CURRENT, DISABLE_WRAP, DONE, DONE_MESSAGE, EXERCISE_DONE, EXERCISE_OUTPUT,
    EXERCISE_ERROR, GREEN, GIT_ADD, GIT_COMMIT, GIT_MESSAGE,
    HINT, HYPERLINK, LIST, NAVIGATE, NEXT, PENDING,
    QUIT, RED, RESET, RESET_COLOR, SELECT, SELECTOR, SOLUTION_LINK
)
from pylings.key_input import KeyInput

class UIManager:
    """Manages the user interface display for Pylings."""
    def __init__(self, exercise_manager):
        """Initializes the UIManager with an exercise manager."""
        self.exercise_manager = exercise_manager
        self.term_width = get_terminal_size().columns
        self.term_height = get_terminal_size().lines
        self.main_menu = True

        if platform.startswith("win"):
            self.start_resize_watcher()
        else:
            signal.signal(signal.SIGWINCH, self.handle_resize)

    def handle_resize(self, signum=None, frame=None):
        """Handles terminal resizing dynamically (Linux/macOS)."""
        self.term_width = get_terminal_size().columns
        self.term_height = get_terminal_size().lines
        # TODO: This handles show_menu(), but what about when we are in show_all_exercises ?
        if self.main_menu == True:
            self.show_menu()
        else:
            self.show_all_exercises()

    def start_resize_watcher(self):
        """Starts a background thread to monitor terminal resizing (Windows)."""
        def watch_resize():
            last_size = get_terminal_size()
            while True:
                time.sleep(0.1)
                new_size = get_terminal_size()
                if new_size != last_size:
                    last_size = new_size
                    self.handle_resize()

        threading.Thread(target=watch_resize, daemon=True).start()

    def show_menu(self):
        """Displays the main menu and exercise output."""
        total = len(self.exercise_manager.exercises)
        completed_count = self.exercise_manager.completed_count
        completed_flag = self.exercise_manager.completed_flag
        self.main_menu = True

        term_width = get_terminal_size().columns
        print(CLEAR_SCREEN, end="",flush=True)
        
        if self.exercise_manager.current_exercise:
            self.print_exercise_output(self.exercise_manager)

        if completed_count == total and completed_flag == True :
            self.exercise_manager.finish()

        self.progress_bar(completed_count, total, term_width)
        
        print(f"\nCurrent exercise: {HYPERLINK(self.exercise_manager.current_exercise)}\n")
        if self.exercise_manager.current_exercise and self.exercise_manager.exercises[self.exercise_manager.current_exercise.name]["status"] == "DONE":
            print(f"\n{DISABLE_WRAP}{NEXT}/ {HINT} / {RESET} / {LIST} / {QUIT}")
        else:
            print(f"\n{DISABLE_WRAP}{HINT} / {RESET} / {LIST} / {QUIT}")

    def print_exercise_output(self,exercise_manager):
        """Displays the output of the current exercise."""
        if self.exercise_manager.current_exercise:
            self.format_output(exercise_manager)
        else:
            print("No current exercise.")

    def progress_bar(self, progress, total, term_width):
        """Displays a progress bar."""
        PREFIX = f"Progress: ["
        POSTFIX = f"]   {progress}/{total}  "
        width = term_width - len(PREFIX) - len(POSTFIX)
        filled = (width * progress) // total
        stdout.write(DISABLE_WRAP)
        stdout.write(PREFIX + GREEN + "#" * filled + RED + "-" * (width - filled) + RESET_COLOR + POSTFIX + "\n")

    def format_status(self, exercise, selected=False):
        """Formats the display line for an exercise with aligned selector and padding length."""
        status = f"{DONE}" if self.exercise_manager.exercises[exercise.name]["status"] == "DONE" else f"{PENDING}"
        current = f"{CURRENT}" if exercise == self.exercise_manager.current_exercise else "       "
        name = f"{exercise.name}"
        selector = f"{SELECTOR}" if selected else " "
        path_str = f"{HYPERLINK(exercise)}"

        padding_length = self.exercise_manager.padding - len(str(exercise)) + 2
        padding = " " * padding_length
        padding_name = " " * (self.exercise_manager.padding_name - len(exercise.name) + 2)
        return f"{DISABLE_WRAP} {selector} {current}   {status}    {name}{padding_name}     {path_str}{padding}{selector}"

    def format_output(self,exercise_manager):
        ex_data = self.exercise_manager.exercises[self.exercise_manager.current_exercise.name]
        if ex_data["status"] == "DONE":
            lines = [f"\n{DISABLE_WRAP}{EXERCISE_OUTPUT(ex_data['output'])}",
                    f"\n\n{DISABLE_WRAP}{EXERCISE_DONE}",
                    f"\n{DISABLE_WRAP}{SOLUTION_LINK(self.exercise_manager.get_solution())}",
                    f"\n\n{DISABLE_WRAP}{DONE_MESSAGE}",
                    f"\n{DISABLE_WRAP}{GIT_MESSAGE}",
                    f"\n\n\t{DISABLE_WRAP}{GIT_ADD(self.exercise_manager.current_exercise)}",
                    f"\n\t{DISABLE_WRAP}{GIT_COMMIT(self.exercise_manager.current_exercise)}\n",
            ]
            output = ''.join(lines)
            print(f"{output}")
        else:
            print(f"{DISABLE_WRAP}{EXERCISE_ERROR(ex_data['error'])}")
            if self.exercise_manager.show_hint:
                print(f"\n{DISABLE_WRAP}{ex_data['hint']}\n")

    def show_all_exercises(self):
        self.main_menu = False
        """Displays an interactive list of all exercises and their completion status."""
        exercises = list(self.exercise_manager.exercises.values())
        total = len(exercises)
        completed = self.exercise_manager.completed_count
        key_input = KeyInput()
        term_width = get_terminal_size().columns
        current_row = next((idx for idx, ex in enumerate(exercises) if ex["path"] == self.exercise_manager.current_exercise), 0)

        try:
            while True:
                print(CLEAR_SCREEN, end="", flush=True)
                print("   Current   State      Name\t\t\t  Path")
                for idx, ex in enumerate(exercises):
                    print(f"{self.format_status(ex["path"],selected=(idx == current_row))}")

                self.progress_bar(completed, total, term_width)
                print(f"\n{DISABLE_WRAP}{NAVIGATE} / {SELECT} / {RESET} / {CHECK} / {QUIT}")

                key = key_input.get_key()

                if key in (b'H', b'\x1b[A') and current_row > 0:
                    current_row -= 1
                elif key in (b'P', b'\x1b[B') and current_row < len(exercises) - 1:
                    current_row += 1
                elif key in (b'G', b'\x1b[H') and current_row > 0:
                    current_row = 0
                elif key in (b'O', 'G') and current_row < len(exercises) - 1:
                    current_row = len(exercises) - 1
                elif key in ("r", b'r'):
                    self.exercise_manager.current_exercise = exercises[current_row]["path"]
                    self.exercise_manager.reset_exercise()
                elif key in ("s", b's'):
                    self.exercise_manager.current_exercise = exercises[current_row]["path"]
                    self.exercise_manager.show_hint = False
                    self.exercise_manager.update_exercise_output()

                    if self.exercise_manager.watcher:
                        print("Restarting watcher for the newly selected exercise...")
                        self.exercise_manager.watcher.restart(str(self.exercise_manager.current_exercise.parent))
                    break
                elif key in ("c", b'c'):
                        self.exercise_manager.check_all_exercises(exercises)
                elif key in ("q", b'q'):
                    break
                print("\n")

        finally:
            print(CLEAR_SCREEN, end="")