from shutil import copy
import subprocess
from sys import exit
from pylings.config import ConfigManager
from pylings.constants import (
     BACKUP_DIR, DONE_MESSAGE, EXERCISES_DIR,
     FINISHED, SOLUTIONS_DIR
)

class ExerciseManager:
    """Manages exercises, including initialization, progression, resets, and output retrieval."""

    def __init__(self):
        """Initializes the ExerciseManager and precomputes exercise states."""
        self.exercises = {}
        self.current_exercise = None
        self.completed_count = 0
        self.completed_flag = False
        self.config_manager = ConfigManager()
        self.first_time = self.config_manager.check_first_time()
        self.watcher = None  
        self.show_hint = False  
        self.initialize_exercises()
        self.padding = len(str(max(EXERCISES_DIR.rglob("*.py"), key=lambda x: len(str(x)))))
        self.padding_name = len(max(EXERCISES_DIR.rglob("*.py"), key=lambda x: len(x.name)).name)
        
    def initialize_exercises(self):
        """Runs all exercises at launch and stores their state."""
        exercises = sorted(EXERCISES_DIR.rglob("*.py"))

        for ex in exercises:
            result = self.run_exercise(ex)
            status = "DONE" if result.returncode == 0 else "PENDING"

            self.exercises[ex.name] = {
                "path": ex,
                "status": status,
                "output": result.stdout if result.returncode == 0 else "",
                "error": result.stderr if result.returncode != 0 else None,
                "hint": self.config_manager.get_hint(ex)
            }

            if status == "DONE":
                self.completed_count += 1

        intro_exercise = EXERCISES_DIR / "00_intro" / "intro1.py"
        if self.first_time and intro_exercise.exists():
            self.current_exercise = intro_exercise
        else:
            self.current_exercise = self.get_next_pending_exercise()
        
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
                stdout, stderr = process.communicate(timeout=10)
                return subprocess.CompletedProcess(
                    args=[exercise], returncode=process.returncode, stdout=stdout, stderr=stderr
                )
            except subprocess.TimeoutExpired:
                process.kill()
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
            self.exercises[self.current_exercise.name]["output"] = self.format_exercise_output(result.stdout) if result.returncode == 0 else ""
            self.exercises[self.current_exercise.name]["error"] = self.format_exercise_output(result.stderr) if result.returncode != 0 else None

            if prev_status != "DONE" and new_status == "DONE":
                self.completed_count += 1
            elif prev_status == "DONE" and new_status != "DONE":
                self.completed_count -= 1

            if self.completed_count == len(self.exercises) and not self.completed_flag:
                self.finish()
                self.completed_flag = True

    def format_exercise_output(self,output):
        safe_output = output.replace("[", "\\[") 
        return safe_output

    def get_next_pending_exercise(self):
        """Finds the next exercise that is still PENDING."""
        for ex_data in self.exercises.values():
            if ex_data["status"] == "PENDING":
                return ex_data["path"]
        return None

    def next_exercise(self):
        """Advances to the next exercise in the list and restarts the watcher."""
        exercises = list(self.exercises.values())
        current_index = next((i for i, ex in enumerate(exercises) if ex["path"] == self.current_exercise), None)

        if current_index is not None and current_index + 1 < len(exercises):
            new_exercise = exercises[current_index + 1]["path"]
            self.current_exercise = new_exercise
            self.show_hint = False

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
                prev_status = self.exercises[self.current_exercise.name]["status"]
                self.update_exercise_output()

                if prev_status == "DONE":
                    self.completed_flag = False
                    self.completed_count -= 1
            else:
                print(f"No backup found for {self.current_exercise}.")
        else:
            print("No current exercise to reset.")

    def check_all_exercises(self, progress_callback=None):
        """Updates all exercises without changing the currently selected exercise."""
        current_exercise_path = self.current_exercise

        total_exercises = len(self.exercises)
        completed_checks = 0

        for ex_name, ex_data in self.exercises.items():
            if progress_callback:
                progress_callback(ex_name, completed_checks, total_exercises)

            result = self.run_exercise(ex_data["path"])
            prev_status = ex_data["status"]
            new_status = "DONE" if result.returncode == 0 else "PENDING"

            ex_data["status"] = new_status
            ex_data["output"] = self.format_exercise_output(result.stdout) if result.returncode == 0 else ""
            ex_data["error"] = self.format_exercise_output(result.stderr) if result.returncode != 0 else None

            if prev_status != "DONE" and new_status == "DONE":
                self.completed_count += 1
            elif prev_status == "DONE" and new_status != "DONE":
                self.completed_count -= 1

            completed_checks += 1

        if progress_callback:
            progress_callback(None, total_exercises, total_exercises)

        self.current_exercise = current_exercise_path



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

    def finish(self):
        print(f"{FINISHED}")