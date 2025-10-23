from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QComboBox, QDateEdit, QTextEdit, QPushButton, QMessageBox, QFormLayout, 
    QSpinBox, QInputDialog, QSizePolicy, QApplication, QTabWidget, QMenuBar, QGroupBox)
from PyQt6.QtGui import QAction, QTextCharFormat, QFont, QGuiApplication
from PyQt6.QtCore import QDate, Qt
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
        self.setWindowTitle("Touch-Point Tracker")
        self.setMinimumSize(400, 950)  # Minimum size for new layout
        
        # Apply window geometry (position and size) if remember setting is enabled
        self.apply_window_geometry()
        
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
        if not isinstance(menu_bar, QMenuBar):
            menu_bar = QMenuBar(self)
            self.setMenuBar(menu_bar)
        # Users menu
        users_menu = menu_bar.addMenu("Users")
        if users_menu is not None:
            add_user_action = QAction("Add User", self)
            add_user_action.triggered.connect(self.add_user)
            users_menu.addAction(add_user_action)
        
        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")
        if edit_menu is not None:
            settings_action = QAction("Settings", self)
            settings_action.triggered.connect(self.show_settings_dialog)
            edit_menu.addAction(settings_action)
        
        # Reports menu
        reports_menu = menu_bar.addMenu("Reports")
        if reports_menu is not None:
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
        self.user_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        user_layout.addWidget(self.user_combo)
        
        # Date selection
        date_layout = QHBoxLayout()
        self.main_layout.addLayout(date_layout)
        
        date_label = QLabel("Date:")
        date_label.setObjectName("required-field")
        date_layout.addWidget(date_label)
        
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        date_layout.addWidget(self.date_edit)
        self.current_date_str = self.date_edit.date().toString("yyyy-MM-dd")
        
        # Initialize widget dictionaries for tracking
        self.current_leads_widgets = {}
        self.prospects_widgets = {}
        
        # Initialize override tracking dictionaries
        self.current_leads_overrides = {}
        self.prospects_overrides = {}
        
        # Create tabs
        tab_widget = QTabWidget()
        tab_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Create Current Leads tab
        current_leads_tab = self._create_metrics_tab("current_leads")
        tab_widget.addTab(current_leads_tab, "Current Leads")
        
        # Create Prospects tab  
        prospects_tab = self._create_metrics_tab("prospects")
        tab_widget.addTab(prospects_tab, "Prospects")
        
        self.main_layout.addWidget(tab_widget)
        
        # Comments/Notes field
        self.comments_edit = QTextEdit()
        self.comments_edit.setPlaceholderText("Notes...")
        self.comments_edit.setMaximumHeight(100)
        self.comments_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.comments_edit.textChanged.connect(self.mark_dirty)
        self.comments_edit.textChanged.connect(self.autosave)
        self.main_layout.addWidget(self.comments_edit)
    
    def _create_metrics_tab(self, tab_name):
        """Create a metrics tab with the new structure"""
        tab_widget = QWidget()
        tab_layout = QVBoxLayout(tab_widget)
        tab_layout.setSpacing(10)
        tab_layout.setContentsMargins(10, 10, 10, 10)
        
        # Determine which widget dictionary to use
        widgets_dict = self.current_leads_widgets if tab_name == "current_leads" else self.prospects_widgets
        overrides_dict = self.current_leads_overrides if tab_name == "current_leads" else self.prospects_overrides
        
        # CALL - Connects Section
        connects_group = self._create_call_section("CALL - Connects", "call_connects", tab_name, widgets_dict, overrides_dict)
        tab_layout.addWidget(connects_group)
        
        # CALL - Non-Connects Section
        nonconnects_group = self._create_call_section("CALL - Non-Connects", "call_nonconnects", tab_name, widgets_dict, overrides_dict)
        tab_layout.addWidget(nonconnects_group)
        
        # CALL - In Betweens Section
        inbetweens_group = self._create_call_section("CALL - In Betweens", "call_inbetweens", tab_name, widgets_dict, overrides_dict)
        tab_layout.addWidget(inbetweens_group)
        
        # OTHER Section
        other_group = self._create_other_section(tab_name, widgets_dict, overrides_dict)
        tab_layout.addWidget(other_group)
        
        # GRAND TOTAL
        grand_total_layout = QHBoxLayout()
        grand_total_label = QLabel("<b>GRAND TOTAL:</b>")
        grand_total_layout.addWidget(grand_total_label)
        grand_total_layout.addStretch()
        
        grand_total_spinbox = QSpinBox()
        grand_total_spinbox.setMinimum(0)
        grand_total_spinbox.setMaximum(99999)
        grand_total_spinbox.setFixedWidth(100)
        grand_total_spinbox.setObjectName("grand-total")
        grand_total_spinbox.valueChanged.connect(lambda: self._on_total_manually_changed("grand_total", tab_name))
        widgets_dict["grand_total"] = grand_total_spinbox
        overrides_dict["grand_total"] = False
        grand_total_layout.addWidget(grand_total_spinbox)
        
        tab_layout.addLayout(grand_total_layout)
        
        # Additional Metrics Section
        additional_group = QGroupBox("Additional Metrics")
        additional_layout = QFormLayout()
        additional_layout.setSpacing(8)
        
        for metric_name, display_name in [
            ("enrolment_packs", "Enrolment Packs"),
            ("quotes", "Quotes"),
            ("cpd_booked", "CPD Booked")
        ]:
            spinbox = QSpinBox()
            spinbox.setMinimum(0)
            spinbox.setMaximum(999)
            spinbox.setFixedWidth(100)
            spinbox.valueChanged.connect(lambda val, mn=metric_name, tn=tab_name: self._on_additional_metric_changed(mn, tn))
            additional_layout.addRow(display_name + ":", spinbox)
            widgets_dict[metric_name] = spinbox
        
        additional_group.setLayout(additional_layout)
        tab_layout.addWidget(additional_group)
        
        # GRAND TOTAL 2
        grand_total_2_layout = QHBoxLayout()
        grand_total_2_label = QLabel("<b>GRAND TOTAL:</b>")
        grand_total_2_layout.addWidget(grand_total_2_label)
        grand_total_2_layout.addStretch()
        
        grand_total_2_spinbox = QSpinBox()
        grand_total_2_spinbox.setMinimum(0)
        grand_total_2_spinbox.setMaximum(99999)
        grand_total_2_spinbox.setFixedWidth(100)
        grand_total_2_spinbox.setObjectName("grand-total")
        grand_total_2_spinbox.valueChanged.connect(lambda: self._on_total_manually_changed("grand_total_2", tab_name))
        widgets_dict["grand_total_2"] = grand_total_2_spinbox
        overrides_dict["grand_total_2"] = False
        grand_total_2_layout.addWidget(grand_total_2_spinbox)
        
        tab_layout.addLayout(grand_total_2_layout)
        tab_layout.addStretch()
        
        return tab_widget
    
    def _create_call_section(self, title, section_key, tab_name, widgets_dict, overrides_dict):
        """Create a CALL section (Connects, Non-Connects, or In Betweens)"""
        group = QGroupBox(title)
        layout = QFormLayout()
        layout.setSpacing(8)
        
        # Create nested dictionary for this section
        widgets_dict[section_key] = {}
        overrides_dict[section_key] = False
        
        # Add input fields
        for field_name, display_name in [
            ("paid_lead", "Paid Lead"),
            ("organic_lead", "Organic Lead"),
            ("agents", "Agents")
        ]:
            spinbox = QSpinBox()
            spinbox.setMinimum(0)
            spinbox.setMaximum(999)
            spinbox.setFixedWidth(100)
            spinbox.valueChanged.connect(lambda val, sk=section_key, tn=tab_name: self._on_section_value_changed(sk, tn))
            layout.addRow(display_name + ":", spinbox)
            widgets_dict[section_key][field_name] = spinbox
        
        # Add Total field (editable)
        total_spinbox = QSpinBox()
        total_spinbox.setMinimum(0)
        total_spinbox.setMaximum(9999)
        total_spinbox.setFixedWidth(100)
        total_spinbox.setObjectName("total-field")
        total_spinbox.valueChanged.connect(lambda: self._on_section_total_manually_changed(section_key, tab_name))
        layout.addRow("<b>Total:</b>", total_spinbox)
        widgets_dict[section_key]["total"] = total_spinbox
        
        group.setLayout(layout)
        return group
    
    def _create_other_section(self, tab_name, widgets_dict, overrides_dict):
        """Create the OTHER section (SMS, Email)"""
        group = QGroupBox("OTHER")
        layout = QFormLayout()
        layout.setSpacing(8)
        
        widgets_dict["other"] = {}
        overrides_dict["other"] = False
        
        for field_name, display_name in [("sms", "SMS"), ("email", "Email")]:
            spinbox = QSpinBox()
            spinbox.setMinimum(0)
            spinbox.setMaximum(999)
            spinbox.setFixedWidth(100)
            spinbox.valueChanged.connect(lambda val, tn=tab_name: self._on_other_value_changed(tn))
            layout.addRow(display_name + ":", spinbox)
            widgets_dict["other"][field_name] = spinbox
        
        # Add Total field
        total_spinbox = QSpinBox()
        total_spinbox.setMinimum(0)
        total_spinbox.setMaximum(9999)
        total_spinbox.setFixedWidth(100)
        total_spinbox.setObjectName("total-field")
        total_spinbox.valueChanged.connect(lambda: self._on_other_total_manually_changed(tab_name))
        layout.addRow("<b>Total:</b>", total_spinbox)
        widgets_dict["other"]["total"] = total_spinbox
        
        group.setLayout(layout)
        return group
    
    # ============================================================================
    # Calculation Methods
    # ============================================================================
    
    def _on_section_value_changed(self, section_key, tab_name):
        """Called when paid_lead, organic_lead, or agents changes in a CALL section"""
        widgets_dict = self.current_leads_widgets if tab_name == "current_leads" else self.prospects_widgets
        overrides_dict = self.current_leads_overrides if tab_name == "current_leads" else self.prospects_overrides
        
        # Only recalculate if not manually overridden
        if not overrides_dict.get(section_key, False):
            total = self._calculate_section_total(widgets_dict[section_key])
            widgets_dict[section_key]["total"].blockSignals(True)
            widgets_dict[section_key]["total"].setValue(total)
            widgets_dict[section_key]["total"].setStyleSheet("")  # Clear override styling
            widgets_dict[section_key]["total"].blockSignals(False)
        
        # Recalculate grand total
        self._recalculate_grand_total(tab_name)
        self.mark_dirty()
        self.autosave()
    
    def _on_section_total_manually_changed(self, section_key, tab_name):
        """Called when user manually edits a section total"""
        overrides_dict = self.current_leads_overrides if tab_name == "current_leads" else self.prospects_overrides
        widgets_dict = self.current_leads_widgets if tab_name == "current_leads" else self.prospects_widgets
        
        # Mark as overridden
        overrides_dict[section_key] = True
        # Apply visual indicator
        widgets_dict[section_key]["total"].setStyleSheet("background-color: #FFFACD;")
        widgets_dict[section_key]["total"].setToolTip("Manually overridden. Change component values to reset.")
        
        # Recalculate grand total
        self._recalculate_grand_total(tab_name)
        self.mark_dirty()
        self.autosave()
    
    def _on_other_value_changed(self, tab_name):
        """Called when SMS or Email changes in OTHER section"""
        widgets_dict = self.current_leads_widgets if tab_name == "current_leads" else self.prospects_widgets
        overrides_dict = self.current_leads_overrides if tab_name == "current_leads" else self.prospects_overrides
        
        # Only recalculate if not manually overridden
        if not overrides_dict.get("other", False):
            total = widgets_dict["other"]["sms"].value() + widgets_dict["other"]["email"].value()
            widgets_dict["other"]["total"].blockSignals(True)
            widgets_dict["other"]["total"].setValue(total)
            widgets_dict["other"]["total"].setStyleSheet("")
            widgets_dict["other"]["total"].blockSignals(False)
        
        # Recalculate grand total
        self._recalculate_grand_total(tab_name)
        self.mark_dirty()
        self.autosave()
    
    def _on_other_total_manually_changed(self, tab_name):
        """Called when user manually edits OTHER total"""
        overrides_dict = self.current_leads_overrides if tab_name == "current_leads" else self.prospects_overrides
        widgets_dict = self.current_leads_widgets if tab_name == "current_leads" else self.prospects_widgets
        
        overrides_dict["other"] = True
        widgets_dict["other"]["total"].setStyleSheet("background-color: #FFFACD;")
        widgets_dict["other"]["total"].setToolTip("Manually overridden. Change SMS/Email to reset.")
        
        self._recalculate_grand_total(tab_name)
        self.mark_dirty()
        self.autosave()
    
    def _on_additional_metric_changed(self, metric_name, tab_name):
        """Called when enrolment_packs, quotes, or cpd_booked changes"""
        self._recalculate_grand_total_2(tab_name)
        self.mark_dirty()
        self.autosave()
    
    def _on_total_manually_changed(self, total_type, tab_name):
        """Called when user manually edits grand_total or grand_total_2"""
        overrides_dict = self.current_leads_overrides if tab_name == "current_leads" else self.prospects_overrides
        widgets_dict = self.current_leads_widgets if tab_name == "current_leads" else self.prospects_widgets
        
        overrides_dict[total_type] = True
        widgets_dict[total_type].setStyleSheet("background-color: #FFFACD;")
        widgets_dict[total_type].setToolTip("Manually overridden. Change component values to reset.")
        
        self.mark_dirty()
        self.autosave()
    
    def _calculate_section_total(self, section_widgets):
        """Calculate total for a CALL section"""
        return (section_widgets["paid_lead"].value() + 
                section_widgets["organic_lead"].value() + 
                section_widgets["agents"].value())
    
    def _recalculate_grand_total(self, tab_name):
        """Recalculate GRAND TOTAL (sum of all CALL sections + OTHER)"""
        widgets_dict = self.current_leads_widgets if tab_name == "current_leads" else self.prospects_widgets
        overrides_dict = self.current_leads_overrides if tab_name == "current_leads" else self.prospects_overrides
        
        # Only recalculate if not manually overridden
        if not overrides_dict.get("grand_total", False):
            total = (widgets_dict["call_connects"]["total"].value() +
                    widgets_dict["call_nonconnects"]["total"].value() +
                    widgets_dict["call_inbetweens"]["total"].value() +
                    widgets_dict["other"]["total"].value())
            
            widgets_dict["grand_total"].blockSignals(True)
            widgets_dict["grand_total"].setValue(total)
            widgets_dict["grand_total"].setStyleSheet("")
            widgets_dict["grand_total"].blockSignals(False)
    
    def _recalculate_grand_total_2(self, tab_name):
        """Recalculate GRAND TOTAL 2 (sum of additional metrics)"""
        widgets_dict = self.current_leads_widgets if tab_name == "current_leads" else self.prospects_widgets
        overrides_dict = self.current_leads_overrides if tab_name == "current_leads" else self.prospects_overrides
        
        # Only recalculate if not manually overridden
        if not overrides_dict.get("grand_total_2", False):
            total = (widgets_dict["enrolment_packs"].value() +
                    widgets_dict["quotes"].value() +
                    widgets_dict["cpd_booked"].value())
            
            widgets_dict["grand_total_2"].blockSignals(True)
            widgets_dict["grand_total_2"].setValue(total)
            widgets_dict["grand_total_2"].setStyleSheet("")
            widgets_dict["grand_total_2"].blockSignals(False)
    
    def _recalculate_all_totals(self):
        """Recalculate all totals for both tabs"""
        for tab_name in ["current_leads", "prospects"]:
            widgets_dict = self.current_leads_widgets if tab_name == "current_leads" else self.prospects_widgets
            overrides_dict = self.current_leads_overrides if tab_name == "current_leads" else self.prospects_overrides
            
            # Recalculate section totals
            for section_key in ["call_connects", "call_nonconnects", "call_inbetweens"]:
                if not overrides_dict.get(section_key, False):
                    total = self._calculate_section_total(widgets_dict[section_key])
                    widgets_dict[section_key]["total"].blockSignals(True)
                    widgets_dict[section_key]["total"].setValue(total)
                    widgets_dict[section_key]["total"].blockSignals(False)
            
            # Recalculate other total
            if not overrides_dict.get("other", False):
                total = widgets_dict["other"]["sms"].value() + widgets_dict["other"]["email"].value()
                widgets_dict["other"]["total"].blockSignals(True)
                widgets_dict["other"]["total"].setValue(total)
                widgets_dict["other"]["total"].blockSignals(False)
            
            # Recalculate grand totals
            self._recalculate_grand_total(tab_name)
            self._recalculate_grand_total_2(tab_name)
    
    # ============================================================================
    # Existing Methods (to be updated)
    # ============================================================================
    
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
        """Save entry data with new schema"""
        # Validate form
        if self.user_combo.currentText() == "":
            QMessageBox.warning(self, "Error", "Please select a caller")
            return
        
        if date_str_override is not None:
            date_str = date_str_override
        else:
            date_str = self.date_edit.date().toString("yyyy-MM-dd")
        
        # Extract data from both tabs
        current_leads_data = self._extract_tab_data(self.current_leads_widgets)
        prospects_data = self._extract_tab_data(self.prospects_widgets)
        
        entry_data = {
            "user": self.user_combo.currentText(),
            "date": date_str,
            "current_leads": current_leads_data,
            "prospects": prospects_data,
            "comments": self.comments_edit.toPlainText()
        }
        
        self.data_manager.save_entry(entry_data)
        self.dirty = False
    
    def _extract_tab_data(self, widgets_dict):
        """Extract data from widget dictionary into save format"""
        data = {}
        
        # Extract CALL sections
        for section_key in ["call_connects", "call_nonconnects", "call_inbetweens"]:
            data[section_key] = {
                "paid_lead": widgets_dict[section_key]["paid_lead"].value(),
                "organic_lead": widgets_dict[section_key]["organic_lead"].value(),
                "agents": widgets_dict[section_key]["agents"].value(),
                "total": widgets_dict[section_key]["total"].value()
            }
        
        # Extract OTHER section
        data["other"] = {
            "sms": widgets_dict["other"]["sms"].value(),
            "email": widgets_dict["other"]["email"].value(),
            "total": widgets_dict["other"]["total"].value()
        }
        
        # Extract standalone fields
        data["grand_total"] = widgets_dict["grand_total"].value()
        data["enrolment_packs"] = widgets_dict["enrolment_packs"].value()
        data["quotes"] = widgets_dict["quotes"].value()
        data["cpd_booked"] = widgets_dict["cpd_booked"].value()
        data["grand_total_2"] = widgets_dict["grand_total_2"].value()
        
        return data

    def load_user_entry(self):
        """Load existing entry data for the selected user and date into the UI."""
        self.current_date_str = self.date_edit.date().toString("yyyy-MM-dd")
        user = self.user_combo.currentText()
        if not user:
            return
        
        date_str = self.date_edit.date().toString("yyyy-MM-dd")
        entry = self.data_manager.get_entry_for_user_and_date(user, date_str)
        
        # Block all signals during load
        self._block_all_signals(True)
        
        if entry:
            # Load current leads data
            self._populate_tab_widgets(self.current_leads_widgets, entry.get("current_leads", {}))
            # Load prospects data
            self._populate_tab_widgets(self.prospects_widgets, entry.get("prospects", {}))
            # Load comments
            self.comments_edit.setText(entry.get("comments", ""))
        else:
            # Clear all to zeros
            self._clear_all_widgets()
        
        # Unblock signals
        self._block_all_signals(False)
        
        # Reset override flags (data loaded from file is not considered overridden)
        self._reset_all_overrides()
        
        # Recalculate all totals to ensure consistency
        self._recalculate_all_totals()
        
        self.update_calendar_styles()
        self.dirty = False
    
    def _populate_tab_widgets(self, widgets_dict, data):
        """Populate widgets from loaded data"""
        # Populate CALL sections
        for section_key in ["call_connects", "call_nonconnects", "call_inbetweens"]:
            section_data = data.get(section_key, {})
            for field in ["paid_lead", "organic_lead", "agents", "total"]:
                value = section_data.get(field, 0)
                widgets_dict[section_key][field].setValue(value)
        
        # Populate OTHER section
        other_data = data.get("other", {})
        for field in ["sms", "email", "total"]:
            value = other_data.get(field, 0)
            widgets_dict["other"][field].setValue(value)
        
        # Populate standalone fields
        widgets_dict["grand_total"].setValue(data.get("grand_total", 0))
        widgets_dict["enrolment_packs"].setValue(data.get("enrolment_packs", 0))
        widgets_dict["quotes"].setValue(data.get("quotes", 0))
        widgets_dict["cpd_booked"].setValue(data.get("cpd_booked", 0))
        widgets_dict["grand_total_2"].setValue(data.get("grand_total_2", 0))
    
    def _clear_all_widgets(self):
        """Clear all widgets to zero"""
        for widgets_dict in [self.current_leads_widgets, self.prospects_widgets]:
            # Clear CALL sections
            for section_key in ["call_connects", "call_nonconnects", "call_inbetweens"]:
                for field in ["paid_lead", "organic_lead", "agents", "total"]:
                    widgets_dict[section_key][field].setValue(0)
            
            # Clear OTHER section
            for field in ["sms", "email", "total"]:
                widgets_dict["other"][field].setValue(0)
            
            # Clear standalone fields
            widgets_dict["grand_total"].setValue(0)
            widgets_dict["enrolment_packs"].setValue(0)
            widgets_dict["quotes"].setValue(0)
            widgets_dict["cpd_booked"].setValue(0)
            widgets_dict["grand_total_2"].setValue(0)
        
        self.comments_edit.clear()
    
    def _block_all_signals(self, block):
        """Block or unblock signals for all widgets"""
        for widgets_dict in [self.current_leads_widgets, self.prospects_widgets]:
            # Block CALL sections
            for section_key in ["call_connects", "call_nonconnects", "call_inbetweens"]:
                for widget in widgets_dict[section_key].values():
                    widget.blockSignals(block)
            
            # Block OTHER section
            for widget in widgets_dict["other"].values():
                widget.blockSignals(block)
            
            # Block standalone fields
            widgets_dict["grand_total"].blockSignals(block)
            widgets_dict["enrolment_packs"].blockSignals(block)
            widgets_dict["quotes"].blockSignals(block)
            widgets_dict["cpd_booked"].blockSignals(block)
            widgets_dict["grand_total_2"].blockSignals(block)
        
        self.comments_edit.blockSignals(block)
    
    def _reset_all_overrides(self):
        """Reset all override flags and styling"""
        for tab_name in ["current_leads", "prospects"]:
            widgets_dict = self.current_leads_widgets if tab_name == "current_leads" else self.prospects_widgets
            overrides_dict = self.current_leads_overrides if tab_name == "current_leads" else self.prospects_overrides
            
            # Reset section overrides
            for section_key in ["call_connects", "call_nonconnects", "call_inbetweens"]:
                overrides_dict[section_key] = False
                widgets_dict[section_key]["total"].setStyleSheet("")
                widgets_dict[section_key]["total"].setToolTip("")
            
            # Reset other override
            overrides_dict["other"] = False
            widgets_dict["other"]["total"].setStyleSheet("")
            widgets_dict["other"]["total"].setToolTip("")
            
            # Reset grand total overrides
            overrides_dict["grand_total"] = False
            widgets_dict["grand_total"].setStyleSheet("")
            widgets_dict["grand_total"].setToolTip("")
            
            overrides_dict["grand_total_2"] = False
            widgets_dict["grand_total_2"].setStyleSheet("")
            widgets_dict["grand_total_2"].setToolTip("")
    
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
        self.save_window_geometry()
        if a0 is not None and hasattr(a0, 'accept'):
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
        self.save_window_geometry()
        QApplication.quit()

    def apply_window_geometry(self):
        """Apply saved window position and size, or use defaults"""
        if self.settings_manager.get('remember_window_position', False):
            geometry = self.settings_manager.get('window_position', {
                'x': 100, 'y': 100, 'width': 400, 'height': 950, 'screen_name': ''
            })
            
            # Extract values
            x = geometry.get('x', 100)
            y = geometry.get('y', 100)
            width = geometry.get('width', 400)
            height = geometry.get('height', 950)
            screen_name = geometry.get('screen_name', '')
            
            # Find target screen
            target_screen = None
            if screen_name:
                for screen in QGuiApplication.screens():
                    if screen.name() == screen_name:
                        target_screen = screen
                        break
            
            # Validate and constrain position/size to screen bounds
            if target_screen:
                screen_geometry = target_screen.availableGeometry()
                x = max(screen_geometry.x(), min(x, screen_geometry.x() + screen_geometry.width() - width))
                y = max(screen_geometry.y(), min(y, screen_geometry.y() + screen_geometry.height() - height))
                width = min(width, screen_geometry.width())
                height = min(height, screen_geometry.height())
            
            # Apply geometry
            self.setGeometry(x, y, width, height)
        else:
            # Use default size and center on screen
            self.resize(400, 950)
            screen = QGuiApplication.primaryScreen()
            if screen:
                screen_geometry = screen.availableGeometry()
                center_x = screen_geometry.x() + (screen_geometry.width() - 400) // 2
                center_y = screen_geometry.y() + (screen_geometry.height() - 950) // 2
                self.move(center_x, center_y)

    def save_window_geometry(self):
        """Save current window position and size"""
        if self.settings_manager.get('remember_window_position', False):
            pos = self.pos()
            size = self.size()
            
            # Find which screen the window is currently on
            current_screen = QGuiApplication.screenAt(pos)
            screen_name = current_screen.name() if current_screen else ''
            
            geometry_data = {
                'x': pos.x(),
                'y': pos.y(),
                'width': size.width(),
                'height': size.height(),
                'screen_name': screen_name
            }
            self.settings_manager.set('window_position', geometry_data)