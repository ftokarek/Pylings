from os import path
from sys import stdout
from time import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
class Watcher:
    """Watches exercise files for modifications and triggers UI updates."""

    def __init__(self, exercise_manager, ui_manager):
        """Initializes the Watcher with exercise and UI managers."""
        self.exercise_manager = exercise_manager
        self.ui_manager = ui_manager
        self.observer = None

    def start(self, exercise_path=None):
        """Starts the file watcher for a specific exercise."""
        self.observer = Observer()
        handler = self.ChangeHandler(self.exercise_manager, self.ui_manager)
        path_to_watch = exercise_path or self.exercise_manager.current_exercise.parent
        self.observer.schedule(handler, str(path_to_watch), recursive=False)
        self.observer.start()

    def stop(self):
        """Stops the file watcher observer."""
        if self.observer:
            self.observer.stop()
            self.observer.join()

    def restart(self, new_exercise_path):
        """Restarts the watcher for a new exercise."""
        self.stop()
        self.start(new_exercise_path)

    class ChangeHandler(FileSystemEventHandler):
        """Handles file modification events."""

        def __init__(self, exercise_manager, ui_manager):
            """Initializes the change handler with the exercise manager and UI manager."""
            self.exercise_manager = exercise_manager
            self.ui_manager = ui_manager
            self.last_modified_time = 0

        def on_modified(self, event):
            """Triggered when an exercise file is modified."""
            current_time = time()
            exercise_path = path.abspath(str(self.exercise_manager.current_exercise))
            event_path = path.abspath(event.src_path)

            if event_path == exercise_path and (current_time - self.last_modified_time) > 0.5:
                self.last_modified_time = current_time
                stdout.flush()
                self.exercise_manager.update_exercise_output()

                if self.ui_manager:
                    self.ui_manager.call_from_thread(self.ui_manager.update_exercise_content)  # Ensures the latest output is displayed
