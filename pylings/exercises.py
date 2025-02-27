from shutil import copy
import subprocess
from sys import exit
from pylings.config import ConfigManager
from pylings.constants import (
     BACKUP_DIR, DONE_MESSAGE, EXERCISE_DONE, EXERCISE_ERROR, 
     EXERCISE_OUTPUT,EXERCISES_DIR, GIT_MESSAGE, GIT_ADD, GIT_COMMIT,
     HYPERLINK, SOLUTIONS_DIR,SOLUTION_LINK
)

class ExerciseManager:
    """Manages exercises, including initialization, progression, resets, and output retrieval."""

    def __init__(self):
        """Initializes the ExerciseManager and precomputes exercise states."""
        self.exercises = {}  # Dictionary to store exercise state
        self.current_exercise = None
        self.completed_count = 0
        self.config_manager = ConfigManager()
        self.first_time = self.config_manager.check_first_time()
        self.watcher = None  # Reference to watcher for restarting
        self.show_hint = False  # Flag to control hint display
        self.initialize_exercises()
        self.padding = len(str(max(EXERCISES_DIR.rglob("*.py"), key=lambda x: len(str(x)))))
        self.padding_name = len(max(EXERCISES_DIR.rglob("*.py"), key=lambda x: len(x.name)).name)  # Set padding by fetching longest filename
        
    def initialize_exercises(self):
        """Runs all exercises at launch and stores their state."""
        exercises = sorted(EXERCISES_DIR.rglob("*.py"))
         # Set padding by directly fetching the longest path

        for ex in exercises:
            result = self.run_exercise(ex)
            status = "DONE" if result.returncode == 0 else "PENDING"

            self.exercises[ex.name] = {
                "path": ex,
                "status": status,
                "output": result.stdout if result.returncode == 0 else "",
                "error": result.stderr if result.returncode != 0 else None,
                "hint": self.config_manager.get_hint(ex)  # Fetch hint from config
            }

            if status == "DONE":
                self.completed_count += 1

        # Ensure first exercise is intro1.py if first time, else pick first pending exercise
        intro_exercise = EXERCISES_DIR / "00_intro" / "intro1.py"
        if self.first_time and intro_exercise.exists():
            self.current_exercise = intro_exercise
        else:
            self.current_exercise = self.get_next_pending_exercise()

    def shutdown_due_to_timeout(self):
            """Shuts down the application gracefully after timeout."""
            print("\nApplication timed out due to inactivity. Exiting...")
            if self.watcher:
                self.watcher.stop()
            exit(0)

    def run_exercise(self, exercise):
        """Runs an exercise file and captures its output and errors with a timeout."""
        try:
            process = subprocess.Popen(
                ["python", str(exercise)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            try:
                stdout, stderr = process.communicate(timeout=10)  # 10-second timeout
                return subprocess.CompletedProcess(
                    args=[exercise], returncode=process.returncode, stdout=stdout, stderr=stderr
                )
            except subprocess.TimeoutExpired:
                process.kill()  # Forcefully terminate the process
                stdout, stderr = process.communicate()
                return subprocess.CompletedProcess(
                    args=[exercise], returncode=1, stdout=stdout, stderr="Exercise timed out due to possible infinite loop."
                )
        except Exception as e:
            return subprocess.CompletedProcess(
                args=[exercise], returncode=1, stdout="", stderr=str(e)
            )

    def update_exercise_output(self):
        """Re-runs the current exercise to update its output and status."""
        if self.current_exercise:
            result = self.run_exercise(self.current_exercise)
            prev_status = self.exercises[self.current_exercise.name]["status"]
            new_status = "DONE" if result.returncode == 0 else "PENDING"

            result = self.run_exercise(self.current_exercise)
            self.exercises[self.current_exercise.name]["status"] = "DONE" if result.returncode == 0 else "PENDING"
            self.exercises[self.current_exercise.name]["output"] = result.stdout if result.returncode == 0 else ""
            self.exercises[self.current_exercise.name]["error"] = result.stderr if result.returncode != 0 else None

            # Update completed count if status changes from PENDING to DONE
            if prev_status != "DONE" and new_status == "DONE":
                self.completed_count += 1

    def check_all_exercises(self, exercises):
        """Updates all exercises without changing the currently selected exercise."""
        current_exercise_path = self.current_exercise  # Preserve current selection

        for ex in exercises:
            result = self.run_exercise(ex["path"])  # Run the exercise
            prev_status = ex["status"]
            new_status = "DONE" if result.returncode == 0 else "PENDING"

            # Update exercise details
            ex["status"] = new_status
            ex["output"] = result.stdout if result.returncode == 0 else ""
            ex["error"] = result.stderr if result.returncode != 0 else None

            # Update completed count
            if prev_status != "DONE" and new_status == "DONE":
                self.completed_count += 1
            elif prev_status == "DONE" and new_status != "DONE":
                self.completed_count -= 1

        # Restore the originally selected exercise
        self.current_exercise = current_exercise_path

        

    def get_next_pending_exercise(self):
        """Finds the next exercise that is still PENDING."""
        for ex_data in self.exercises.values():
            if ex_data["status"] == "PENDING":
                return ex_data["path"]
        return None  # No pending exercises left

    def next_exercise(self):
        """Advances to the next exercise in the list and restarts the watcher."""
        exercises = list(self.exercises.values())
        current_index = next((i for i, ex in enumerate(exercises) if ex["path"] == self.current_exercise), None)

        if current_index is not None and current_index + 1 < len(exercises):
            # Move to the next exercise in the list
            self.current_exercise = exercises[current_index + 1]["path"]
            self.show_hint = False

            # Run the exercise and restart watcher
            self.update_exercise_output()
            if self.watcher:
                self.watcher.restart(str(self.current_exercise.parent))
        else:
            print("All exercises completed!")

    def reset_exercise(self):
        """Resets the current exercise to its backup version and updates progress."""
        if self.current_exercise:
            backup_path = BACKUP_DIR / self.current_exercise.relative_to(EXERCISES_DIR)
            if backup_path.exists():
                copy(backup_path, self.current_exercise)
                result = self.run_exercise(self.current_exercise)
                prev_status = self.exercises[self.current_exercise.name]["status"]
                self.update_exercise_output()

                # Decrement completed count if a completed exercise is reset
                if prev_status == "DONE":
                    self.completed_count -= 1
            else:
                print(f"No backup found for {self.current_exercise}.")
        else:
            print("No current exercise to reset.")

    def print_exercise_output(self):
        """Displays the output of the current exercise."""
        if self.current_exercise:
            ex_data = self.exercises[self.current_exercise.name]
            if ex_data["status"] == "DONE":
                print(f"\n{EXERCISE_OUTPUT(ex_data['output'])}")
                print(f"\n\n{EXERCISE_DONE}")
                print(
                    f"{SOLUTION_LINK(self.get_solution())}"
                )
                print(
                    f"{DONE_MESSAGE}"
                )
                print(
                    f"{GIT_MESSAGE}"
                )
                print(
                    f"\n\t{GIT_ADD(self.current_exercise)}"
                )
                print(
                    f'\n\t{GIT_COMMIT(self.current_exercise.name)}\n'
                )
            else:
                print(f"{EXERCISE_ERROR(ex_data['error'])}")
                if self.show_hint:
                    print(f"\n{ex_data['hint']}\n")
        else:
            print("No current exercise.")

    def get_solution(self):
        """Return the solution file path for the given current exercise."""
        if not self.current_exercise:
            return None
        try:
            relative_path = self.current_exercise.relative_to(EXERCISES_DIR)
            solution_path = SOLUTIONS_DIR / relative_path
            if solution_path.exists():
                return solution_path
            return None
        except Exception as e:
            print(f"Error resolving solution path: {e}")
            return None

    def toggle_hint(self):
        """Toggles the hint display flag."""
        self.show_hint = not self.show_hint