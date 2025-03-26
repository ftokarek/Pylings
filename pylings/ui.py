from pylings.utils import PylingsUtils
from pylings.exercises import ExerciseManager
from pylings.constants import (DEBUG_PATH, DONE,DONE_MESSAGE, EXERCISE_DONE, EXERCISE_ERROR, EXERCISE_OUTPUT,
                              GREEN, LIGHT_BLUE, LIST_VIEW, LIST_VIEW_NEXT,
                               MAIN_VIEW, MAIN_VIEW_NEXT, PENDING, RESET_COLOR
)
from rich.text import Text     
from textual.app import App, ComposeResult
from textual.widgets import  ListView, ListItem, Static
from textual.containers import Horizontal, Vertical
from textual.events import Key
from pathlib import Path
import logging
logging.basicConfig(filename=DEBUG_PATH, level=logging.DEBUG, format="%(asctime)s - %(message)s")

class PylingsUI(App):
    """Textual-based UI for Pylings."""

    CSS_PATH = "./styles/ui.tcss"

    def __init__(self, exercise_manager: ExerciseManager):
        super().__init__()
        self.exercise_manager = exercise_manager
        self.current_exercise = self.exercise_manager.current_exercise
        self.list_focused = False
        self.sidebar_visible = False

    def compose(self) -> ComposeResult:
        """Build UI layout."""
        yield Horizontal(
            Vertical(
                Static("", id="output"),
                Static("", id="hint"),
                Static("", id="progress-bar"),
                Static("Current exercise: ", id="exercise-path"),
                Static("", disabled=True, id="checking-all-exercises-status"),
                id="main"
            ),
            Vertical(
                Static("Status  Exercise"),
                ListView(*self.get_exercise_list(), id="exercise-list"),
                id="sidebar"
            ),
        )
        
        self.footer_hints = Static(MAIN_VIEW, id="footer-hints")
        self.footer_hints.visible = True
        yield self.footer_hints
    def on_mount(self):
        """Update UI with initial exercise details."""
        self.update_exercise_content()
        sidebar = self.query_one("#sidebar", Vertical)
        main_content = self.query_one("#main", Vertical)

        sidebar.add_class("hidden")
        main_content.add_class("expanded")

        self.list_focused = False
        self.footer_hints.update(MAIN_VIEW)

    def get_exercise_list(self):
            """Generate exercise list for sidebar with updated status."""
            items = []
            for name, ex in self.exercise_manager.exercises.items():
                status = DONE if ex["status"] == "DONE" else PENDING
                items.append(ListItem(Static(f"{status} {name}")))
            return items

    def update_exercise_content(self):
        """Update displayed exercise details, refresh the list, and update the exercise path."""
        exercise_path_widget = self.query_one("#exercise-path", Static)
        exercise_path = self.current_exercise if self.current_exercise else "No exercise selected"
        exercise_path_widget.update(f"Current exercise: {exercise_path}") 
        self.refresh_exercise_output()
        self.footer_hints.update(self.view_options())
        self.update_progress_bar()

    def refresh_exercise_output(self):
        """Reloads exercise output when file changes."""
        if not self.current_exercise:
            return
        output_widget = self.query_one("#output", Static)
        formatted_output = self.build_output()
        output_widget.update(formatted_output)

    def build_output(self):
        """Builds the exercise output for display in the UI."""
        if not self.current_exercise:
            return "No exercise selected."

        exercise_name = self.current_exercise.name if self.current_exercise.name else None
        if not exercise_name or exercise_name not in self.exercise_manager.exercises:
            return "Invalid exercise."

        ex_data = self.exercise_manager.exercises[exercise_name]

        if ex_data["status"] == "DONE":
            full_solution_path, short_path = self.exercise_manager.get_solution()
            git_status = PylingsUtils.get_git_status()
            lines = [
                f"\n{EXERCISE_OUTPUT(ex_data['output'])}",
                f"\n\n{EXERCISE_DONE}",
                f"\n{self.solution_link(full_solution_path,short_path)}",
                f"\n\n{DONE_MESSAGE}",
                f"\n{self.git_suggestion(git_status)}"
            ]
            return ''.join(lines)

        else:
            error_message = f"{EXERCISE_ERROR(ex_data['error'])}"
            if self.exercise_manager.show_hint:
                error_message += f"\n{ex_data.get('hint', '')}\n"

        return error_message

    def solution_link(self, full_path, short_path):
        uri = Path(full_path).absolute().as_uri()
        display = f"solutions/{short_path.replace("\\", "/")}"
        text = Text("Solution for comparison: ")
        text.append(f"{GREEN}{display}{RESET_COLOR}", style=f" link {uri}")
        return text

    def git_suggestion(self,git_status_lines):
        """
        Accepts parsed output from get_git_status_lines() and returns a Text object
        with `git add` commands and a summarized `git commit -m`.
        """
        text = Text()
        if not git_status_lines:
            return text.append("")

        added = []
        modified = []
        deleted = []
        unknown = []

        for line in git_status_lines:
            status = line[:2].strip()
            path = line[3:].strip()

            if status == "??":
                added.append(path)
            elif status == "M":
                modified.append(path)
            elif status == "D":
                deleted.append(path)
            else:
                unknown.append((status, path))

        all_files = added + modified + deleted + [p for _, p in unknown]

        # --- Git Add Block ---
        text.append("Use ")
        text.append("git", style="underline")
        text.append(" to keep track of your progress:\n\n")

        #text.append("  ")
        text.append(f"\t{LIGHT_BLUE}git add ")
        text.append(f" ".join(all_files))
        text.append(f"{RESET_COLOR}\n")

        # --- Commit Summary ---

        #text.append("  ")
        text.append(f"\t{LIGHT_BLUE}git commit -m \"changes: ")
        text.append(f" ".join(all_files))
        text.append(f'\"{RESET_COLOR}\n')

        return text


    def update_list_content(self):
        listview_widget = self.query_one("#exercise-list", ListView)
        listview_widget.clear()
        listview_widget.extend(self.get_exercise_list())
    
    def update_progress_bar(self):
        """Generate a Rustlings-style text progress bar inside Static.""" 
        progress_bar_widget = self.query_one("#progress-bar", Static)
        
        total_exercises = len(self.exercise_manager.exercises)
        completed_exercises = self.exercise_manager.completed_count

        bar_length = 55
        progress_fraction = completed_exercises / total_exercises if total_exercises > 0 else 0

        filled = int(progress_fraction * bar_length)
        remaining = bar_length - filled - 1 

        progress_bar = Text("Progress: [", style="bold")
        progress_bar.append("#" * filled, style="green")
        progress_bar.append(">", style="green")
        progress_bar.append("-" * remaining, style="red")
        progress_bar.append(f"]   {completed_exercises}/{total_exercises}", style="bold")

        progress_bar_widget.update(progress_bar)

    def update_check_progress(self, exercise_name, completed, total):
        """Update the UI to show checking progress."""
        check_progress_widget = self.query_one("#checking-all-exercises-status", Static)
        
        if exercise_name:
            logging.debug(f"PylingsUI.update_update_progress.exercise_name: {exercise_name} {completed}/{total-1}")
            check_progress_widget.update(f"Checking exercise: {completed}/{total-1 } {exercise_name}")
        self.refresh()


    def finished_check_progress_notice(self, clear=False):
        check_progress_widget = self.query_one("#checking-all-exercises-status", Static)
        
        if clear:
            check_progress_widget.update("")
        else:
            check_progress_widget.update("Finished checking all exercises")

    def toggle_list_view(self):
        """Toggle the visibility of the exercise list view while preserving selection."""
        
        sidebar = self.query_one("#sidebar", Vertical)
        main_content = self.query_one("#main", Vertical)
        list_view = self.query_one("#exercise-list", ListView)

        selected_index = list_view.index if list_view.index is not None else 0
        if "hidden" in sidebar.classes:
            sidebar.remove_class("hidden")
            main_content.remove_class("expanded")

            if 0 <= selected_index < len(list_view.children):
                list_view.index = selected_index
                list_view.scroll_visible(list_view.children[selected_index])
                
            self.list_focused = True
            self.sidebar_visible = True
            
            self.footer_hints.update(self.view_options())
    
        else:
            sidebar.add_class("hidden")
            main_content.add_class("expanded")
            self.list_focused = False
            self.sidebar_visible = False
            self.footer_hints.update(self.view_options())

    def view_options(self):
        if self.sidebar_visible == True:
            if self.exercise_manager.current_exercise_state == "DONE":
                return LIST_VIEW_NEXT
            elif self.exercise_manager.current_exercise_state == "PENDING": 
                return LIST_VIEW
        else:
            if self.exercise_manager.current_exercise_state == "DONE":
                return MAIN_VIEW_NEXT
            elif self.exercise_manager.current_exercise_state == "PENDING":
                return MAIN_VIEW

    def on_key(self, event: Key) -> None:
        """Handle keyboard shortcuts for navigation and actions."""
        if event.key == "q":
            self.exit()
        elif event.key == "n":
            if self.exercise_manager.current_exercise_state == "DONE":
                self.exercise_manager.next_exercise()
                self.current_exercise = self.exercise_manager.current_exercise
                self.update_exercise_content()
                self.update_list_content()
        elif event.key == "r":
            self.exercise_manager.reset_exercise()
            self.update_exercise_content()
            self.update_list_content()
        elif event.key == "h":
            if self.exercise_manager.show_hint == False:
                hint = self.exercise_manager.config_manager.get_hint(self.current_exercise)
                self.exercise_manager.toggle_hint()
                self.query_one("#hint", Static).update(hint)
            elif self.exercise_manager.show_hint == True:
                self.query_one("#hint", Static).update("")
                self.exercise_manager.toggle_hint()
        elif event.key == "l":
            self.toggle_list_view()
            self.finished_check_progress_notice(True)
            event.key = "tab"
        elif self.list_focused and event.key in ("up", "down", "end", "home","c", "s"):
            list_view = self.query_one("#exercise-list", ListView)
            if event.key == "up":
                selected_index = list_view.index
                
            elif event.key == "down":
                selected_index = list_view.index
                
            elif event.key == "end":
                list_view.index = len(list_view.children) - 1
                
            elif event.key == "home":
                list_view.index = 0

            elif event.key == "s":
                selected_index = list_view.index
                if selected_index is not None:
                    exercise_keys = list(self.exercise_manager.exercises.keys())
                    new_exercise_name = exercise_keys[selected_index]
                    new_exercise = self.exercise_manager.exercises[new_exercise_name]["path"]
                    self.exercise_manager.current_exercise = new_exercise
                    self.current_exercise = new_exercise
                    self.exercise_manager.config_manager.set_lasttime_exercise(new_exercise)
                    self.exercise_manager.current_exercise_state = self.exercise_manager.exercises[new_exercise_name]["status"]
                    self.update_exercise_content()

                    if self.exercise_manager.watcher:        
                        self.exercise_manager.watcher.restart(str(new_exercise.parent))

            elif event.key == "c":
                self.exercise_manager.check_all_exercises(progress_callback=self.update_check_progress)
                self.finished_check_progress_notice(False)
                self.update_exercise_content()
                self.update_list_content()

if __name__ == "__main__":
    exercise_manager = ExerciseManager()
    app = PylingsUI(exercise_manager)
    app.run()