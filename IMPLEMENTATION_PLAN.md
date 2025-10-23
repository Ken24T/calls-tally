# Data Schema Change - Implementation Plan

## Overview
This document outlines the complete implementation plan for restructuring the Touch-Point Tracker application to support the new metrics and UI layout.

---

## 🎯 Goals

1. Replace current metrics structure with new categorized system
2. Implement editable totals that users can override
3. Add two separate "GRAND TOTAL" calculations
4. Make window resizable
5. Update reports to reflect new structure
6. Maintain existing features (autosave, notes, date selection, etc.)

---

## 📊 New Data Schema

### Structure for Both Tabs (Current Leads & Prospects)

```json
{
  "user": "John",
  "date": "2025-10-23",
  "current_leads": {
    "call_connects": {
      "paid_lead": 0,
      "organic_lead": 0,
      "agents": 0,
      "total": 0  // Can be auto-calculated or user-overridden
    },
    "call_nonconnects": {
      "paid_lead": 0,
      "organic_lead": 0,
      "agents": 0,
      "total": 0
    },
    "call_inbetweens": {
      "paid_lead": 0,
      "organic_lead": 0,
      "agents": 0,
      "total": 0
    },
    "other": {
      "sms": 0,
      "email": 0,
      "total": 0
    },
    "grand_total": 0,  // Sum of all above totals (user can override)
    "enrolment_packs": 0,
    "quotes": 0,
    "cpd_booked": 0,
    "grand_total_2": 0  // Sum of enrolment_packs + quotes + cpd_booked (user can override)
  },
  "prospects": {
    // Same structure as current_leads
  },
  "comments": "Daily notes here"
}
```

---

## 🔧 Implementation Phases

### **PHASE 1: Data Manager Updates**
**File**: `src/data/data_manager.py`

#### Tasks:
1. **Update `_ensure_data_file()`**
   - Initialize with new empty schema structure

2. **Create new method: `create_empty_entry_structure()`**
   - Returns a fresh entry object with new schema
   - Used when creating new entries or missing data

3. **Update `save_entry()`**
   - Handle new nested structure
   - Preserve user-overridden totals

4. **Update `get_entry_for_user_and_date()`**
   - Return entries with new structure
   - Handle missing fields gracefully (default to 0)

5. **No migration needed** - fresh start with new data

#### Data Validation:
- Ensure all numeric fields are integers
- Validate nested structure exists
- Handle backward compatibility gracefully (old data ignored)

---

### **PHASE 2: Main Window UI Restructuring**
**File**: `src/ui/main_window.py`

**Additional File**: `src/settings/settings_manager.py` (for window size persistence)

#### Tasks:

##### 2.1 Window Configuration
- Change from `setFixedSize(300, 860)` to `setMinimumSize(350, 900)`
- Allow window to be resizable
- Adjust layout policies for proper resizing behavior
- **Window Position & Size Persistence**:
  - If `remember_window_position` setting is True:
    - Restore both position AND size from settings on startup
    - Save both position AND size on window close
  - If `remember_window_position` setting is False:
    - Use default position and default size on startup
    - Default size: 350x900 (or suitable starting size)
    - Default position: Center of screen or (100, 100)

##### 2.2 Create New UI Components
Replace `create_form()` method with new structure:

**For each tab (Current Leads & Prospects):**

1. **CALL - Connects Section**
   - 3 SpinBox inputs: Paid Lead, Organic Lead, Agents
   - 1 Total field (SpinBox, editable, background color to indicate manual override)
   - Auto-calculate total on value change
   - Allow user override

2. **CALL - Non-Connects Section**
   - Same structure as Connects

3. **CALL - In Betweens Section**
   - Same structure as Connects

4. **OTHER Section**
   - 2 SpinBox inputs: SMS, Email
   - 1 Total field (editable)

5. **GRAND TOTAL**
   - Calculated: sum of all 4 section totals
   - Editable/overridable
   - Prominent styling (bold, larger font)

6. **Additional Metrics**
   - 3 SpinBox inputs: Enrolment Packs, Quotes, CPD Booked
   - Each standalone (no grouping total)

7. **GRAND TOTAL (Second)**
   - Calculated: Enrolment Packs + Quotes + CPD Booked
   - Editable/overridable
   - Prominent styling

8. **NOTES Section**
   - Keep existing QTextEdit for comments
   - Position at bottom

##### 2.3 Layout Strategy
```python
# Use QVBoxLayout with nested QFormLayouts for each section
# Structure:
MainVBoxLayout
  ├─ User/Date selection (existing)
  ├─ QTabWidget
  │   ├─ Current Leads Tab
  │   │   ├─ CALL - Connects (QGroupBox with QFormLayout)
  │   │   ├─ CALL - Non-Connects (QGroupBox with QFormLayout)
  │   │   ├─ CALL - In Betweens (QGroupBox with QFormLayout)
  │   │   ├─ OTHER (QGroupBox with QFormLayout)
  │   │   ├─ GRAND TOTAL (QLabel or editable QSpinBox)
  │   │   ├─ Additional Metrics (QFormLayout)
  │   │   └─ GRAND TOTAL 2 (QLabel or editable QSpinBox)
  │   └─ Prospects Tab (same structure)
  ├─ NOTES (QTextEdit)
  └─ Done Button
```

##### 2.4 Widget Tracking
Create dictionary structures to track all widgets:
```python
self.current_leads_widgets = {
    'call_connects': {
        'paid_lead': QSpinBox,
        'organic_lead': QSpinBox,
        'agents': QSpinBox,
        'total': QSpinBox
    },
    'call_nonconnects': {...},
    'call_inbetweens': {...},
    'other': {...},
    'grand_total': QSpinBox,
    'enrolment_packs': QSpinBox,
    'quotes': QSpinBox,
    'cpd_booked': QSpinBox,
    'grand_total_2': QSpinBox
}

self.prospects_widgets = {
    // Same structure
}
```

##### 2.5 Calculation Logic

**Method: `calculate_section_total(section_widgets)`**
- Sum paid_lead + organic_lead + agents
- Return calculated value
- Don't update if user has manually overridden

**Method: `calculate_grand_total_1(tab_widgets)`**
- Sum all section totals (call_connects + call_nonconnects + call_inbetweens + other)
- Return calculated value

**Method: `calculate_grand_total_2(tab_widgets)`**
- Sum enrolment_packs + quotes + cpd_booked
- Return calculated value

**Method: `on_section_value_changed(section_name, tab_name)`**
- Called when any section input changes
- Recalculate section total (if not manually overridden)
- Recalculate grand totals (if not manually overridden)
- Update UI labels/spinboxes
- Trigger autosave

**Method: `on_total_manually_changed(section_name, tab_name)`**
- Set flag indicating manual override
- Visual indicator (background color change)
- Still trigger autosave

**Method: `reset_total_to_calculated(section_name, tab_name)`**
- Right-click context menu option or button
- Clear manual override flag
- Recalculate from components
- Reset visual indicator

##### 2.8 Visual Indicators for Overrides
- **Normal calculated**: Default background color
- **User overridden**: Light yellow background (#FFFACD)
- **Tooltip**: "Manually overridden. Right-click to reset to calculated value"

##### 2.9 Window Size & Position Persistence

**Update SettingsManager (`settings_manager.py`)**:
```python
self.default_settings = {
    'remember_window_position': False,
    'window_position': {
        'x': 100, 
        'y': 100, 
        'width': 350,    # Add width
        'height': 900,   # Add height
        'screen_name': ''
    },
    'default_emails': ''
}
```

**Update MainWindow methods**:

1. **`apply_window_position()` → `apply_window_geometry()`**:
```python
def apply_window_geometry(self):
    """Apply saved window position and size, or use defaults"""
    if self.settings_manager.get('remember_window_position', False):
        geometry = self.settings_manager.get('window_position', {
            'x': 100, 'y': 100, 'width': 350, 'height': 900, 'screen_name': ''
        })
        
        # Extract values
        x = geometry.get('x', 100)
        y = geometry.get('y', 100)
        width = geometry.get('width', 350)
        height = geometry.get('height', 900)
        screen_name = geometry.get('screen_name', '')
        
        # Find target screen
        target_screen = None
        if screen_name:
            from PyQt6.QtGui import QGuiApplication
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
        # Use default size and center on screen (or fixed position)
        self.resize(350, 900)
        # Option 1: Center on screen
        from PyQt6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            center_x = screen_geometry.x() + (screen_geometry.width() - 350) // 2
            center_y = screen_geometry.y() + (screen_geometry.height() - 900) // 2
            self.move(center_x, center_y)
        # Option 2: Fixed default position
        # self.move(100, 100)
```

2. **`save_window_position()` → `save_window_geometry()`**:
```python
def save_window_geometry(self):
    """Save current window position and size"""
    if self.settings_manager.get('remember_window_position', False):
        from PyQt6.QtGui import QGuiApplication
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
```

3. **Update calls in `__init__()` and `closeEvent()`**:
```python
# In __init__, after creating window:
self.apply_window_geometry()  # Changed from apply_window_position()

# In closeEvent():
self.save_window_geometry()  # Changed from save_window_position()
```

**Update Settings Dialog UI**:
- Setting label: "Remember window position and size"
- Tooltip: "When enabled, the application will restore its position and size from the last session"
- JSON setting name: `remember_window_position` (keep same name for backward compatibility)



### **PHASE 3: Load/Save Logic**
**File**: `src/ui/main_window.py`

#### Tasks:

##### 3.1 Update `save_data()` method
```python
def save_data(self, date_str_override=None):
    # Validate user selected
    if not self.user_combo.currentText():
        return
    
    date_str = date_str_override or self.date_edit.date().toString("yyyy-MM-dd")
    
    # Build current_leads data
    current_leads_data = self._extract_tab_data(self.current_leads_widgets)
    
    # Build prospects data
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
    for section_name, section_widgets in widgets_dict.items():
        if isinstance(section_widgets, dict):
            data[section_name] = {
                key: widget.value() 
                for key, widget in section_widgets.items()
            }
        else:
            # Single widget (grand totals, etc.)
            data[section_name] = section_widgets.value()
    return data
```

##### 3.2 Update `load_user_entry()` method
```python
def load_user_entry(self):
    self.current_date_str = self.date_edit.date().toString("yyyy-MM-dd")
    user = self.user_combo.currentText()
    if not user:
        return
    
    date_str = self.date_edit.date().toString("yyyy-MM-dd")
    entry = self.data_manager.get_entry_for_user_and_date(user, date_str)
    
    # Block all signals
    self._block_all_signals(True)
    
    if entry:
        self._populate_tab_widgets(self.current_leads_widgets, entry.get("current_leads", {}))
        self._populate_tab_widgets(self.prospects_widgets, entry.get("prospects", {}))
        self.comments_edit.setText(entry.get("comments", ""))
    else:
        # Clear all to zeros
        self._clear_all_widgets()
    
    # Unblock signals
    self._block_all_signals(False)
    
    # Recalculate all totals
    self._recalculate_all_totals()
    
    self.dirty = False

def _populate_tab_widgets(self, widgets_dict, data):
    """Populate widgets from loaded data"""
    for section_name, section_data in data.items():
        if section_name in widgets_dict:
            if isinstance(section_data, dict):
                for key, value in section_data.items():
                    if key in widgets_dict[section_name]:
                        widgets_dict[section_name][key].setValue(value)
            else:
                # Single value
                widgets_dict[section_name].setValue(section_data)
```

---

### **PHASE 4: Report Generation Updates**
**File**: `src/ui/report_dialog.py`

#### Tasks:

##### 4.1 Update `generate_report()` method

New report format:
```
Touch-Point Tracker Report for [User]
Period: 2025-10-20 to 2025-10-26

=== Current Leads ===

CALL - Connects:
  Paid Lead: 15
  Organic Lead: 8
  Agents: 3
  Total: 26

CALL - Non-Connects:
  Paid Lead: 22
  Organic Lead: 12
  Agents: 5
  Total: 39

CALL - In Betweens:
  Paid Lead: 7
  Organic Lead: 4
  Agents: 1
  Total: 12

OTHER:
  SMS: 10
  Email: 15
  Total: 25

GRAND TOTAL: 102

Enrolment Packs: 5
Quotes: 8
CPD Booked: 3
GRAND TOTAL: 16

=== Prospects ===
[Same structure as Current Leads]

=== Notes ===

2025-10-20:
  Met with 3 new prospects today

2025-10-22:
  Follow-up calls scheduled for next week
```

##### 4.2 Aggregation Logic
```python
def aggregate_new_structure(data, section_key):
    """Aggregate data for new schema"""
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
                result[call_section][field] += int(call_data.get(field, 0))
        
        # Aggregate OTHER
        other_data = section.get('other', {})
        for field in ['sms', 'email', 'total']:
            result['other'][field] += int(other_data.get(field, 0))
        
        # Aggregate grand totals and additional metrics
        result['grand_total'] += int(section.get('grand_total', 0))
        result['enrolment_packs'] += int(section.get('enrolment_packs', 0))
        result['quotes'] += int(section.get('quotes', 0))
        result['cpd_booked'] += int(section.get('cpd_booked', 0))
        result['grand_total_2'] += int(section.get('grand_total_2', 0))
    
    return result
```

---

### **PHASE 5: Styling and Polish**
**File**: `styles.qss`

#### Tasks:

1. **Add styles for new components**:
```css
/* Section headers */
QGroupBox {
    font-weight: bold;
    font-size: 11pt;
    margin-top: 10px;
}

/* Total fields */
QSpinBox[isTotal="true"] {
    font-weight: bold;
    background-color: #f0f0f0;
}

/* Overridden totals */
QSpinBox[isOverridden="true"] {
    background-color: #FFFACD;
}

/* Grand totals */
QSpinBox[isGrandTotal="true"] {
    font-weight: bold;
    font-size: 12pt;
    background-color: #e8f4f8;
}
```

2. **Update existing styles** for new layout

3. **Ensure consistent spacing** between sections

---

### **PHASE 6: Testing Strategy**

#### Unit Tests:
1. **Data Manager**:
   - Test save/load with new schema
   - Test missing field handling
   - Test data validation

2. **Calculation Logic**:
   - Test section total calculations
   - Test grand total calculations
   - Test manual override behavior

3. **UI Logic**:
   - Test widget population from data
   - Test data extraction from widgets
   - Test signal connections

#### Manual Testing Checklist:
- [ ] Create new entry with all fields populated
- [ ] Save and reload entry - verify all fields persist
- [ ] Test section total auto-calculation
- [ ] Test manual override of section total
- [ ] Test grand total calculations
- [ ] Test both tabs independently
- [ ] Test switching between dates
- [ ] Test switching between users
- [ ] Test report generation with new format
- [ ] Test email report functionality
- [ ] Test notes section in reports
- [ ] Test window resizing behavior
- [ ] Test window position & size persistence:
  - [ ] Enable "Remember window position" setting
  - [ ] Resize and move window
  - [ ] Close and reopen app - verify position and size restored
  - [ ] Disable "Remember window position" setting
  - [ ] Close and reopen app - verify default size and position used
  - [ ] Test across multiple monitors if available
  - [ ] Verify setting accessible from Settings UI
  - [ ] Verify setting accessible from app_settings.json file
- [ ] Test autosave functionality
- [ ] Test with empty/missing data

---

## 🚀 Implementation Order

### Step 1: Data Layer (1-2 hours)
1. Update `data_manager.py` with new schema
2. Create helper methods
3. Test save/load independently

### Step 2: UI Structure (3-4 hours)
1. Create new widget layout for one tab
2. Implement widget tracking dictionaries
3. Copy structure to second tab
4. Update window sizing and resizability
5. Implement window size & position persistence (update settings manager)
6. Test window geometry save/restore

### Step 3: Calculation Logic (2-3 hours)
1. Implement section total calculations
2. Implement grand total calculations
3. Add manual override support
4. Add visual indicators

### Step 4: Integration (1-2 hours)
1. Connect calculations to autosave
2. Implement load/save with new widgets
3. Test full cycle (load → edit → save → load)

### Step 5: Reports (1-2 hours)
1. Update report generation
2. Update aggregation logic
3. Test report output

### Step 6: Polish & Testing (1-2 hours)
1. Apply styling
2. Manual testing
3. Bug fixes
4. Performance optimization

---

## 📋 Checklist Before Starting

- [x] Branch created: `feature/data-schema-change`
- [x] Previous branch merged to main
- [x] Implementation plan documented
- [ ] Backup current data files
- [ ] Review plan with stakeholders
- [ ] Begin Phase 1 implementation

---

## 🎯 Success Criteria

✅ All new metrics are capturable
✅ Totals calculate automatically
✅ Users can override any total
✅ Visual indicators show overridden values
✅ Window is resizable
✅ Window size and position persist when setting enabled
✅ Default size and position used when setting disabled
✅ Setting accessible from both UI and JSON file
✅ Reports display new structure correctly
✅ Autosave works with new schema
✅ Notes feature still works
✅ No data loss during use
✅ UI is intuitive and clean

---

## 📝 Notes

- **Fresh Start**: No migration from old data needed
- **Override Detection**: Track which totals are manually set vs auto-calculated
- **Performance**: Recalculation on every change - should be fast with simple arithmetic
- **Window Persistence**: Save/restore both position AND size when setting enabled
- **Settings Access**: Window geometry setting available via UI (Settings dialog) and JSON file (data/app_settings.json)
- **Default Behavior**: When "remember position" is disabled, use default size (350x900) and center on primary screen
- **Future Enhancement**: Consider "reset all overrides" button
- **Validation**: Ensure totals make logical sense (warning if manual total < sum of components)

---

**Plan Created**: October 23, 2025
**Target Branch**: `feature/data-schema-change`
**Estimated Total Time**: 9-15 hours
**Status**: Ready for Implementation
