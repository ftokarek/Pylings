from os import name, path, getpid, getenv
from psutil import pid_exists
from sys import prefix, exit
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path
import toml
from pylings.constants import PYPROJECT_FILE, REPOSITORY

class PylingsUtils:
    """Utility class for virtual environment management and argument handling."""

    LOCK_FILE = path.join(prefix, ".pylings.lock")

    @staticmethod
    def parse_args():
        """Parse command-line arguments with Rustlings-style output."""
        parser = ArgumentParser(
            prog="pylings",
            description="Pylings is a collection of small exercises to get you used to writing and reading Python code.",
            formatter_class=RawTextHelpFormatter,
        )

        parser.add_argument("-v", "--version", action="store_true", help="Get version and information about Pylings.")

        subparsers = parser.add_subparsers(dest="command")

        run_parser = subparsers.add_parser("run", help="Run pylings at the supploed exercise.")
        run_parser.add_argument("file", type=str, help="Path to the exercise file.")

        dry_parser = subparsers.add_parser("dry-run", help="Dry-run an exercise non-interactively.")
        dry_parser.add_argument("file", type=str, help="Path to the exercise file.")

        solutions_parser = subparsers.add_parser("solution", help="Check solution for supplied exercise non-interactively.")
        solutions_parser.add_argument("file", type=str, help="Path to the solution file.")

        return parser.parse_args()


    @staticmethod
    def handle_args(args, exercise_manager, watcher):
        """Handle command-line arguments for running and testing exercises."""

        def shutdown():
            """Shut down after handling an argument."""
            if watcher:
                watcher.stop()
            PylingsUtils.print_exit_message()
            exit(0)

          
        if args.version:
            version, license_text = PylingsUtils.get_pylings_info()
            print(f"\nPylings Version: {version}")
            print(f"Licence: {license_text}")
            print(f"Repo: {REPOSITORY}")
            exit(0)

         
        if not args.command:
            return False   

        if args.command == "dry-run":
            exercise_path = Path(args.file)
            if exercise_path.exists() and exercise_path.is_file():
                exercise_manager.current_exercise = exercise_path
                exercise_manager.update_exercise_output()
                exercise_manager.print_exercise_output()
                shutdown()
            else:
                print(f"Invalid exercise path: {args.file}")
                shutdown()

        elif args.command == "solution":
            solution_path = Path(args.file)
            if solution_path.exists() and solution_path.is_file():
                result = exercise_manager.run_exercise(solution_path)
                output = result.stdout if result.returncode == 0 else result.stderr
                print(output)
                shutdown()
            else:
                print(f"Invalid solution path: {args.file}")
                shutdown()

        elif args.command == "run":
            exercise_path = Path(args.file)
            if exercise_path.exists() and exercise_path.is_file():
                exercise_manager.current_exercise = exercise_path
                exercise_manager.update_exercise_output()
                exercise_manager.print_exercise_output()
                return False   
            else:
                print(f"Invalid exercise path: {args.file}")
                shutdown()

        return False   

    @staticmethod
    def get_pylings_info():
        """Reads the Pylings version and license from pyproject.toml."""
        pyproject_path = PYPROJECT_FILE

        if pyproject_path.exists():
            try:
                pyproject_data = toml.load(pyproject_path)
                version = pyproject_data["project"].get("version", "Unknown Version")
                license_text = pyproject_data["project"].get("license", {}).get("text", "Unknown License")
                return version, license_text
            except Exception as e:
                print(f"Error reading version info: {e}")
                return "Unknown Version", "Unknown License"
        return "Unknown Version", "Unknown License"

    @staticmethod
    def is_in_virtual_env():
        """Check if the script is running inside a virtual environment."""
        return getenv("VIRTUAL_ENV") is not None

    @staticmethod
    def create_lock_file(lock_file):
        """Create a lock file with the current PID."""
        with open(lock_file, "w") as f:
            f.write(str(getpid()))

    @staticmethod
    def get_lock_file_path():
        """Returns the path for the lock file in the virtual environment."""
        return path.join(prefix, ".pylings.lock")


    @staticmethod
    def overwrite_lock_file(lock_file):
        """Overwrite the stale lock file with the current PID."""
        with open(lock_file, "w") as f:
            f.write(str(getpid()))

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
             
            PylingsUtils.create_lock_file(lock_file)

    @staticmethod
    def print_venv_instruction():
        """Print instructions on how to activate the virtual environment."""
        print("\nTo use pylings you must be run inside a virtual environment!")
        if name == "nt":   
            print("➡ To activate the venv, run:")
            print("   source venv\\Scripts\\activate")
        else:
            print("➡ To activate the venv, run:")
            print("   source venv/bin/activate")
        exit(1)   

    @staticmethod
    def print_exit_message():
        print("\nThanks for using Pylings!")
        print("➡ Remember to run `deactivate` to exit the virtual environment")
        if name == "nt":   
            print("➡ When you come back, run:")
            print("  ➡ source venv/Scripts/activate")
        else:
            print("➡ When you come back, run:")
            print("  ➡ source venv/bin/activate")
        exit(1)