from pathlib import Path
import shutil
import subprocess

def init_workspace(path: str = None, force: bool = False):
    cwd = Path.cwd()
    target_dir = Path(path).resolve() if path else (
        cwd if (cwd / ".pylings.toml").exists() and not force else cwd / "pylings"
    )

    print(f"📁 Initializing pylings workspace at: {target_dir}")
    target_dir.mkdir(parents=True, exist_ok=True)

    # Copy exercises
    exercises_src = Path(__file__).parent / "exercises"
    exercises_dst = target_dir / "exercises"
    if force and exercises_dst.exists():
        shutil.rmtree(exercises_dst)
    if not exercises_dst.exists():
        shutil.copytree(exercises_src, exercises_dst)
        print("✅ exercises/ copied.")

    # Create .pylings.toml
    (target_dir / ".pylings.toml").write_text('workspace_version = "0.1.0"\n')

    # Create .firsttime marker
    (target_dir / ".firsttime").write_text("firsttime=true\n")
    initialise_git(target_dir)
    print("🎉 Workspace ready at:", target_dir)


def initialise_git(target_dir):
    git_dir = target_dir / ".git"
    if not git_dir.exists():
        try:
            subprocess.run(["git", "init"], cwd=target_dir, check=True)
            print("✅ Git repository initialized.")

            # Write .gitignore
            gitignore = target_dir / ".gitignore"
            gitignore.write_text(
                "__pycache__/\n"
                "*.pyc\n"
                ".venv/\n"
                "pylings_debug.log\n"
                ".firsttime\n"
            )
            print("✅ .gitignore created.")
        except Exception as e:
            print(f"⚠️ Failed to initialize git repository: {e}")