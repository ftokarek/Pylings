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
from toml import load
from pylings.constants import (
    CLEAR_SCREEN,
    CONFIG_FILE,
    FIRSTTIME_FILE,
    HINT_TITLE,
    NO_EXERCISE_MESSAGE,
    NO_HINT_MESSAGE,
)
from pylings.utils import PylingsUtils

class ConfigManager:
    """Handles loading, updating, and accessing configuration settings."""

    def __init__(self):
        """Initializes the configuration manager by reading the config file."""
        self.config = self.load_config()

    def load_config(self):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return load(f)

    def check_first_time(self):
        """Checks and handles the first-time setup, then updates the firsttime flag."""
        args = PylingsUtils.parse_args()
        num_args = len(argv) - 1   

        if num_args == 0 or (args.command == "run" and hasattr(args, "file")):
            try:
                with open(FIRSTTIME_FILE, "r+", encoding="utf-8") as f:
                    lines = f.readlines()
                    f.seek(0)   
                    for line in lines:
                        if "firsttime=true" in line:
                             
                            welcome_message = self.config["settings"]["welcome_message"]
                            print(CLEAR_SCREEN, end="", flush=True)
                            print("Welcome message:", welcome_message)
                            input("\nPress Enter to continue...")

                             
                            f.write(line.replace("firsttime=true", "firsttime=false"))
                            return True
                        else:
                            return None
            except FileNotFoundError:
                print(f"Error: The file {FIRSTTIME_FILE} does not exist.")
                return None
        return None


    def get_hint(self, current_exercise):
        """Retrieves the hint for the given exercise from the config file.

        Args:
            current_exercise (Path): The current exercise file path.

        Returns:
            str: The hint for the exercise, or an error message if no hint is found.
        """
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