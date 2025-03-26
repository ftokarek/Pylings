from pathlib import Path
import shutil
import importlib.util
import subprocess
import toml
import filecmp

IGNORED_DIRS = {"__pycache__", ".git"}
IGNORED_FILES = {".DS_Store", "Thumbs.db"}

def init_workspace(path: str = None, force: bool = False):
    cwd = Path.cwd()

    if path:
        target_dir = Path(path).resolve()
    elif force:
        target_dir = cwd
    elif (cwd / ".pylings.toml").exists():
        target_dir = cwd
    else:
        target_dir = cwd / "pylings"

    target_dir.mkdir(parents=True, exist_ok=True)

    exercises_src = Path(__file__).parent / "exercises"
    exercises_dst = target_dir / "exercises"

    if exercises_dst.exists():
        if force:
            shutil.rmtree(exercises_dst)
        else:
            print(f"Found existing exercises at {exercises_dst}, skipping copy. Use --force to overwrite.")
            exercises_dst = None

    if exercises_dst is not None:
        shutil.copytree(exercises_src, exercises_dst)

    version = get_installed_version()
    (target_dir / ".pylings.toml").write_text(
        f'[workspace]\nversion = "{version}"\nfirsttime=true\ncurrent_exercise = "00_intro/intro1.py"'
    )

    initialise_git(target_dir)
    print("🎉 Pylings initialised at:", target_dir)



def get_package_root():
    return Path(importlib.util.find_spec("pylings").origin).parent

def update_workspace(path: str = None):
    cwd = Path.cwd()
    target_dir = Path(path).resolve() if path else cwd
    root_dir = get_package_root()

    print(f"🔍 Updating workspace at: {target_dir}")

    for folder_name in ["exercises", "solutions"]:
        src_dir = root_dir / folder_name
        dst_dir = target_dir / folder_name

        if not src_dir.exists():
            print(f"Source folder {src_dir} does not exist. Skipping.")
            continue

        new_files = []
        removed_files = []
        skipped_files = []

        for dst_file in dst_dir.rglob("*"):
            if dst_file.is_file():
                if any(part in IGNORED_DIRS for part in dst_file.parts):
                    continue
                if dst_file.name in IGNORED_FILES:
                    continue

                rel_path = dst_file.relative_to(dst_dir)
                src_file = src_dir / rel_path
                print(f"dst.is_file(): {dst_file}   //  src_file: {src_file} exists = {src_file.exists()} ")
                if dst_file.is_file() and not src_file.exists():
                    try:
                        dst_file.unlink()
                        removed_files.append(str(rel_path))
                    except Exception as e:
                        print(f"Could not remove {dst_file}: {e}")

        for dirpath in sorted(dst_dir.rglob("*"), reverse=True):
            if dirpath.is_dir() and not any(dirpath.iterdir()):
                try:
                    dirpath.rmdir()
                except Exception:
                    pass

        for src_file in src_dir.rglob("*"):
            if src_file.is_file():
                if any(part in IGNORED_DIRS for part in src_file.parts):
                    continue
                if src_file.name in IGNORED_FILES:
                    continue

                rel_path = src_file.relative_to(src_dir)
                dest_file = dst_dir / rel_path

                if folder_name == "exercises":
                    if not dest_file.exists():
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src_file, dest_file)
                        new_files.append(str(rel_path))

                elif folder_name == "solutions":
                    if dest_file.exists():
                        if not filecmp.cmp(src_file, dest_file, shallow=False):
                            shutil.copy2(src_file, dest_file)
                            new_files.append(str(rel_path))
                        else:
                            skipped_files.append(str(rel_path))

        print(f"\n{folder_name}/")
        if new_files:
            print("Updated or added:")
            for f in new_files:
                print(f"  + {f}")
        if removed_files:
            print("Removed:")
            for f in removed_files:
                print(f"  - {f}")
        if skipped_files:
            print("Unchanged:")
            for f in skipped_files:
                print(f"  ~ {f}")

    src_backups = root_dir / "backups"
    dst_backups = target_dir / "backups"
    if dst_backups.exists() and not src_backups.exists():
        shutil.rmtree(dst_backups)
        print("Removed stale backups/ directory")


def get_installed_version():
    try:
        import pylings
        return pylings.__version__
    except Exception:
        return "0.1.0"

def get_workspace_version():
    pylings_toml = Path(".pylings.toml")
    if not pylings_toml.exists():
        return None

    try:
        data = toml.load(pylings_toml)
        return data.get("workspace", {}).get("version", None)
    except Exception as e:
        print(f"Could not read workspace version: {e}")
        return None

def check_version_mismatch():
    import pylings
    workspace_version = get_workspace_version()
    installed_version = pylings.__version__

    if workspace_version and workspace_version != installed_version:
        print(f"\nYour workspace was created with pylings v{workspace_version}, but v{installed_version} is now installed.")
        print("To update your exercises with new content only, run:")
        print("   pylings update\n")
        print("To upgrade the package itself:")
        print("   pip install --upgrade pylings\n")
        exit(1)

def initialise_git(target_dir):
    git_dir = target_dir / ".git"
    if not git_dir.exists():
        try:
            subprocess.run(["git", "init"], cwd=target_dir, check=True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            (target_dir / ".gitignore").write_text(
                "__pycache__/\n"
                "*.pyc\n"
                ".venv/\n"
                ".pylings_debug.log\n"
            )
        except Exception as e:
            print(f"Failed to initialize git repository: {e}")