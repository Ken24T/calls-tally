import sys
import os
import shutil
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow

def ensure_external_data():
    # Determine the folder where the executable resides.
    exe_dir = os.path.dirname(os.path.abspath(sys.executable)) if getattr(sys, '_MEIPASS', False) else os.path.abspath(".")
    data_folder = os.path.join(exe_dir, "data")
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    # For each JSON file we want to allow editing, copy from the bundled resource if not present.
    bundled_data_folder = os.path.join(getattr(sys, '_MEIPASS', os.path.abspath(".")), "data")
    for filename in ["email_settings.json", "default_emails.json"]:
        dest_file = os.path.join(data_folder, filename)
        if not os.path.exists(dest_file):
            bundled_file = os.path.join(bundled_data_folder, filename)
            if os.path.exists(bundled_file):
                shutil.copy(bundled_file, dest_file)
    return data_folder

def main():
    # Create application directories if they don't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Ensure external (writable) JSON files exist.
    ensure_external_data()
    
    app = QApplication(sys.argv)
    
    # Load stylesheet from a location relative to the executable.
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    qss_file = os.path.join(base_path, "styles.qss")
    if os.path.exists(qss_file):
        with open(qss_file, 'r') as f:
            app.setStyleSheet(f.read())
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
