from sys import exit
from threading import Thread
from pylings.exercises import ExerciseManager
from pylings.utils import PylingsUtils
from pylings.watcher import Watcher
from pylings.ui import PylingsUI
from pylings.constants import DEBUG_PATH
from pylings.config import ConfigManager

import logging
logging.basicConfig(filename=DEBUG_PATH, level=logging.DEBUG, format="%(asctime)s - %(message)s")

def shutdown(exercise_manager, watcher):
    """Gracefully shut down and release all resources."""
      
    print("\nShutting down and releasing resources.")
    if watcher:
        watcher.stop()
    if exercise_manager:
        exercise_manager.watcher = None
    if PylingsUtils.is_in_virtual_env():
        PylingsUtils.print_exit_message()
    exit(0)

def main():
    """Main function to run the Pylings application."""
    args = PylingsUtils.parse_args()
    if args.command == "init":
        PylingsUtils.handle_args(args, None, None)
        return

    if args.command != "init" and not PylingsUtils.is_pylings_toml():
        exit(1)

    exercise_manager = ExerciseManager()
    watcher = Watcher(exercise_manager, None) 
    exercise_manager.watcher = watcher   

    if PylingsUtils.handle_args(args, exercise_manager, watcher):
        exercise_manager.update_exercise_output()

    app = PylingsUI(exercise_manager)
    watcher.ui_manager = app 
      
    if exercise_manager.current_exercise:
        watcher.start(str(exercise_manager.current_exercise.parent))

    try:
        app.run()
    except KeyboardInterrupt:
        shutdown(exercise_manager, watcher)

if __name__ == "__main__":
    main()