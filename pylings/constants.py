"""constants.py: Shared constants for pylings project"""

from pathlib import Path

# FILE PATHS
BASE_DIR = Path.cwd()
CONFIG_FILE = Path(__file__).parent / "config" / "config.toml"
EXERCISES_DIR = BASE_DIR / "exercises"
SOLUTIONS_DIR = BASE_DIR / "solutions"
BACKUP_DIR = Path(__file__).parent / Path("backups")
PYLINGS_TOML = BASE_DIR / ".pylings.toml"
DEBUG_PATH = BASE_DIR / ".pylings_debug.log"
IGNORED_DIRS = {"__pycache__", ".git"}
IGNORED_FILES = {".DS_Store", "Thumbs.db"}

# MARKUP STYLES FOR TEXTUAL
GREEN = "[bold green]"
LIGHT_BLUE = "[bold lightblue]"
ORANGE = "[bold orange]"
RED = "[bold red]"
RESET_COLOR = "[/]"
UNDERLINE = "[underline]"

# FORMATTING CONTROLS
CLEAR_SCREEN = "\033[2J\033[H"

# MESSAGES
DONE_MESSAGE = f"When you are done experimenting press {LIGHT_BLUE}n{RESET_COLOR} for the next exercise 🐍\n"
EXERCISE_DONE = f"{GREEN}Exercise done ✔{RESET_COLOR}"
EXERCISE_ERROR = lambda error: f"{RED}{error}{RESET_COLOR}"
EXERCISE_OUTPUT = lambda output: f"{UNDERLINE}Output{RESET_COLOR}\n{output}"
HINT_TITLE = f"{GREEN}{UNDERLINE}Hint:{RESET_COLOR}"
NO_HINT_MESSAGE = f"{RED}No hint found for the current exercise.{RESET_COLOR}"
NO_EXERCISE_MESSAGE = f"{RED}No current exercise selected.{RESET_COLOR}"
REPOSITORY = "https://github.com/CompEng0001/pylings"

# LIST STATUS FORMATTING
PENDING = f"{ORANGE}PENDING{RESET_COLOR}"
DONE = f"{GREEN}DONE   {RESET_COLOR}"

# MENU OPTIONS
CHECK = f"{LIGHT_BLUE}c{RESET_COLOR}:check all"
NEXT = f"{LIGHT_BLUE}n{RESET_COLOR}:next"
HINT = f"{LIGHT_BLUE}h{RESET_COLOR}:hint"
RESET = f"{LIGHT_BLUE}r{RESET_COLOR}:reset"
LIST = f"{LIGHT_BLUE}l{RESET_COLOR}:toggle list"
QUIT = f"{LIGHT_BLUE}q{RESET_COLOR}:quit ?"
NAVIGATE = f"{LIGHT_BLUE}↑/↓{RESET_COLOR}:navigate"
SELECT = f"{LIGHT_BLUE}s{RESET_COLOR}:select"

# NAVIGATION
MAIN_VIEW_NEXT = f"{NEXT} / {RESET} / {HINT} / {LIST} / {QUIT}"
MAIN_VIEW = f"{RESET} / {HINT} / {LIST} / {QUIT}"
LIST_VIEW_NEXT = f"{NEXT} / {RESET} / {HINT} / {LIST} / {SELECT} / {CHECK} / {NAVIGATE}  / {QUIT}"
LIST_VIEW = f"{RESET} / {HINT} / {LIST} / {SELECT} / {CHECK} / {NAVIGATE}  / {QUIT}"

# END MESSAGE
FINISHED = f"""
{GREEN}
+---------------------------------------------------------+
|            You made it to the Fi-Ni!-sh line!            |
+---------------------------------------------------------+
                                                       .
        .++         \\/                             :***-
   -=.   +@=        .:                             .+@=.
    -*+-.:+%*:     :*=                           :+#*:
      :=**+*@@#=:. :#+             ::  .:   .:=*%@%+:
         .:-*@@@@%#+##=:-=--=+----*%%*#*+=+*%@@@@@*:
             =#@@@%#%@@@@@@@@@@@@@@@@@@#-:..=**=..
               -#=  -#@@%@@@@@@@@@@@%@#-
               .:    :*@@@@@@@@@@@@@@@=
                      -@@#**%@@#++*@@@-
                     .=@@-   ##:   #@@=l
                      =@@%%%%%%%%%%@@@=
                      -@@@@@@@@@@@@@@@+
                      :#@@@@@@@@@@@@%#=.
                       .+*%@@@@@@@#-.
                          .::=#*:..

\nCongratulations, you have successfully completed all pyling exercises!
\nThank you for learning Python with Pylings
\nIf you'd like to contribute or add more exercises, vist the repository\n:
  - {REPOSITORY}"
{RESET_COLOR}
"""