from pylings.config import ConfigManager
from pylings.constants import (
     BACKUP_DIR,BASE_DIR,DEBUG_PATH, EXERCISES_DIR,
     FINISHED, SOLUTIONS_DIR
)
from pathlib import Path
from shutil import copy, copy2
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import pylings
import logging
logging.basicConfig(filename=DEBUG_PATH, level=logging.DEBUG, format="%(asctime)s - %(message)s")

class ExerciseManager:
    """Manages exercises, including initialization, progression, resets, and output retrieval."""

    def __init__(self):
        """Initializes the ExerciseManager and precomputes exercise states."""
        
        self.exercises = {}
        self.current_exercise = None
        self.current_exercise_state = ""
        self.arg_exercise = None
        self.completed_count = 0
        self.completed_flag = False
        self.config_manager = ConfigManager()
        self.watcher = None  
        self.show_hint = False  
        logging.debug(f"ExerciseManager.init.self: {self.__dict__}")
        self.initialize_exercises()
        self.config_manager.check_first_time()


    def initialize_exercises(self):        
        """Runs all exercises at launch and stores their state in the correct order."""
        exercises = sorted(EXERCISES_DIR.rglob("*.py"))
        
        results = []
        
        with ThreadPoolExecutor() as executor:
            future_to_index = {
                executor.submit(self.run_exercise, ex): i for i, ex in enumerate(exercises)
            }
            
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    result = future.result()
                    results.append((index, result))
                except Exception as e:
                    print(f"Error processing exercise: {e}")

        results.sort(key=lambda x: x[0])
        self.exercises = {}

        for i, (_, result) in enumerate(results):
            status = "DONE" if result.returncode == 0 else "PENDING"
            self.exercises[exercises[i].name] = {
                "path": exercises[i],
                "status": status,
                "output": self.format_exercise_output(result.stdout) if result.returncode == 0 else "",
                "error": self.format_exercise_output(result.stderr) if result.returncode != 0 else None,
                "hint": self.config_manager.get_hint(exercises[i])
            }
            if status == "DONE":
                self.completed_count += 1

        self.current_exercise = EXERCISES_DIR / self.config_manager.get_lasttime_exercise()
        self.current_exercise_state = self.exercises[self.current_exercise.name]["status"]

    def run_exercise(self, exercise):
        """Runs an exercise file and captures its output and errors with a timeout."""
        logging.debug(f"ExerciseManager.run_exercise.exercise: {exercise}")
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
            
        if self.arg_exercise is not None:
            logging.debug(f"ExerciseManager.update_exercise_output.self.arg_exercise: {self.arg_exercise}")   
            self.current_exercise = self.arg_exercise
            logging.debug(f"ExerciseManager.update_exercise_output.self.current_exercise: {self.current_exercise}")
            self.arg_exercise = None

        if self.current_exercise:
            logging.debug(f"ExerciseManager.update_exercise_output.self.current_exercise: {self.current_exercise}")
            result = self.run_exercise(self.current_exercise)
            prev_status = self.exercises[self.current_exercise.name]["status"]
            new_status = "DONE" if result.returncode == 0 else "PENDING"

            self.exercises[self.current_exercise.name]["status"] = "DONE" if result.returncode == 0 else "PENDING"
            self.exercises[self.current_exercise.name]["output"] = self.format_exercise_output(result.stdout) if result.returncode == 0 else ""
            self.exercises[self.current_exercise.name]["error"] = self.format_exercise_output(result.stderr) if result.returncode != 0 else None
            self.current_exercise_state = self.exercises[self.current_exercise.name]["status"]
            
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

    def next_exercise(self):
        """Advances to the next exercise in the list and restarts the watcher."""
        exercises = list(self.exercises.values())
        current_index = next((i for i, ex in enumerate(exercises) if ex["path"] == self.current_exercise), None)

        if current_index is not None and current_index + 1 < len(exercises):
            new_exercise = exercises[current_index + 1]["path"]
            self.current_exercise = new_exercise
            self.show_hint = False
            logging.debug(f"ExerciseManager.next_exercise.self.current_exercise: {self.current_exercise}")

            self.update_exercise_output()
            self.current_exercise_state = self.exercises[self.current_exercise.name]["status"]
            self.config_manager.set_lasttime_exercise(self.current_exercise)
            if self.watcher:
                self.watcher.restart(str(self.current_exercise))
        else:
            print("All exercises completed!")

    def reset_exercise(self):
        """Resets the current exercise to its backup version and updates progress."""
        if self.current_exercise:
            logging.debug(f"ExerciseManager.reset_exercise.self.current_exercise: {self.current_exercise}")

            backup_path = self.current_exercise.relative_to(EXERCISES_DIR)
            package_root = Path(pylings.__file__).parent
            root_backup = BACKUP_DIR / backup_path

            if root_backup.exists():
                root_backup.parent.mkdir(parents=True, exist_ok=True)
                copy(root_backup, self.current_exercise)
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
        """Runs all exercises in parallel while maintaining the original order."""
        current_exercise_path = self.current_exercise
        logging.debug(f"ExerciseManager.check_all_exercises.current_exercise_path : {current_exercise_path }")
        exercises = list(self.exercises.values())
        results = []

        with ThreadPoolExecutor() as executor:
            future_to_index = {
                executor.submit(self.run_exercise, ex["path"]): i for i, ex in enumerate(exercises)
            }

            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    result = future.result()
                    results.append((index, result))
                    logging.debug(f"ExerciseManager.check_all_exercises.result : {result.args[0]} -> {result.returncode}")
                except Exception as e:
                    print(f"Error processing exercise: {e}")

        results.sort(key=lambda x: x[0])

        for i, (_, result) in enumerate(results):
            exercise_name = exercises[i]["path"].name 
            prev_status = self.exercises[exercise_name]["status"]

            new_status = "DONE" if result.returncode == 0 else "PENDING"
            if new_status != prev_status:
                self.exercises[exercise_name] = {
                    "path": exercises[i]["path"],
                    "status": new_status,
                    "output": self.format_exercise_output(result.stdout) if result.returncode == 0 else "",
                    "error": self.format_exercise_output(result.stderr) if result.returncode != 0 else None,
                }

            if prev_status != "DONE" and new_status == "DONE":
                self.completed_count += 1
            elif prev_status == "DONE" and new_status != "DONE":
                self.completed_count -= 1

        self.current_exercise = current_exercise_path


    def get_solution(self):
        """Return the solution file path for the given current exercise."""
        if not self.current_exercise:
            return None

        try:
            SOLUTIONS_DIR.mkdir(parents=True, exist_ok=True)

            relative_path = self.current_exercise.relative_to(EXERCISES_DIR)

            solution_path = SOLUTIONS_DIR / relative_path
            if solution_path.exists():
                return solution_path

            package_root = Path(pylings.__file__).parent
            root_solution = package_root / "solutions" / relative_path

            if root_solution.exists():
                solution_path.parent.mkdir(parents=True, exist_ok=True)
                copy2(root_solution, solution_path)
                return get_local_solution_path(solution_path)

            return None

        except Exception as e:
            print(f"Error resolving solution path: {e}")
            return None


    def toggle_hint(self):
        """Toggles the hint display flag."""
        
        self.show_hint = not self.show_hint

    def finish(self):
        
        print(f"{FINISHED}")