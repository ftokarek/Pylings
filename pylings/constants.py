"""constants.py: Shared constants for pylings project"""

from pathlib import Path

# FILE PATHS
EXERCISES_DIR = Path("exercises")
SOLUTIONS_DIR = Path("solutions")
BACKUP_DIR = Path("backups")
CONFIG_FILE = Path("pylings/config/config.toml")
FIRSTTIME_FILE = Path("venv/.firsttime")

# COLOURS
GREEN = "\033[92m"
LIGHT_BLUE = "\033[94m"
ORANGE = "\033[33m"
RED = "\033[91m"
RESET_COLOR = "\033[0m"

# FORMATTING CONTROLS
CLEAR_SCREEN = f"\033[2J\033[H"
RESET_UNDERLINE = "\033[24m"
HYPERLINK = (
    lambda path: f"{LIGHT_BLUE}{UNDERLINE}{path}{RESET_UNDERLINE}{RESET_COLOR}"
)
SOLUTION_LINK = (
    lambda path: f"Solution for comparison: {GREEN}{UNDERLINE}{path}{RESET_UNDERLINE}{RESET_COLOR}"
)
UNDERLINE = "\033[4m"

# MESSAGES
DONE_MESSAGE = f"When you are done experimenting, remove 'FIXME' from current exercise and press `{LIGHT_BLUE}n{RESET_COLOR}` for the next exercise 🐍\n"
EXERCISE_DONE = f"{GREEN}Exercise done ✔{RESET_COLOR}"
EXERCISE_ERROR = (
    lambda error: f"{RED}{error}{RESET_COLOR}"
)
EXERCISE_OUTPUT = (
    lambda output: f"{UNDERLINE}Output{RESET_UNDERLINE}\n{output}"
)
GIT_ADD = (
    lambda path : f"{LIGHT_BLUE} git add {HYPERLINK(path)}{RESET_COLOR}"
)
GIT_COMMIT = (
    lambda exercise_name: f"{LIGHT_BLUE} git commit -m \"mod: complete {exercise_name}\"{RESET_COLOR}"
)
GIT_MESSAGE = f"If you forked pylings you can use {UNDERLINE}git{RESET_UNDERLINE} to keep track of your progress:"
HINT_TITLE = f"{GREEN}{UNDERLINE}Hint:{RESET_UNDERLINE}{RESET_COLOR}"
NO_HINT_MESSAGE = f"{RED}No hint found for the current exercise.{RESET_COLOR}"
NO_EXERCISE_MESSAGE = f"{RED}No current exercise selected.{RESET_COLOR}"

# LIST STATUS FORMATTING
CURRENT = f"{RED}>>>>>>>{RESET_COLOR}"
PENDING = f"{ORANGE}PENDING{RESET_COLOR}"
SELECTOR = f"{GREEN}*{RESET_COLOR}"
DONE = f"{GREEN}DONE   {RESET_COLOR}"

# MENU OPTIONS
CHECK = f"{LIGHT_BLUE}c{RESET_COLOR}:check all" 
NEXT = f"{LIGHT_BLUE}n{RESET_COLOR}:next" 
HINT = f"{LIGHT_BLUE}h{RESET_COLOR}:hint" 
RESET = f"{LIGHT_BLUE}r{RESET_COLOR}:reset exercise"
LIST = f"{LIGHT_BLUE}l{RESET_COLOR}:list"
QUIT = f"{LIGHT_BLUE}q{RESET_COLOR}:quit ?"
NAVIGATE =f"{LIGHT_BLUE}↑/↓/home/end{RESET_COLOR}:navigate"
SELECT =f"{LIGHT_BLUE}s{RESET_COLOR}:select"