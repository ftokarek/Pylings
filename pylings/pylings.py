from sys import exit
import traceback
from pylings.exercises import ExerciseManager
from pylings.utils import PylingsUtils
from pylings.watcher import Watcher
from pylings.ui import PylingsUI
from pylings.init import init_workspace, update_workspace, check_version_mismatch

def main():
    args = PylingsUtils.parse_args()

    if args.command == "init":
        init_workspace(args.path, force=args.force)
        exit(0)

    elif args.command == "update":
        update_workspace(args.path)
        exit(0)

    elif args.version:
        local_version = PylingsUtils.get_local_version()
        pip_version, pip_license, github_url,pip_url = PylingsUtils.get_pip_package_info()

        print("\nLocal Pylings :")
        print(f"\tVersion: {local_version}")

        print("\npip Pylings :")
        print(f"\tVersion: {pip_version}")
        print(f"\tLicense: {pip_license}")
        print(f"\tGitHub:  {github_url}")
        print(f"\tPypi:    {pip_url}")
        exit(0)

    check_version_mismatch()

    if not PylingsUtils.is_pylings_toml():
        exit(1)

    exercise_manager = ExerciseManager()
    watcher = Watcher(exercise_manager, None)
    exercise_manager.watcher = watcher

    if PylingsUtils.handle_args(args, exercise_manager, watcher):
        exercise_manager.update_exercise_output()

    app = PylingsUI(exercise_manager)
    watcher.ui_manager = app

    if exercise_manager.current_exercise:
        watcher.start(str(exercise_manager.current_exercise.parent))

    try:
        app.run()
    except KeyboardInterrupt:
        print("Interrupted by user.")
        exit(0)
    except Exception as e:
        print(f"Error: {e}")
        print.error(f"App crashed with exception:\n" + traceback.format_exc())
        exit(1)

if __name__ == "__main__":
    main()