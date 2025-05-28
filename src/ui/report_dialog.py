from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QDateEdit, QPushButton, QTextEdit, QLineEdit,
                           QMessageBox, QFormLayout, QSizePolicy)
from PyQt6.QtCore import Qt, QDate
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
import json
import os

class ReportDialog(QDialog):
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        
        self.setWindowTitle("Generate Report")
        self.setMinimumSize(300, 400)  # Lower minimum width for horizontal resizing
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        layout = QVBoxLayout(self)
        
        # Date range selector
        date_form = QFormLayout()
        
        self.start_date = QDateEdit()
        # Default to start of current week (Monday)
        current_date = QDate.currentDate()
        start_of_week = current_date.addDays(1 - current_date.dayOfWeek())
        self.start_date.setDate(start_of_week)
        self.start_date.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.start_date.setCalendarPopup(True)
        date_form.addRow("Start Date:", self.start_date)
        
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
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
        layout.addWidget(self.report_display)
        
        # Email options
        email_layout = QFormLayout()
        
        self.email_to = QLineEdit()
        self.email_to.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        # Set default recipient emails if stored in data/default_emails.json
        default_emails = self.load_default_emails()
        if default_emails:
            self.email_to.setText(default_emails)
        email_layout.addRow("Email To:", self.email_to)
        
        layout.addLayout(email_layout)
        
        # Send button
        self.send_btn = QPushButton("Send Report")
        self.send_btn.clicked.connect(self.send_report)
        self.send_btn.setEnabled(False)  # Disabled until report is generated
        layout.addWidget(self.send_btn)
    
    def generate_report(self):
        start_date_str = self.start_date.date().toString("yyyy-MM-dd")
        end_date_str = self.end_date.date().toString("yyyy-MM-dd")
        
        # Get data for the date range
        data = self.data_manager.get_data_for_date_range(start_date_str, end_date_str)
        
        if not data:
            self.report_display.setText("No data found for the selected date range.")
            self.send_btn.setEnabled(False)
            return
        
        # Initialize aggregators
        user_totals = {}
        date_totals = {}
        overall_totals = {
            "calls": 0, "connections": 0, "email": 0, "sms": 0,
            "form6_sent": 0, "form6_received": 0, "leads": 0,
            "appointments": 0, "cma": 0, "appraisals": 0, "tasks": 0
        }
        
        # Aggregate data ensuring numeric conversion
        for entry in data:
            user = entry["user"]
            date = entry["date"]
            
            # Initialize user and date dictionaries if they don't exist
            if user not in user_totals:
                user_totals[user] = {k: 0 for k in overall_totals.keys()}
            if date not in date_totals:
                date_totals[date] = {k: 0 for k in overall_totals.keys()}
            
            # Aggregate the data
            for key in overall_totals.keys():
                if key in entry:
                    try:
                        value = int(entry.get(key, 0))
                    except Exception:
                        value = 0
                    user_totals[user][key] += value
                    date_totals[date][key] += value
                    overall_totals[key] += value
        
        # Generate the report
        report = f"# Call Tally Report\n"
        report += f"Period: {start_date_str} to {end_date_str}\n\n"
        
        report += "## Overall Totals\n"
        for key, value in overall_totals.items():
            report += f"{key.replace('_', ' ').title()}: {value}\n"
        
        report += "\n## User Breakdown\n"
        for user, totals in user_totals.items():
            report += f"\n### {user}\n"
            for key, value in totals.items():
                report += f"{key.replace('_', ' ').title()}: {value}\n"
        
        report += "\n## Daily Breakdown\n"
        for date in sorted(date_totals.keys()):
            report += f"\n### {date}\n"
            totals = date_totals[date]
            for key, value in totals.items():
                report += f"{key.replace('_', ' ').title()}: {value}\n"
        
        self.report_display.setText(report)
        self.send_btn.setEnabled(True)
        self.current_report = report
    
    def send_report(self):
        if not hasattr(self, 'current_report'):
            QMessageBox.warning(self, "Error", "Please generate a report first")
            return
        
        to_email = self.email_to.text().strip()
        if not to_email:
            QMessageBox.warning(self, "Error", "Please enter a recipient email address")
            return
        
        # Load email settings
        try:
            # In a real application, you would store these securely, not in the code
            # This is just a placeholder implementation
            
            # Check if we have stored SMTP settings
            settings_file = "data/email_settings.json"
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    smtp_server = settings.get('smtp_server')
                    smtp_port = settings.get('smtp_port')
                    smtp_user = settings.get('smtp_user')
                    smtp_password = settings.get('smtp_password')
                    from_email = settings.get('from_email')
            else:
                # Prompt for settings in a real app
                QMessageBox.information(
                    self, 
                    "Email Setup Required", 
                    "Email settings not configured. Please set up SMTP details in Settings menu."
                )
                return
                
            # Create report email
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = f"Call Tally Report {self.start_date.date().toString('yyyy-MM-dd')} to {self.end_date.date().toString('yyyy-MM-dd')}"
            
            # Convert report to HTML
            html_report = "<html><body><pre>" + self.current_report + "</pre></body></html>"
            msg.attach(MIMEText(html_report, 'html'))
            
            # This would send the email in a real application
            # with smtplib.SMTP(smtp_server, smtp_port) as server:
            #     server.login(smtp_user, smtp_password)
            #     server.send_message(msg)
            
            # For demonstration, we'll just show success
            QMessageBox.information(
                self, 
                "Success", 
                f"Report would be sent to {to_email} in a real application.\n\n"
                "This is a placeholder for email functionality.\n\n"
                "For a complete implementation, you would need to configure SMTP settings."
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send email: {str(e)}")
    
    def load_default_emails(self):
        settings_file = "data/default_emails.json"
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    data = json.load(f)
                return data.get("default_emails", "")
            except Exception:
                return ""
        return ""