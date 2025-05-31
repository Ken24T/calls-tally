from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QCheckBox, QFormLayout, QGroupBox, QMessageBox, QTabWidget, QWidget)
from src.settings.settings_manager import SettingsManager

class SettingsDialog(QDialog):
    def __init__(self, settings_manager: SettingsManager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager # Use the passed instance
        self.setWindowTitle("Settings")
        self.setFixedSize(400, 300)
        self.setModal(True)
        
        self.init_ui()
        self.load_current_settings()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Create tabs
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # General settings tab
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        
        # Window settings group
        window_group = QGroupBox("Window Settings")
        window_layout = QFormLayout(window_group)
        
        self.remember_position_cb = QCheckBox("Remember window position")
        window_layout.addRow(self.remember_position_cb)
        
        general_layout.addWidget(window_group)
        general_layout.addStretch()
        tab_widget.addTab(general_tab, "General")
        
        # Email settings tab
        email_tab = QWidget()
        email_layout = QVBoxLayout(email_tab)
        
        # Default Email Recipients group
        default_recipients_group = QGroupBox("Default Email Recipients")
        default_recipients_form_layout = QFormLayout(default_recipients_group)
        
        self.default_emails_edit = QLineEdit()
        self.default_emails_edit.setMinimumHeight(32)
        self.default_emails_edit.setPlaceholderText("Enter default recipient emails (semicolon separated)")
        
        default_email_label = QLabel("Default Recipients:")
        default_email_label.setToolTip("Default email addresses to populate when sending reports (separate multiple emails with semicolons)")
        
        default_recipients_form_layout.addRow(default_email_label, self.default_emails_edit)
        
        # Info label about mailto
        info_label = QLabel("Note: Reports are sent using your default email application (e.g., Outlook).")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray; font-style: italic;")
        
        email_layout.addWidget(default_recipients_group)
        email_layout.addWidget(info_label)
        email_layout.addStretch()
        tab_widget.addTab(email_tab, "Email")
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept_settings)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)

    def load_current_settings(self):
        # Load general settings
        remember_pos = self.settings_manager.get('remember_window_position', False)
        self.remember_position_cb.setChecked(bool(remember_pos))
        
        # Load default emails
        default_emails = self.settings_manager.get('default_emails', '')
        self.default_emails_edit.setText(str(default_emails))

    def accept_settings(self):
        # Save general settings
        self.settings_manager.set('remember_window_position', self.remember_position_cb.isChecked())
        
        # Save default emails
        self.settings_manager.set('default_emails', self.default_emails_edit.text())
        
        QMessageBox.information(self, "Settings", "Settings saved successfully!")
        self.accept()