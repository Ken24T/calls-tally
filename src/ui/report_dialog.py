from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, 
                           QDateEdit, QPushButton, QTextEdit, QLineEdit,
                           QMessageBox, QFormLayout, QSizePolicy, QHBoxLayout)
from PyQt6.QtCore import QDate
import webbrowser
import urllib.parse # Re-add for mailto URL encoding
import datetime  # Added for weekday name

class ReportDialog(QDialog):
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        
        self.setWindowTitle("Generate Report")
        self.setMinimumSize(300, 400)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        layout = QVBoxLayout(self)
        
        # Date range selector
        date_form = QFormLayout()
        
        self.start_date = QDateEdit()
        current_date = QDate.currentDate()
        # Monday of the current week (dayOfWeek() is 1 for Monday, 7 for Sunday)
        start_of_week = current_date.addDays(1 - current_date.dayOfWeek())
        self.start_date.setDate(start_of_week)
        self.start_date.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.start_date.setCalendarPopup(True)
        date_form.addRow("Start Date:", self.start_date)
        
        self.end_date = QDateEdit()
        # Sunday of the current week
        end_of_week = current_date.addDays(7 - current_date.dayOfWeek())
        self.end_date.setDate(end_of_week) # Set to Sunday of the current week
        self.end_date.setCalendarPopup(True)
        self.end_date.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        date_form.addRow("End Date:", self.end_date)
        
        layout.addLayout(date_form)
        
        # Generate report button
        generate_btn = QPushButton("Generate Report")
        generate_btn.clicked.connect(self.generate_report)
        layout.addWidget(generate_btn)
        
        # Report display
        layout.addWidget(QLabel("Report Preview:"))
        self.report_display = QTextEdit()
        self.report_display.setReadOnly(True)
        self.report_display.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.report_display)        # Email options
        email_layout = QFormLayout()
        
        self.email_to = QLineEdit()
        self.email_to.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.email_to.setPlaceholderText("Optional: Enter recipient email")
        # Set default recipient emails from settings
        default_emails = self.load_default_emails()
        if default_emails:
            self.email_to.setText(default_emails)
        email_layout.addRow("Email To:", self.email_to)
        
        layout.addLayout(email_layout)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch() # Add stretch to push buttons to the right

        self.send_btn = QPushButton("Send Report via Email")
        self.send_btn.clicked.connect(self.send_report)
        self.send_btn.setEnabled(False)
        self.send_btn.setStyleSheet("background-color: #ADD8E6;") # Example color
        buttons_layout.addWidget(self.send_btn)

        done_button = QPushButton("Done")
        done_button.clicked.connect(self.accept) # Changed from self.close to self.accept for standard dialog behavior
        done_button.setStyleSheet("background-color: #ADD8E6;") # Example color
        buttons_layout.addWidget(done_button)
        
        layout.addLayout(buttons_layout) # Add the horizontal buttons layout to the main vertical layout
    
    def generate_report(self):
        start_date_str = self.start_date.date().toString("yyyy-MM-dd")
        end_date_str = self.end_date.date().toString("yyyy-MM-dd")
        data = self.data_manager.get_data_for_date_range(start_date_str, end_date_str)
        if not data:
            self.report_display.setText("No data found for the selected date range.")
            self.send_btn.setEnabled(False)
            return
        sources = ["google", "c-fox", "courses.com.au", "organic", "agents"]
        section_types = [("Connects", "connects"), ("Non-Connects", "nonconnects")]
        def aggregate_section(data, section_key):
            # section_key: 'current_leads' or 'prospects'
            # Returns: {section_type: {source: total}}
            result = {stype: {src: 0 for src in sources} for stype, _ in section_types}
            for entry in data:
                section = entry.get(section_key, {})
                # Backward compatibility: if section missing, skip
                if not section:
                    continue
                for stype, suffix in section_types:
                    for src in sources:
                        key = f"{src}_{suffix}"
                        try:
                            value = int(section.get(key, 0))
                        except (ValueError, TypeError):
                            value = 0
                        result[stype][src] += value
            return result
        report_lines = []
        report_lines.append("Call Tracker Report")
        report_lines.append(f"Period: {start_date_str} to {end_date_str}")
        for tab_label, section_key in [("Current Leads", "current_leads"), ("Prospects", "prospects")]:
            report_lines.append(f"\n=== {tab_label} ===")
            agg = aggregate_section(data, section_key)
            for stype, _ in section_types:
                report_lines.append(f"\n{stype} Totals:")
                for src in sources:
                    label = src.replace("courses.com.au", "Courses.com.au").replace("c-fox", "C-FOX").capitalize()
                    report_lines.append(f"  {label}: {agg[stype][src]}")
        report_text = "\n".join(report_lines)
        self.report_display.setText(report_text)
        self.current_generated_text = report_text
        self.send_btn.setEnabled(True)

    def send_report(self):
        try:
            if not hasattr(self, 'current_generated_text') or not self.current_generated_text.strip():
                QMessageBox.warning(self, "Warning", "No report content to send. Please generate a report first.")
                return
            
            report_plain_text = self.current_generated_text
            
            to_email = self.email_to.text().strip()
            start_date_str = self.start_date.date().toString("yyyy-MM-dd")
            end_date_str = self.end_date.date().toString("yyyy-MM-dd")
            subject = f"Call Tracker Report {start_date_str} to {end_date_str}"

            mailto_parts = []
            if to_email:
                # Handle multiple recipients if your UI supports it (e.g., semicolon separated)
                recipients = [r.strip() for r in to_email.split(';') if r.strip()]
                if recipients:
                    mailto_parts.append(",".join(recipients)) # mailto typically uses comma for multiple To's
            
            # Encode subject and body for the mailto URL
            encoded_subject = urllib.parse.quote(subject)
            encoded_body = urllib.parse.quote(report_plain_text)
            
            mailto_url = f"mailto:{';'.join(mailto_parts)}?subject={encoded_subject}&body={encoded_body}"
            
            webbrowser.open(mailto_url)

        except Exception as e:
            QMessageBox.critical(self, "Error Opening Email Client", f"Failed to open email client: {str(e)}")

    def load_default_emails(self):
        from src.settings.settings_manager import SettingsManager
        settings_manager = SettingsManager()
        return settings_manager.get('default_emails', '')