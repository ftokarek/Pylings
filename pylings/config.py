"""pylings/pylings/config.py: Handles configuration management for pylings

This module manages configuration settings for the Pylings project, including
handling first-time setup, retrieving exercise hints, and specifying initial exercises.

Classes:
    ConfigManager: Manages reading and writing configuration data, and provides
                   helper methods for exercise management.

Functions:
    None

"""
from os import path
from sys import argv
from toml import dump,load
from pylings.constants import (
    CLEAR_SCREEN,
    CONFIG_FILE,
    DEBUG_PATH,
    PYLINGS_TOML,
    HINT_TITLE,
    NO_EXERCISE_MESSAGE,
    NO_HINT_MESSAGE,
)
from pylings.utils import PylingsUtils

import logging
logging.basicConfig(filename=DEBUG_PATH, level=logging.DEBUG, format="%(asctime)s - %(message)s")
class ConfigManager:
    """Handles loading, updating, and accessing configuration settings."""

    def __init__(self):
        """Initializes the configuration manager by reading the config file."""
        logging.debug(f"ConfigManager.__init__: Entered")
        self.config = self.load_config()

    def load_config(self):
        logging.debug(f"ConfigManager.load_config: Entered")
        logging.debug(f"ConfigManager.load_config.CONFIG_FILE:{CONFIG_FILE}")
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return load(f)
    
    def check_first_time(self):
        """Checks and handles the first-time setup, then updates the firsttime flag."""
        logging.debug("ConfigManager.check_first_time: Entered")
        args = PylingsUtils.parse_args()
        num_args = len(argv) - 1

        if num_args == 0 or (args.command == "run" and hasattr(args, "file")):
            try:
                with open(PYLINGS_TOML, "r", encoding="utf-8") as f:
                    self.config = load(f)
                if self.config["workspace"]["firsttime"] == True:
                    #Update firsttime to false
                    self.config["workspace"]["firsttime"] = False
                    with open(PYLINGS_TOML, "w", encoding="utf-8") as f:
                        dump(self.config, f)

                    self.config = self.load_config()
                    welcome_message = self.config["settings"]["welcome_message"]
                    print(CLEAR_SCREEN, end="", flush=True)
                    print("Welcome message:", welcome_message)
                    input("\nPress Enter to continue...")


                    return True

                return False

            except FileNotFoundError:
                print(f"Error: The file {PYLINGS_TOML} does not exist.")
                return None

        return None

    def get_lasttime_exercise(self):
        logging.debug(f"ConfigManager.get_lasttime_exercise: Entered")
        try:
            with open(PYLINGS_TOML, "r", encoding="utf-8") as f:
                self.config = load(f)

            lasttime_exercise = self.config["workspace"]["current_exercise"]
            logging.debug(f"ConfigManager.get_lasttime_exercise.line.lasttime_exercise: {lasttime_exercise}")
            return lasttime_exercise

        except FileNotFoundError:
            print(f"Error: The file {PYLINGS_TOML} does not exist.")
            return "00_intro/intro1.py"
        except KeyError:
            print(f"Error: 'current_exercise' not found in [workspace] section of {PYLINGS_TOML}")
            return "00_intro/intro1.py"


    def set_lasttime_exercise(self,current_exercise):
        logging.debug(f"ConfigManager.set_lasttime_exercise: Entered")
        try:
            with open(PYLINGS_TOML, "r", encoding="utf-8") as f:
                self.config = load(f)
                #Update firsttime to false
                self.config["workspace"]["current_exercise"] = str(current_exercise)
                with open(PYLINGS_TOML, "w", encoding="utf-8") as f:
                    dump(self.config, f)
        except FileNotFoundError:
            print(f"Error: The file {PYLINGS_TOML} does not exist.")
            return None

    def get_hint(self, current_exercise):
        """Retrieves the hint for the given exercise from the config file.

        Args:
            current_exercise (Path): The current exercise file path.

        Returns:
            str: The hint for the exercise, or an error message if no hint is found.
        """
        logging.debug(f"ConfigManager.get_hint: Entered")
        if not current_exercise:
            return f"{NO_EXERCISE_MESSAGE}"

        base_name = path.basename(str(current_exercise))
        ce_name = path.splitext(base_name)[0].strip()

        for section in self.config.keys():
            if section.startswith("exercise_"):
                exercise_name = self.config[section]["name"].strip('"').strip('"')
                if exercise_name == ce_name:
                    return (
                        f"{HINT_TITLE}\n"
                        + self.config[section]["hint"]
                    )
        return f"{NO_HINT_MESSAGE}"