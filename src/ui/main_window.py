from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QComboBox, QDateEdit, QTextEdit, QPushButton, QMessageBox, QFormLayout, QSpinBox, QGroupBox, 
    QInputDialog, QSizePolicy, QApplication, QSpacerItem)
from PyQt6.QtGui import QAction, QTextCharFormat, QFont  # added QTextCharFormat, QFont
from PyQt6.QtCore import QDate
from src.ui.report_dialog import ReportDialog
from src.data.data_manager import DataManager
from src.settings.settings_manager import SettingsManager
from src.ui.settings_dialog import SettingsDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Autosave on every change; no dirty flag needed.
        
        # Initialize settings manager
        self.settings_manager = SettingsManager()
        
        # Initialize data manager
        self.data_manager = DataManager('data/tally_data.json')
        
        # Set up the main window
        self.setWindowTitle("Calls Tally App")
        self.setFixedSize(210, 740)  # Fixed window size to prevent resizing across monitors
        
        # Apply window position if remember setting is enabled
        self.apply_window_position()
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.central_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)
        
        # Create menus
        self.create_menus()
        
        # Create the form
        self.create_form()
        
        # Add save button at the bottom
        # self.save_button = QPushButton("Save")
        # self.save_button.clicked.connect(self.save_data)
        # self.save_button.setObjectName("primary-button")
        # self.save_button.setEnabled(False)  # Initially disabled
        # self.main_layout.addWidget(self.save_button)

        # Add done button below save button
        self.done_button = QPushButton("Done")
        self.done_button.clicked.connect(self.handle_done)
        self.done_button.setObjectName("primary-button")
        self.main_layout.addWidget(self.done_button)

        # Track unsaved changes
        self.dirty = False
        
        # Update user dropdown and clear current selection
        self.update_user_dropdown()

        self.user_combo.currentIndexChanged.connect(self.load_user_entry)
        self.user_combo.currentIndexChanged.connect(self.update_save_button_state)  # Enable/disable Save
        self.date_edit.dateChanged.connect(self.load_user_entry)
    
    def create_menus(self):
        # Create menu bar
        menu_bar = self.menuBar()
        # Users menu
        users_menu = menu_bar.addMenu("Users")
        add_user_action = QAction("Add User", self)
        add_user_action.triggered.connect(self.add_user)
        users_menu.addAction(add_user_action)
        
        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings_dialog)
        edit_menu.addAction(settings_action)
        
        # Reports menu
        reports_menu = menu_bar.addMenu("Reports")
        self.generate_report_action = QAction("Generate Report", self)
        self.generate_report_action.triggered.connect(self.show_report_dialog)
        reports_menu.addAction(self.generate_report_action)
        self.generate_report_action.setEnabled(False)

    def show_settings_dialog(self):
        settings_dialog = SettingsDialog(self.settings_manager, self)
        settings_dialog.exec()

    def create_form(self):
        # User selection
        user_layout = QHBoxLayout()
        self.main_layout.addLayout(user_layout)
        
        user_label = QLabel("Caller:")
        user_label.setObjectName("required-field")
        user_layout.addWidget(user_label)
        
        self.user_combo = QComboBox()
        # Make user_combo expand horizontally but leave room for the add button
        self.user_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        user_layout.addWidget(self.user_combo)
        
        # Add '+' button to the right of the user_combo
        # self.add_user_button = QPushButton("+")
        # self.add_user_button.setFixedWidth(40)
        # self.add_user_button.setToolTip("Add new user")
        # self.add_user_button.clicked.connect(self.add_user)
        # user_layout.addWidget(self.add_user_button)
        
        # Date selection
        date_layout = QHBoxLayout()
        self.main_layout.addLayout(date_layout)
        
        date_label = QLabel("Date:")
        date_label.setObjectName("required-field")
        date_layout.addWidget(date_label)
        
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        # Allow date_edit to resize horizontally
        self.date_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        date_layout.addWidget(self.date_edit)
        # Store the currently loaded date as ISO string.
        self.current_date_str = self.date_edit.date().toString("yyyy-MM-dd")
        
        # Counters group
        counters_group = QGroupBox("Call Tallies")
        counters_group.setMinimumHeight(440)  # Adjusted to fit all controls at standard dimensions
        counters_group.setMaximumHeight(440)  # Prevent growing beyond intended size
        counters_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        counters_layout = QFormLayout(counters_group)
        counters_layout.setSpacing(10)
        # Allow fields in the form to expand horizontally
        counters_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        
        # Create counters with a helper function
        self.counters = {}
        counter_names = [
            "Calls", "Conns", "Email", "SMS", "F6 Sent", 
            "F6 Rec'd", "Leads", "Appts", "CMA", 
            "Apprs", "Tasks"
        ]
        
        for name in counter_names:
            field_name = name.lower().replace(" ", "_")
            counter_layout = QHBoxLayout()
            spin_box = QSpinBox()
            spin_box.setMinimum(0)
            spin_box.setMaximum(999)
            spin_box.setMinimumHeight(31)  # Increased minimum height for better visibility
            spin_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)  # Prevent shrinking below minimum height
            spin_box.setFixedWidth(70)  # <-- Manually set the width in pixels (adjust as needed)
            # Connect mark_dirty before autosave
            spin_box.valueChanged.connect(self.mark_dirty)
            spin_box.valueChanged.connect(lambda val, key=field_name: self.autosave())
            counter_layout.addWidget(spin_box)
            counters_layout.addRow(name, counter_layout)
            self.counters[field_name] = spin_box
        
        self.main_layout.addWidget(counters_group)
        # Remove the addStretch() call from here if it exists.
        # For example, if there was a line like self.main_layout.addStretch() here, it should be removed.

        # Modify existing spacer to be expanding, or ensure it is if previously changed.
        # The key change is QSizePolicy.Policy.Expanding for the vertical policy.
        self.main_layout.addSpacerItem(QSpacerItem(0, 32, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Comments field
        comments_label = QLabel("Comments:")
        comments_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        # self.main_layout.addWidget(comments_label) # Commented out to hide the label
        self.comments_edit = QTextEdit()
        self.comments_edit.setFixedHeight(60)
        self.comments_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        # Connect mark_dirty before autosave
        self.comments_edit.textChanged.connect(self.mark_dirty)
        self.comments_edit.textChanged.connect(self.autosave)
        self.main_layout.addWidget(self.comments_edit)

        # Ensure no other addStretch() is at the very end of this method if it interferes.
        # If an addStretch() was at the end of create_form() to push buttons down,
        # it might need to be re-evaluated or removed if the expanding spacer handles all slack.
        # Given the buttons are added after create_form in __init__, this might not be an issue here.
    
    def update_user_dropdown(self):
        # Get users and update combo box
        self.user_combo.blockSignals(True)
        current_selection_text = self.user_combo.currentText() # Store current selection text
        self.user_combo.clear()
        users = self.data_manager.get_users()
        
        user_was_selected_programmatically = False

        if users:
            self.user_combo.addItems(users)
            if len(users) == 1:
                self.user_combo.setCurrentIndex(0)  # Select the single user
                user_was_selected_programmatically = True
            elif current_selection_text and current_selection_text in users:
                self.user_combo.setCurrentText(current_selection_text) # Restore previous selection
                # If a user was re-selected, their data should ideally be loaded or re-loaded.
                # However, load_user_entry is already connected to currentIndexChanged.
                # For initial startup, the explicit call is key.
                # For subsequent calls (e.g. after adding a user), if the selection changes, the signal will handle it.
                # If selection doesn't change but list does, an explicit load might be desired if context changes.
                # For now, focus on initial load for single user.
                if self.user_combo.currentIndex() >= 0: # Check if a user is actually selected
                    user_was_selected_programmatically = True

            else:
                self.user_combo.setCurrentIndex(-1)  # No selection
        else:
            self.user_combo.setCurrentIndex(-1)
        
        self.user_combo.blockSignals(False)
        
        # If a user was set (either the single one or a restored one)
        # and this is likely the initial setup (or a scenario where an explicit load is beneficial),
        # call load_user_entry.
        # The currentIndexChanged signal might not fire if setCurrentIndex is called while signals are blocked,
        # or if the index doesn't actually change from its previous state before clear().
        if user_was_selected_programmatically and self.user_combo.currentIndex() >= 0:
            # Check if this is the first time update_user_dropdown is called (during __init__)
            # A more robust way might be to pass a flag or check a state if this method is called multiple times
            # For now, assume if a user is selected programmatically here, we should load their data.
            self.load_user_entry()

        self.update_save_button_state()
    
    def update_save_button_state(self):
        # Enable Save only if a valid user is selected (index >= 0 and text not empty)
        idx = self.user_combo.currentIndex()
        txt = self.user_combo.currentText()
        enabled = idx >= 0 and bool(txt.strip())
        # self.save_button.setEnabled(enabled) # Also comment out references to save_button
        if hasattr(self, 'generate_report_action'):
            self.generate_report_action.setEnabled(enabled)

    def add_user(self):
        name, ok = QInputDialog.getText(self, "Add User", "Enter user's first name:")
        if ok and name:
            # Check if user already exists (case-insensitive)
            existing_users = [u.lower() for u in self.data_manager.get_users()]
            if name.lower() in existing_users:
                QMessageBox.warning(self, "User Exists", f"The user '{name}' already exists.")
                return
            # Add user to data manager
            self.data_manager.add_user(name)
            self.update_user_dropdown()
            self.update_calendar_styles()
    
    def save_data(self, date_str_override=None):
        # Validate form
        if self.user_combo.currentText() == "":
            QMessageBox.warning(self, "Error", "Please select a caller")
            return
        if date_str_override is not None:
            date_str = date_str_override
        else:
            date_str = self.date_edit.date().toString("yyyy-MM-dd")
        counter_data = {}
        for field_name, spin_box in self.counters.items():
            counter_data[field_name] = spin_box.value()
        entry_data = {
            "user": self.user_combo.currentText(),
            "date": date_str,
            "comments": self.comments_edit.toPlainText(),
            **counter_data
        }
        self.data_manager.save_entry(entry_data)
        # Any "Data saved successfully" dialog that might have been here is removed.
        # Removed QApplication.beep() to eliminate sound
        self.dirty = False
    
    def load_user_entry(self):
        """Load existing call statistics for the selected user and date into the UI."""
        self.current_date_str = self.date_edit.date().toString("yyyy-MM-dd")
        user = self.user_combo.currentText()
        if not user:
            return
        date_str = self.date_edit.date().toString("yyyy-MM-dd")
        entry = self.data_manager.get_entry_for_user_and_date(user, date_str)
        
        # Block signals so programmatic updates don’t trigger autosave.
        self.comments_edit.blockSignals(True)
        for spin_box in self.counters.values():
            spin_box.blockSignals(True)
        
        if entry:
            for key, spin_box in self.counters.items():
                spin_box.setValue(entry.get(key, 0))
            self.comments_edit.setText(entry.get("comments", ""))
        else:
            for spin_box in self.counters.values():
                spin_box.setValue(0)
            self.comments_edit.clear()
        
        for spin_box in self.counters.values():
            spin_box.blockSignals(False)
        self.comments_edit.blockSignals(False)
        
        self.update_calendar_styles()
        self.dirty = False
    
    def show_report_dialog(self):
        user = self.user_combo.currentText()
        report_dialog = ReportDialog(self.data_manager)
        if user:
            report_dialog.setWindowTitle(f"Report for {user}")
        report_dialog.exec()
    
    def update_calendar_styles(self):
        """Update the date picker's calendar to bold dates with call stats for the selected user."""
        calendar = self.date_edit.calendarWidget()
        if not calendar:
            return
        
        # Clear formatting for the current year's dates.
        fmt_default = QTextCharFormat()
        current_year = QDate.currentDate().year()
        dt = QDate(current_year, 1, 1)
        end_date = QDate(current_year, 12, 31)
        while dt <= end_date:
            calendar.setDateTextFormat(dt, fmt_default)
            dt = dt.addDays(1)
        
        selected_user = self.user_combo.currentText()
        if not selected_user:
            return
        
        # Retrieve the base font from the calendar widget.
        default_font = calendar.font()
        boldFont = QFont(default_font)
        boldFont.setBold(True)
        boldFormat = QTextCharFormat()
        boldFormat.setFont(boldFont)
        
        # Bold the dates for which the selected user has stats.
        data = self.data_manager._load_data()  # Using internal load.
        for entry in data.get("entries", []):
            if entry.get("user") == selected_user:
                date_val = entry.get("date")
                if not isinstance(date_val, str):
                    continue  # Skip if date is not a string.
                qdate = QDate.fromString(date_val, "yyyy-MM-dd")
                if qdate.isValid():
                    calendar.setDateTextFormat(qdate, boldFormat)
    
    def closeEvent(self, a0):
        self.save_window_position()
        a0.accept()

    def autosave(self):
        self.save_data()
        self.dirty = False

    def mark_dirty(self):
        self.dirty = True
        self.update_save_button_state()

    def handle_done(self):
        if self.dirty:
            reply = QMessageBox.question(
                self, 
                "Unsaved Changes", 
                "You have unsaved changes. Are you sure you want to exit?", 
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        self.save_window_position()
        QApplication.quit()

    def apply_window_position(self):
        if self.settings_manager.get('remember_window_position', False):
            position = self.settings_manager.get('window_position', {'x': 100, 'y': 100, 'screen_name': ''})
            if position:
                # Try to find the screen by name first
                screen_name = position.get('screen_name', '')
                target_screen = None
                
                if screen_name:
                    from PyQt6.QtGui import QGuiApplication
                    for screen in QGuiApplication.screens():
                        if screen.name() == screen_name:
                            target_screen = screen
                            break
                
                # If screen found, move to that screen, otherwise use current screen
                x = position.get('x', 100)
                y = position.get('y', 100)
                
                # Ensure position is within screen bounds
                if target_screen:
                    geometry = target_screen.availableGeometry()
                    x = max(geometry.x(), min(x, geometry.x() + geometry.width() - self.width()))
                    y = max(geometry.y(), min(y, geometry.y() + geometry.height() - self.height()))
                
                self.move(x, y)

    def save_window_position(self):
        if self.settings_manager.get('remember_window_position', False):
            from PyQt6.QtGui import QGuiApplication
            pos = self.pos()
            
            # Find which screen the window is currently on
            current_screen = QGuiApplication.screenAt(pos)
            screen_name = current_screen.name() if current_screen else ''
            
            position_data = {
                'x': pos.x(),
                'y': pos.y(),
                'screen_name': screen_name
            }
            self.settings_manager.set('window_position', position_data)