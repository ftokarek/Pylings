"""constants.py: Shared constants for pylings project"""

from pathlib import Path
import os

# FILE PATHS
BASE_DIR = Path.cwd()
CONFIG_FILE = Path(__file__).parent / "config" / "config.toml"
EXERCISES_DIR = BASE_DIR / "exercises"
SOLUTIONS_DIR = BASE_DIR / "solutions"
BACKUP_DIR = Path(__file__).parent / Path("backups")
#CONFIG_FILE = PYLINGS_DIR / Path("pylings/config/config.toml")
PYPROJECT_FILE =""# PYLINGS_DIR / Path("pyproject.toml")
FIRSTTIME_FILE = Path(__file__).parent / "firsttime"
DEBUG_PATH = Path(__file__).parent / "pylings_debug.log"

# MARKUP STYLES FOR TEXTUAL
GREEN = "[lightgreen]"
LIGHT_BLUE = "[lightblue]"
ORANGE = "[orange]"
RED = "[red]"
RESET_COLOR = "[/]"
UNDERLINE = "[underline]"

# FORMATTING CONTROLS
CLEAR_SCREEN = "\033[2J\033[H"
DISABLE_WRAP = "\033[?7l"
RESET_UNDERLINE = "\033[24m"

SOLUTION_LINK = (
    lambda path: f"Solution for comparison: {GREEN}{path}[/]"
)

# MESSAGES
DONE_MESSAGE = f"When you are done experimenting press {LIGHT_BLUE}n{RESET_COLOR} for the next exercise 🐍\n"
EXERCISE_DONE = f"{GREEN}Exercise done ✔{RESET_COLOR}"
EXERCISE_ERROR = lambda error: f"{RED}{error}{RESET_COLOR}"
EXERCISE_OUTPUT = lambda output: f"{UNDERLINE}Output{RESET_COLOR}\n{output}"
GIT_ADD = lambda path: f"{LIGHT_BLUE} git add {path}{RESET_COLOR}"
GIT_COMMIT = lambda exercise_name: f"{LIGHT_BLUE} git commit -m \"mod: complete {exercise_name}\"{RESET_COLOR}"
GIT_MESSAGE = f"If you forked pylings you can use {UNDERLINE}git{RESET_COLOR} to keep track of your progress:"
HINT_TITLE = f"{GREEN}{UNDERLINE}Hint:{RESET_COLOR}"
NO_HINT_MESSAGE = f"{RED}No hint found for the current exercise.{RESET_COLOR}"
NO_EXERCISE_MESSAGE = f"{RED}No current exercise selected.{RESET_COLOR}"
REPOSITORY = "https://github.com/CompEng0001/pylings"

# LIST STATUS FORMATTING
CURRENT = f"{RED}>>>>>>> {RESET_COLOR}"
PENDING = f"{ORANGE}PENDING{RESET_COLOR}"
SELECTOR = f"{GREEN}*{RESET_COLOR}"
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