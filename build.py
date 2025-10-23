import subprocess
import shutil
import os
import glob
import sys

def check_git_clean():
    """Check if the git working directory is clean."""
    try:
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if result.returncode != 0:
            print("Warning: Could not check git status. Proceeding anyway.")
            return True
        if result.stdout.strip():
            print("Warning: Your git working directory has uncommitted changes.")
            response = input("Continue anyway? (y/n): ")
            return response.lower() == 'y'
        return True
    except Exception as e:
        print(f"Warning: Could not check git status: {e}. Proceeding anyway.")
        return True

def clean_previous_builds():
    """Remove previous build artifacts."""
    print("Cleaning previous builds...")
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"  Removed {folder}/")
    for spec in glob.glob("*.spec"):
        os.remove(spec)
        print(f"  Removed {spec}")

def create_data_folder_template():
    """Create an empty data folder structure in the dist folder."""
    print("\nCreating data folder template...")
    dist_data = os.path.join("dist", "touch-point-tracker", "data")
    os.makedirs(dist_data, exist_ok=True)
    
    # Create empty .gitkeep to ensure folder exists
    with open(os.path.join(dist_data, ".gitkeep"), "w") as f:
        f.write("# This folder will contain user data files\n")
    print(f"  Created {dist_data}/ (empty)")

def main():
    print("=" * 60)
    print("Touch-Point Tracker - Build Script")
    print("=" * 60)
    
    if not check_git_clean():
        print("\nBuild cancelled.")
        sys.exit(1)
    
    clean_previous_builds()

    print("\nRunning PyInstaller...")
    # Run PyInstaller using the current interpreter for one-folder build
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onedir",                        # One-folder build
        "--noconsole",                     # No console window (GUI app)
        "--name", "touch-point-tracker",
        "--add-data", r"styles.qss;.",     # Include stylesheet in the root
        "--icon=NONE",                     # No icon (can add later if needed)
    ]

    cmd.append("app.py")

    result = subprocess.run(cmd)
    
    if result.returncode != 0:
        print("\n" + "=" * 60)
        print("❌ Build FAILED")
        print("=" * 60)
        sys.exit(1)
    
    # Create data folder structure
    create_data_folder_template()
    
    print("\n" + "=" * 60)
    print("✅ Build SUCCEEDED")
    print("=" * 60)
    print(f"\nExecutable location: dist/touch-point-tracker/touch-point-tracker.exe")
    print(f"Distribution folder: dist/touch-point-tracker/")
    print("\nNext steps:")
    print("  1. Test the executable by running it from dist/touch-point-tracker/")
    print("  2. The 'data' folder will be created automatically on first run")
    print("  3. Zip the entire 'dist/touch-point-tracker' folder for deployment")
    print("=" * 60)

if __name__ == "__main__":
    main()
