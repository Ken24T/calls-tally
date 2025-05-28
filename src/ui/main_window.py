from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QComboBox, QDateEdit, QTextEdit, QPushButton, QMessageBox, QDialog, 
    QLineEdit, QListWidget, QListWidgetItem, QFormLayout, QSpinBox, QGroupBox, 
    QToolBar, QMenu, QMenuBar, QTabWidget, QCalendarWidget, QInputDialog, QSizePolicy, QApplication)
from PyQt6.QtGui import QIcon, QAction, QTextCharFormat, QFont, QTextCharFormat, QFont  # added QTextCharFormat, QFont
from PyQt6.QtCore import Qt, QDate
from src.data.data_manager import DataManager
from src.ui.report_dialog import ReportDialog
import datetime

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Autosave on every change; no dirty flag needed.
        
        # Initialize data manager
        self.data_manager = DataManager('data/tally_data.json')
        
        # Set up the main window
        self.setWindowTitle("Calls Tally App")
        self.setMinimumSize(200, 600)  # Lowered minimum width to allow horizontal shrinking
        
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
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_data)
        self.save_button.setObjectName("primary-button")
        self.save_button.setEnabled(False)  # Initially disabled
        self.main_layout.addWidget(self.save_button)

        # Add done button below save button
        self.done_button = QPushButton("Done")
        self.done_button.clicked.connect(self.handle_done)
        self.done_button.setObjectName("primary-button")
        self.main_layout.addWidget(self.done_button)

        # Track unsaved changes
        self.dirty = False
        
        # Update user dropdown and clear current selection
        self.update_user_dropdown()
        self.user_combo.setCurrentIndex(-1)
        
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
        
        # Reports menu
        reports_menu = menu_bar.addMenu("Reports")
        
        self.generate_report_action = QAction("Generate Report", self)
        self.generate_report_action.triggered.connect(self.show_report_dialog)
        reports_menu.addAction(self.generate_report_action)
        self.generate_report_action.setEnabled(False)

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
        self.add_user_button = QPushButton("+")
        self.add_user_button.setFixedWidth(40)
        self.add_user_button.setToolTip("Add new user")
        self.add_user_button.clicked.connect(self.add_user)
        user_layout.addWidget(self.add_user_button)
        
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
        counters_layout = QFormLayout(counters_group)
        counters_layout.setSpacing(10)
        # Allow fields in the form to expand horizontally
        counters_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        
        # Create counters with a helper function
        self.counters = {}
        counter_names = [
            "Calls", "Connections", "Email", "SMS", "Form6 Sent", 
            "Form6 Received", "Leads", "Appointments", "CMA", 
            "Appraisals", "Tasks"
        ]
        
        for name in counter_names:
            field_name = name.lower().replace(" ", "_")
            counter_layout = QHBoxLayout()
            spin_box = QSpinBox()
            spin_box.setMinimum(0)
            spin_box.setMaximum(999)
            spin_box.setMinimumHeight(28)
            spin_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            spin_box.valueChanged.connect(lambda val, key=field_name: self.autosave())
            spin_box.valueChanged.connect(self.mark_dirty)
            counter_layout.addWidget(spin_box)
            counters_layout.addRow(name, counter_layout)
            self.counters[field_name] = spin_box
        
        self.main_layout.addWidget(counters_group)
        
        # Comments field
        self.main_layout.addWidget(QLabel("Comments:"))
        self.comments_edit = QTextEdit()
        # Remove fixed height and allow expansion using the correct QSizePolicy enum
        self.comments_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # NEW: Autosave on every change in comments
        self.comments_edit.textChanged.connect(self.autosave)
        self.comments_edit.textChanged.connect(self.mark_dirty)
        self.main_layout.addWidget(self.comments_edit)
        
        # Add stretch so extra space is used dynamically
        self.main_layout.addStretch()
    
    def update_user_dropdown(self):
        # Get users and update combo box with no default selection
        self.user_combo.blockSignals(True)
        self.user_combo.clear()
        users = self.data_manager.get_users()
        if users:
            self.user_combo.addItems(users)
            self.user_combo.setCurrentIndex(-1)  # No selection
        else:
            self.user_combo.setCurrentIndex(-1)
        self.user_combo.blockSignals(False)
        self.update_save_button_state()
    
    def update_save_button_state(self):
        # Enable Save only if a valid user is selected (index >= 0 and text not empty)
        idx = self.user_combo.currentIndex()
        txt = self.user_combo.currentText()
        enabled = idx >= 0 and bool(txt.strip())
        self.save_button.setEnabled(enabled)
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
        print("Autosave triggered. Entry data:", entry_data)
        QApplication.beep()
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
    
    def closeEvent(self, event):
        event.accept()
    
    def autosave(self):
        self.save_data()
        self.dirty = False

    def mark_dirty(self):
        self.dirty = True
        self.update_save_button_state()

    def handle_done(self):
        if self.dirty:
            reply = QMessageBox.question(self, "Unsaved Changes", "You have unsaved changes. Are you sure you want to exit?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                return
        QApplication.quit()