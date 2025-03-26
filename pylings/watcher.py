"""
Watches for changes in exercise files and triggers updates to the UI or backend state.

Uses watchdog to observe file system events, compute file hashes,
and debounce rapid file changes before invoking refresh callbacks.
"""
import hashlib
import logging
import os
from threading import Timer
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

log = logging.getLogger(__name__)

class Watcher:
    """Manages file watching for Pylings exercises using watchdog.

    Watches the currently selected exercise file and restarts the watcher
    whenever the exercise is changed.
    """

    def __init__(self, exercise_manager, ui_manager):
        """Initializes the Watcher with access to the exercise and UI managers.

        Args:
            exercise_manager: The object managing exercises and state.
            ui_manager: The Textual-based UI controller to refresh content.
        """
        log.debug("Watcher.__init__: Entered")
        self.exercise_manager = exercise_manager
        self.ui_manager = ui_manager
        self.observer = None

    def start(self, exercise_path: str | Path = None):
        """Starts the file system watcher for a specific exercise path.

        Args:
            exercise_path (str | Path, optional): The path to the file to watch.
            If not provided, uses the current exercise path from the manager.
        """
        log.debug("Watcher.start: Entered")
        self.observer = Observer()
        handler = self.ChangeHandler(self.exercise_manager, self.ui_manager)

        path_to_watch = Path(exercise_path) if exercise_path else self.exercise_manager.current_exercise
        log.debug(f"Watcher.start.path_to_watch: {path_to_watch}")
        self.observer.schedule(handler, str(path_to_watch), recursive=False)
        self.observer.start()

    def stop(self):
        """Stops the active file watcher and waits for its thread to finish."""
        log.debug("Watcher.stop: Entered")
        if self.observer:
            self.observer.stop()
            self.observer.join()

    def restart(self, new_exercise_path: str | Path):
        """Restarts the watcher on a new exercise path.

        Stops the current observer (if any) and starts a new one.

        Args:
            new_exercise_path (str | Path): Path to the newly selected exercise file.
        """
        log.debug("Watcher.restart: stopping")
        self.stop()
        log.debug(f"Watcher.restart.new_exercise_path: {new_exercise_path}")
        self.start(new_exercise_path)
        log.debug("Watcher.restart: started")

    class ChangeHandler(FileSystemEventHandler):
        """Handles file system modification events for the watched exercise.

        Uses file hashing and debouncing to prevent redundant updates on every keystroke.
        """

        def __init__(self, exercise_manager, ui_manager):
            """Initializes the file change handler.

            Args:
                exercise_manager: Reference to the exercise state manager.
                ui_manager: Reference to the UI for triggering updates.
            """
            log.debug("ChangeHandler.__init__: Entered")
            self.exercise_manager = exercise_manager
            self.ui_manager = ui_manager
            self.last_hash = None
            self.debounce_timer = None
            self.debounce_interval = 0.3  # seconds

        def get_file_hash(self, file_path: Path) -> str | None:
            """Computes a hash of the given file contents using blake2b.

            Args:
                file_path (Path): Path to the file being monitored.

            Returns:
                str | None: Hash digest or None on error.
            """
            log.debug("ChangeHandler.get_file_hash: Entered")
            try:
                with open(file_path, "rb") as f:
                    return hashlib.blake2b(f.read(), digest_size=16).hexdigest()
            except Exception as e:
                log.error(f"ChangeHandler.get_file_hash error: {e}")
                return None

        def trigger_update_if_changed(self, event_path: str):
            """Triggers a UI and output update if the file has changed.

            Uses file hash comparison to detect actual changes.
            Debounces updates to avoid flooding on save or write events.

            Args:
                event_path (str): Path to the file that changed.
            """
            event_path = os.path.abspath(event_path)
            current_path = os.path.abspath(str(self.exercise_manager.current_exercise))

            if event_path != current_path:
                return

            current_hash = self.get_file_hash(event_path)
            if not current_hash or current_hash == self.last_hash:
                return

            self.last_hash = current_hash
            if self.debounce_timer:
                self.debounce_timer.cancel()

            self.debounce_timer = Timer(self.debounce_interval, self._handle_file_change)
            self.debounce_timer.start()

        def _handle_file_change(self):
            """Performs the actual refresh of exercise output and UI content."""
            log.debug("ChangeHandler._handle_file_change: Triggered")
            self.exercise_manager.update_exercise_output()
            if self.ui_manager:
                self.ui_manager.call_from_thread(self.ui_manager.update_exercise_content)

        def on_modified(self, event):
            """Called by watchdog when a file is modified."""
            if not event.is_directory:
                self.trigger_update_if_changed(event.src_path)

        def on_created(self, event):
            """Called by watchdog when a new file is created."""
            if not event.is_directory:
                self.trigger_update_if_changed(event.src_path)
