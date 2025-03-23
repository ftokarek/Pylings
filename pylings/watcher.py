import os
import hashlib
from threading import Timer
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pylings.constants import DEBUG_PATH
import logging
logging.basicConfig(filename=DEBUG_PATH, level=logging.DEBUG, format="%(asctime)s - %(message)s")

class Watcher:
    """Watches exercise files for modifications and triggers UI updates."""

    def __init__(self, exercise_manager, ui_manager):
        """Initializes the Watcher with exercise and UI managers."""
        logging.debug(f"Watcher.init: Entered")
        self.exercise_manager = exercise_manager
        self.ui_manager = ui_manager
        self.observer = None

    def start(self, exercise_path=None):
        """Starts the file watcher for a specific exercise."""
        logging.debug(f"Watcher.start: Entered")
        self.observer = Observer()
        handler = self.ChangeHandler(self.exercise_manager, self.ui_manager)
        path_to_watch = exercise_path or self.exercise_manager.current_exercise
        self.observer.schedule(handler, str(path_to_watch), recursive=False)
        logging.debug(f"Watcher.start.path_to_watch: {path_to_watch}")
        self.observer.start()

    def stop(self):
        """Stops the file watcher observer."""
        logging.debug(f"Watcher.stop: Entered")
        if self.observer:
            self.observer.stop()
            self.observer.join()

    def restart(self, new_exercise_path):
        """Restarts the watcher for a new exercise."""
        logging.debug(f"Watcher.restart: Entered")
        self.stop()
        logging.debug(f"Watcher.restart.new_exercise_path: {new_exercise_path}")
        self.start(new_exercise_path)

    class ChangeHandler(FileSystemEventHandler):
        def __init__(self, exercise_manager, ui_manager):
            logging.debug("ChangeHandler.__init__: Entered")
            self.exercise_manager = exercise_manager
            self.ui_manager = ui_manager
            self.last_hash = None
            self.debounce_timer = None
            self.debounce_interval = 0.3  # adjust if needed

        def get_file_hash(self, file_path):
            try:
                with open(file_path, "rb") as f:
                    return hashlib.blake2b(f.read(), digest_size=16).hexdigest()
            except Exception as e:
                logging.error(f"ChangeHandler.get_file_hash error: {e}")
                return None

        def trigger_update_if_changed(self, event_path):
            current_exercise_path = os.path.abspath(str(self.exercise_manager.current_exercise))
            event_path = os.path.abspath(event_path)

            if event_path != current_exercise_path:
                return

            current_hash = self.get_file_hash(event_path)
            if not current_hash or current_hash == self.last_hash:
                logging.debug("ChangeHandler: No content change or unreadable file")
                return

            self.last_hash = current_hash

            if self.debounce_timer:
                self.debounce_timer.cancel()

            self.debounce_timer = Timer(self.debounce_interval, self._handle_file_change)
            self.debounce_timer.start()

        def on_modified(self, event):
            logging.debug("ChangeHandler.on_modified: Entered")
            if not event.is_directory:
                self.trigger_update_if_changed(event.src_path)

        def on_created(self, event):
            logging.debug("ChangeHandler.on_created: Entered")
            if not event.is_directory:
                self.trigger_update_if_changed(event.src_path)

        def _handle_file_change(self):
            logging.debug("ChangeHandler._handle_file_change: Updating exercise")
            self.exercise_manager.update_exercise_output()
            if self.ui_manager:
                self.ui_manager.call_from_thread(self.ui_manager.update_exercise_content)
