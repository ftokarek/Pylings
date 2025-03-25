from argparse import ArgumentParser, RawTextHelpFormatter
from os import name, path
from pathlib import Path
from sys import exit
from pylings.constants import DEBUG_PATH, PYLINGS_TOML, REPOSITORY
from pylings.init import init_workspace
import toml
import logging
from logging import FileHandler
logging.basicConfig(filename=DEBUG_PATH, level=logging.DEBUG, format="%(asctime)s - %(message)s")

class PylingsUtils:
    """Utility class for virtual environment management and argument handling."""

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

        init_parser = subparsers.add_parser("init", help="Initialize a pylings workspace.")
        init_parser.add_argument("--path", type=str, help="Target folder (default: current directory)")
        init_parser.add_argument("--force", action="store_true", help="Reinitialize workspace (overwrites exercises/)")

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
                result = exercise_manager.run_exercise(exercise_path)
                output = result.stdout if result.returncode == 0 else result.stderr
                print(output)
                shutdown()
            else:
                print(f"Invalid exercise path: {args.file}")
                shutdown()

        elif args.command == "init":
            init_workspace(args.path, force=args.force)
            exit(0)

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
                exercise_manager.arg_exercise = exercise_path
                return True   
            else:
                print(f"Invalid exercise path: {args.file}")
                shutdown()

        return False   

    @staticmethod
    def get_pylings_info():
        """Reads the Pylings version and license from pyproject.toml."""
        pyproject_path = PYLINGS_TOML

        if pyproject_path.exists():
            try:
                pyproject_data = toml.load(pyproject_path)
                version = pyproject_data["workspace"].get("workspace_version", "Unknown Version")
                return version
            except Exception as e:
                print(f"Error reading version info: {e}")
                return "Unknown Version"
        return "Unknown Version"

    @staticmethod
    def is_pylings_toml():
        """Check if the current directory or parent has a .pylings.toml file."""
        from pathlib import Path
        for p in [Path.cwd()] + list(Path.cwd().parents):
            if (p / ".pylings.toml").exists():
                return True
        print("Not a pylings workspace.")
        print("Change to pylings workspace, if it exists, or")
        print("Run: pylings init [--path /path/to/pylings]")
        return False

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

    @staticmethod
    def clear_log():
        try:
            if not os.path.exists(DEBUG_PATH):
                return
            with open(DEBUG_PATH, "w") as f:
                f.truncate(0)
            logging.debug(f"PylingsUI.clear_log: Last log truncated")
        except Exception as e:
            print(f"Error checking/clearing log file: {e}")