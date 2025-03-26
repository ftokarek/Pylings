from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path
import shutil
import subprocess
import os
import logging
import toml#
from pylings.constants import PYLINGS_TOML, REPOSITORY, DEBUG_PATH

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
        init_parser.add_argument("--force", action="store_true", help="Reinitialize workspace (overwrites existing files)")

        reinit_parser = subparsers.add_parser("update", help="Update workspace with current version")
        reinit_parser.add_argument("--path", type=str, help="Target folder (default: current directory)")

        run_parser = subparsers.add_parser("run", help="Run pylings at the supplied exercise.")
        run_parser.add_argument("file", type=str, help="Path to the exercise file.")

        dry_parser = subparsers.add_parser("dry-run", help="Dry-run an exercise non-interactively.")
        dry_parser.add_argument("file", type=str, help="Path to the exercise file.")

        solutions_parser = subparsers.add_parser("solution", help="Check solution for supplied exercise non-interactively.")
        solutions_parser.add_argument("file", type=str, help="Path to the solution file.")

        return parser.parse_args()

    @staticmethod
    def handle_args(args, exercise_manager, watcher):
        """Handle command-line arguments for running and testing exercises."""

        if not args.command:
            return False
        
        if args.command == "solution":
            solution_path = Path(args.file)
            if solution_path.exists() and solution_path.is_file():
                result = exercise_manager.run_exercise(solution_path)
                output = result.stdout if result.returncode == 0 else result.stderr
                print(output)
                exit(0)
            else:
                print(f"Invalid solution path: {args.file}")
                exit(1)

        elif args.command == "dry-run":
            exercise_path = Path(args.file)
            if exercise_path.exists() and exercise_path.is_file():
                result = exercise_manager.run_exercise(exercise_path)
                output = result.stdout if result.returncode == 0 else result.stderr
                print(output)
                exit(0)
            else:
                print(f"Invalid exercise path: {args.file}")
                exit(1)

        elif args.command == "run":
            exercise_path = Path(args.file)
            if exercise_path.exists() and exercise_path.is_file():
                exercise_manager.arg_exercise = exercise_path
                return True
            else:
                print(f"Invalid exercise path: {args.file}")
                exit(1)

        return False

    @staticmethod
    def is_pylings_toml():
        for p in [Path.cwd()] + list(Path.cwd().parents):
            if (p / ".pylings.toml").exists():
                return True
        print("Not a pylings workspace.")
        print("Change to pylings workspace, if it exists, or")
        print("Run: pylings init [--path /path/to/pylings]")
        print("\t Or pylings --help")
        return False

    @staticmethod
    def get_git_status():
        if not shutil.which("git"):
            return None
        try:
            result = subprocess.run(
                ["git", "status", "--short"],
                capture_output=True,
                text=True,
                check=True
            )
            lines = result.stdout.strip().splitlines()
            return lines if lines else None
        except subprocess.CalledProcessError as e:
            print(f"Error running git status: {e}")
            return None

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

    @staticmethod 
    def get_local_version():
        """Get version from local pyproject.toml."""
        if PYLINGS_TOML.exists():
            try:
                pyproject_data = toml.load(PYLINGS_TOML)
                return pyproject_data.get("workspace", {}).get("version", "Unknown")
            except Exception as e:
                print(f"Error reading pyproject.toml: {e}")
                return "Unknown"
        return "Not in a local initialised pylings directory"

    @staticmethod
    def get_pip_package_info():
        """Get version and license from installed pip package."""
        try:
            result = subprocess.run(
                ["pip", "show", "pylings", "--verbose"],
                check=True,
                capture_output=True,
                text=True
            )
            version = "Unknown"
            license_text = "Unknown"
            github = "Unknown"
            pypiorg = "Unknown"

            for line in result.stdout.splitlines():
                if line.startswith("Version:"):
                    version = line.split(":", 1)[1].strip()
                elif line.startswith("License-Expression:"):
                    license_text = line.split(":", 1)[1].strip()
                elif line.startswith("Home-page:"):
                    github = line.split(":", 1)[1].strip()
                elif "Repository," in line:
                    pypiorg = line.split(",", 1)[1].strip()

            return version, license_text, github, pypiorg
        except subprocess.CalledProcessError:
            return "Not Installed", "N/A"