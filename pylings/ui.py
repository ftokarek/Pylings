from textual.app import App, ComposeResult
from textual.widgets import  ListView, ListItem, ProgressBar, Static
from textual.containers import Center, Horizontal, Vertical
from textual.reactive import reactive
from textual.events import Key
from pylings.exercises import ExerciseManager
from pylings.constants import DONE,DONE_MESSAGE, GIT_ADD, GIT_COMMIT, GIT_MESSAGE, EXERCISE_DONE, SOLUTION_LINK, PENDING, EXERCISE_OUTPUT, EXERCISE_ERROR, LIST_VIEW, MAIN_VIEW
from rich.text import Text

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
        self.update_progress_bar()

    def refresh_exercise_output(self):
        """Reloads exercise output when file changes."""
        if not self.current_exercise:
            return
        output_widget = self.query_one("#output", Static)
        formatted_output = self.format_output()
        output_widget.update(formatted_output)

    def format_output(self):
        """Formats the exercise output for display in the UI."""
        if not self.current_exercise:
            return "No exercise selected."

        exercise_name = self.current_exercise.name if self.current_exercise.name else None
        if not exercise_name or exercise_name not in self.exercise_manager.exercises:
            return "Invalid exercise."

        ex_data = self.exercise_manager.exercises[exercise_name]

        if ex_data["status"] == "DONE":
            lines = [
                f"\n{EXERCISE_OUTPUT(ex_data['output'])}",
                f"\n\n{EXERCISE_DONE}",
                f"\n{SOLUTION_LINK(self.exercise_manager.get_solution())}",
                f"\n\n{DONE_MESSAGE}",
                f"\n{GIT_MESSAGE}",
                f"\n\n\t{GIT_ADD(self.current_exercise)}",
                f"\n\t{GIT_COMMIT(self.current_exercise)}\n",
            ]
            return ''.join(lines)

        else:
            error_message = f"{EXERCISE_ERROR(ex_data['error'])}"
            if self.exercise_manager.show_hint:
                error_message += f"\n{ex_data.get('hint', '')}\n"

        return error_message

    def update_list_content(self):
        listview_widget = self.query_one("#exercise-list", ListView)
        listview_widget.clear()
        listview_widget.extend(self.get_exercise_list())
    
    def update_progress_bar(self):
        """Generate a Rustlings-style text progress bar inside Static."""
        progress_bar_widget = self.query_one("#progress-bar", Static)
        
        total_exercises = len(self.exercise_manager.exercises)
        completed_exercises = sum(1 for ex in self.exercise_manager.exercises.values() if ex["status"] == "DONE")

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

        #if exercise_name:
        #    check_progress_widget.update(f"Checking exercise: {completed}/{total-1 } {exercise_name}")
        
        self.refresh()

    def focus_list(self, enable):
        """Focus on the ListView for navigation."""
        self.query_one("#exercise-list", ListView).focus()
        self.list_focused = enable

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
            
            self.footer_hints.update(LIST_VIEW)
    
        else:
            sidebar.add_class("hidden")
            main_content.add_class("expanded")
            #self.list_focused = False
            self.footer_hints.update(MAIN_VIEW)

    def on_key(self, event: Key) -> None:
        """Handle keyboard shortcuts for navigation and actions."""
        if event.key == "q":
            self.exit()
        elif event.key == "n":
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
                    self.update_exercise_content()

                    if self.exercise_manager.watcher:        
                        self.exercise_manager.watcher.restart(str(new_exercise.parent))

            elif event.key == "c":
                self.exercise_manager.check_all_exercises(progress_callback=self.update_check_progress)
                self.update_exercise_content()
                self.update_list_content()

if __name__ == "__main__":
    exercise_manager = ExerciseManager()
    app = PylingsUI(exercise_manager)
    app.run()