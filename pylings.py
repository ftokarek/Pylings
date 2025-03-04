from sys import exit
from threading import Thread
from pylings.exercises import ExerciseManager
from pylings.key_input import KeyInput
from pylings.ui import UIManager
from pylings.utils import PylingsUtils
from pylings.watcher import Watcher

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
     
    if not PylingsUtils.is_in_virtual_env():
        PylingsUtils.print_venv_instruction()

    PylingsUtils.ensure_single_instance()   

    exercise_manager = ExerciseManager()
    ui_manager = UIManager(exercise_manager)
    key_input = KeyInput()

     
    watcher = Watcher(exercise_manager, ui_manager)
    exercise_manager.watcher = watcher   
    watcher_thread = Thread(target=watcher.start, daemon=True)

    if exercise_manager.current_exercise:
        watcher_thread.start()
    
    args = PylingsUtils.parse_args()
    
     
    if PylingsUtils.handle_args(args, exercise_manager, watcher):
        return   
    
    try:
        while True:
            ui_manager.show_menu()
            choice = key_input.get_key().strip()

            if choice in ("n", b'n') and exercise_manager.current_exercise:
                exercise_manager.next_exercise()
            elif choice in ("r", b'r'):
                exercise_manager.reset_exercise()
            elif choice in ("h", b'h'):
                exercise_manager.toggle_hint()
            elif choice in ("l", b'l'):
                ui_manager.show_all_exercises()
            elif choice in ("q", b'q'):
                watcher.stop()
                if watcher_thread.is_alive():
                    watcher_thread.join(timeout=0.2)

                PylingsUtils.print_exit_message()
                exit(0)

    except KeyboardInterrupt:
        shutdown(exercise_manager, watcher)

if __name__ == "__main__":
    main()