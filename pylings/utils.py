from os import name, path, getpid, getenv
from psutil import pid_exists
from sys import prefix, exit
from argparse import ArgumentParser
from pathlib import Path

class PylingsUtils:
    """Utility class for virtual environment management and argument handling."""

    LOCK_FILE = path.join(prefix, ".pylings.lock")  # Lock file in virtual environment directory

    @staticmethod
    def is_in_virtual_env():
        """Check if the script is running inside a virtual environment."""
        return getenv("VIRTUAL_ENV") is not None

    @staticmethod
    def print_venv_instruction():
        """Print instructions on how to activate the virtual environment."""
        print("\n❌ To use pylings you must be run inside a virtual environment!")
        if name == "nt":  # Windows
            print("➡ To activate the venv, run:")
            print("   source venv\\Scripts\\activate")
        else:  # macOS/Linux
            print("➡ To activate the venv, run:")
            print("   source venv/bin/activate")
        exit(1)  # Exit since we are not in a venv

    @staticmethod
    def print_exit_message():
        print("\nThanks for using Pylings!")
        print("➡ Remember to run `deactivate` to exit the virtual environment")
        if name == "nt":  # Windows
            print("➡ When you come back, run:")
            print("  ➡ source venv/Scripts/activate")
        else:  # macOS/Linux
            print("➡ When you come back, run:")
            print("  ➡ source venv/bin/activate")
        exit(1)

    @staticmethod
    def parse_args():
        """Parse command-line arguments."""
        parser = ArgumentParser(description="Run Pylings exercises.")
        parser.add_argument('--solution', type=str, help='Path to the solution exercise to test and exit')
        parser.add_argument('--test', type=str, help='Path to the exercise to test and exit')
        parser.add_argument('--run', type=str, help='Path to the exercise to run pylings with')
        return parser.parse_args()
    
    @staticmethod
    def get_lock_file_path():
        """Returns the path for the lock file in the virtual environment."""
        return path.join(prefix, ".pylings.lock")

    @staticmethod
    def ensure_single_instance():
        """Ensure only one instance of Pylings runs in the current virtual environment."""
        lock_file = PylingsUtils.get_lock_file_path()

        if path.exists(lock_file):
            with open(lock_file, "r") as f:
                pid = int(f.read().strip())
                if pid_exists(pid):
                    print(f"Another instance of Pylings is already running (PID {pid}). Exiting.")
                    exit(1)
                else:
                    PylingsUtils.overwrite_lock_file(lock_file)

        else:
            # Lock file doesn't exist, create it
            PylingsUtils.create_lock_file(lock_file)

    @staticmethod
    def create_lock_file(lock_file):
        """Create a lock file with the current PID."""
        with open(lock_file, "w") as f:
            f.write(str(getpid()))

    @staticmethod
    def overwrite_lock_file(lock_file):
        """Overwrite the stale lock file with the current PID."""
        with open(lock_file, "w") as f:
            f.write(str(getpid()))

    @staticmethod
    def handle_args(args, exercise_manager, watcher):
        """Handle command-line arguments for testing and running exercises."""
        def shutdown():
            """Shut down after handling an argument."""
            if watcher:
                watcher.stop()
            PylingsUtils.print_exit_message()
            exit(0)

        if args.test:
            exercise_path = Path(args.test)
            if exercise_path.exists() and exercise_path.is_file():
                exercise_manager.current_exercise = exercise_path
                exercise_manager.update_exercise_output()
                exercise_manager.print_exercise_output()
                shutdown()
            else:
                print(f"Invalid exercise path: {args.test}")
                shutdown()

        if args.solution:
            solution_path = Path(args.solution)
            if solution_path.exists() and solution_path.is_file():
                result = exercise_manager.run_exercise(solution_path)
                output = result.stdout if result.returncode == 0 else result.stderr
                print(f"{output}")
                shutdown()
            else:
                print(f"Invalid solution path: {args.solution}")
                shutdown()

        if args.run:
            exercise_path = Path(args.run)
            if exercise_path.exists() and exercise_path.is_file():
                exercise_manager.current_exercise = exercise_path
                exercise_manager.update_exercise_output()
                exercise_manager.print_exercise_output()
                return False  # Continue running the program
            else:
                print(f"Invalid exercise path: {args.run}")
                shutdown()

        return False  # No valid argument provided