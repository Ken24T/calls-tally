from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, 
                           QDateEdit, QPushButton, QTextEdit, QLineEdit,
                           QMessageBox, QFormLayout, QSizePolicy, QHBoxLayout)
from PyQt6.QtCore import QDate
import webbrowser
import urllib.parse # Re-add for mailto URL encoding

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
        user_name = None
        if data:
            user_name = data[0].get("user", None)
        if not data:
            self.report_display.setText("No data found for the selected date range.")
            self.send_btn.setEnabled(False)
            return
        
        def aggregate_new_structure(data, section_key):
            """Aggregate data for new schema structure"""
            result = {
                'call_connects': {'paid_lead': 0, 'organic_lead': 0, 'agents': 0, 'total': 0},
                'call_nonconnects': {'paid_lead': 0, 'organic_lead': 0, 'agents': 0, 'total': 0},
                'call_inbetweens': {'paid_lead': 0, 'organic_lead': 0, 'agents': 0, 'total': 0},
                'other': {'sms': 0, 'email': 0, 'total': 0},
                'grand_total': 0,
                'enrolment_packs': 0,
                'quotes': 0,
                'cpd_booked': 0,
                'grand_total_2': 0
            }
            
            for entry in data:
                section = entry.get(section_key, {})
                if not section:
                    continue
                
                # Aggregate each call section
                for call_section in ['call_connects', 'call_nonconnects', 'call_inbetweens']:
                    call_data = section.get(call_section, {})
                    for field in ['paid_lead', 'organic_lead', 'agents', 'total']:
                        try:
                            result[call_section][field] += int(call_data.get(field, 0))
                        except (ValueError, TypeError):
                            pass
                
                # Aggregate OTHER
                other_data = section.get('other', {})
                for field in ['sms', 'email', 'total']:
                    try:
                        result['other'][field] += int(other_data.get(field, 0))
                    except (ValueError, TypeError):
                        pass
                
                # Aggregate grand totals and additional metrics
                try:
                    result['grand_total'] += int(section.get('grand_total', 0))
                except (ValueError, TypeError):
                    pass
                try:
                    result['enrolment_packs'] += int(section.get('enrolment_packs', 0))
                except (ValueError, TypeError):
                    pass
                try:
                    result['quotes'] += int(section.get('quotes', 0))
                except (ValueError, TypeError):
                    pass
                try:
                    result['cpd_booked'] += int(section.get('cpd_booked', 0))
                except (ValueError, TypeError):
                    pass
                try:
                    result['grand_total_2'] += int(section.get('grand_total_2', 0))
                except (ValueError, TypeError):
                    pass
            
            return result
        
        report_lines = []
        if user_name:
            report_lines.append(f"Touch-Point Tracker Report for {user_name}")
        else:
            report_lines.append("Touch-Point Tracker Report")
        report_lines.append(f"Period: {start_date_str} to {end_date_str}")
        
        for tab_label, section_key in [("Current Leads", "current_leads"), ("Prospects", "prospects")]:
            report_lines.append(f"\n=== {tab_label} ===")
            agg = aggregate_new_structure(data, section_key)
            
            # CALL - Connects
            report_lines.append("\nCALL - Connects:")
            report_lines.append(f"  Paid Lead: {agg['call_connects']['paid_lead']}")
            report_lines.append(f"  Organic Lead: {agg['call_connects']['organic_lead']}")
            report_lines.append(f"  Agents: {agg['call_connects']['agents']}")
            report_lines.append(f"  Total: {agg['call_connects']['total']}")
            
            # CALL - Non-Connects
            report_lines.append("\nCALL - Non-Connects:")
            report_lines.append(f"  Paid Lead: {agg['call_nonconnects']['paid_lead']}")
            report_lines.append(f"  Organic Lead: {agg['call_nonconnects']['organic_lead']}")
            report_lines.append(f"  Agents: {agg['call_nonconnects']['agents']}")
            report_lines.append(f"  Total: {agg['call_nonconnects']['total']}")
            
            # CALL - In Betweens
            report_lines.append("\nCALL - In Betweens:")
            report_lines.append(f"  Paid Lead: {agg['call_inbetweens']['paid_lead']}")
            report_lines.append(f"  Organic Lead: {agg['call_inbetweens']['organic_lead']}")
            report_lines.append(f"  Agents: {agg['call_inbetweens']['agents']}")
            report_lines.append(f"  Total: {agg['call_inbetweens']['total']}")
            
            # OTHER
            report_lines.append("\nOTHER:")
            report_lines.append(f"  SMS: {agg['other']['sms']}")
            report_lines.append(f"  Email: {agg['other']['email']}")
            report_lines.append(f"  Total: {agg['other']['total']}")
            
            # GRAND TOTAL
            report_lines.append(f"\nGRAND TOTAL: {agg['grand_total']}")
            
            # Additional Metrics
            report_lines.append(f"\nEnrolment Packs: {agg['enrolment_packs']}")
            report_lines.append(f"Quotes: {agg['quotes']}")
            report_lines.append(f"CPD Booked: {agg['cpd_booked']}")
            
            # GRAND TOTAL 2
            report_lines.append(f"\nGRAND TOTAL: {agg['grand_total_2']}")
        
        # Add comments/notes section
        comments_with_dates = []
        for entry in data:
            comment = entry.get("comments", "").strip()
            if comment:
                date = entry.get("date", "")
                comments_with_dates.append((date, comment))
        
        if comments_with_dates:
            # Sort by date
            comments_with_dates.sort(key=lambda x: x[0])
            report_lines.append("\n=== Notes ===")
            for date, comment in comments_with_dates:
                report_lines.append(f"\n{date}:")
                report_lines.append(f"  {comment}")
        
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
            subject = f"Touch-Point Tracker Report {start_date_str} to {end_date_str}"

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