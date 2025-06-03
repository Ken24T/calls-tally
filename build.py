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

    python_major = sys.version_info.major
    python_minor = sys.version_info.minor
    python_dll_name = f"python{python_major}{python_minor}.dll"  # e.g., python312.dll
    # Use sys.base_prefix to get the root of the Python installation
    # This is more reliable for finding core DLLs, especially with venvs or store Python
    python_dir = sys.base_prefix 
    python_dll_path = os.path.join(python_dir, python_dll_name)

    # If the DLL is in a 'DLLs' subdirectory of sys.base_prefix, adjust path:
    if not os.path.exists(python_dll_path) and os.path.exists(os.path.join(python_dir, "DLLs", python_dll_name)):
        python_dll_path = os.path.join(python_dir, "DLLs", python_dll_name)


    # Run PyInstaller using the current interpreter.
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--name", "CallsTally",
        "--add-data", r"styles.qss;.",     # Include stylesheet in the root
        "--add-data", r"data\*.json;data",
    ]

    if os.path.exists(python_dll_path):
        # Use ';' as the separator for source and destination on Windows for --add-binary
        cmd.extend(["--add-binary", f"{python_dll_path};."])
        print(f"Attempting to add binary: {python_dll_path}")
    else:
        print(f"Warning: Python DLL {python_dll_path} not found. Skipping --add-binary for it.")
        print(f"Please ensure that {python_dll_name} is in the directory {python_dir} or that your Python installation is correct.")

    cmd.append("app.py")

    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("Build failed.")
    else:
        print("Build succeeded. The executable is in the dist folder.")

if __name__ == "__main__":
    main()
