import subprocess
import shutil
import os
import glob
import sys  # using the current interpreter

def check_git_clean():
    """Check if the git working directory is clean."""
    try:
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if result.returncode != 0:
            print("Warning: Could not check git status. Proceeding anyway.")
            return True
        if result.stdout.strip():
            print("Error: Your git working directory is not clean. Commit or stash your changes before building.")
            return False
        return True
    except Exception as e:
        print(f"Warning: Could not check git status: {e}. Proceeding anyway.")
        return True

def clean_previous_builds():
    # Remove build and dist directories and any spec files if they exist.
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    for spec in glob.glob("*.spec"):
        os.remove(spec)

def main():
    if not check_git_clean():
        sys.exit(1)
    clean_previous_builds()

    # Run PyInstaller using the current interpreter.
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--name", "call-tracker",
        "--add-data", r"styles.qss;.",     # Include stylesheet in the root
        "--add-data", r"data\*.json;data",
    ]

    cmd.append("app.py")

    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("Build failed.")
    else:
        print("Build succeeded. The executable is in the dist folder.")

if __name__ == "__main__":
    main()
