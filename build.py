import subprocess
import shutil
import os
import glob
import sys  # using the current interpreter

def clean_previous_builds():
    # Remove build and dist directories and any spec files if they exist.
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    for spec in glob.glob("*.spec"):
        os.remove(spec)

def main():
    clean_previous_builds()
    # Run PyInstaller using the current interpreter.
    # Added "--add-data" for styles.qss so that it is included alongside the executable.
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile", "--noconsole",
        "--add-data", r"styles.qss;.",     # Include stylesheet in the root
        "--add-data", r"data\*.json;data",
        "app.py"
    ]
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("Build failed.")
    else:
        print("Build succeeded. The executable is in the dist folder.")

if __name__ == "__main__":
    main()
