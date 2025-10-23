import json
import os
from datetime import datetime

class DataManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self._ensure_data_file()
    
    def create_empty_section_structure(self):
        """Create an empty section structure with new schema"""
        return {
            "call_connects": {
                "paid_lead": 0,
                "organic_lead": 0,
                "agents": 0,
                "total": 0
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
            "grand_total": 0,
            "enrolment_packs": 0,
            "quotes": 0,
            "cpd_booked": 0,
            "grand_total_2": 0
        }
    
    def create_empty_entry_structure(self):
        """Create an empty entry structure with new schema"""
        return {
            "user": "",
            "date": "",
            "current_leads": self.create_empty_section_structure(),
            "prospects": self.create_empty_section_structure(),
            "comments": ""
        }
    
    def _ensure_data_file(self):
        """Create the data file with default structure if it doesn't exist"""
        if not os.path.exists(self.file_path):
            default_data = {
                "users": [],
                "entries": []
            }
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, 'w') as f:
                json.dump(default_data, f, indent=2)
    
    def _load_data(self):
        """Load data from the JSON file"""
        with open(self.file_path, 'r') as f:
            return json.load(f)
    
    def _save_data(self, data):
        try:
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=2)
            # print("Data saved successfully to", self.file_path)
        except Exception as e:
            print("Error saving data:", e)
    
    def get_users(self):
        """Get the list of users"""
        data = self._load_data()
        return data.get("users", [])
    
    def add_user(self, name):
        """Add a new user if they don't already exist"""
        data = self._load_data()
        if name not in data["users"]:
            data["users"].append(name)
            self._save_data(data)
    
    def save_entry(self, entry):
        """Save a new entry, overwriting existing stats if an entry exists for the same date and user"""
        data = self._load_data()
        
        # Validate and ensure entry has proper structure
        validated_entry = self._validate_entry(entry)
        
        found = False
        for existing_entry in data["entries"]:
            if (existing_entry["user"] == validated_entry["user"] and 
                existing_entry["date"] == validated_entry["date"]):
                # Overwrite with validated entry
                existing_entry["current_leads"] = validated_entry["current_leads"]
                existing_entry["prospects"] = validated_entry["prospects"]
                existing_entry["comments"] = validated_entry["comments"]
                found = True
                break
        
        if not found:
            data["entries"].append(validated_entry)
        
        self._save_data(data)
    
    def _validate_entry(self, entry):
        """Validate and normalize entry structure"""
        validated = self.create_empty_entry_structure()
        validated["user"] = entry.get("user", "")
        validated["date"] = entry.get("date", "")
        validated["comments"] = entry.get("comments", "")
        
        # Validate and merge current_leads
        if "current_leads" in entry:
            validated["current_leads"] = self._validate_section(entry["current_leads"])
        
        # Validate and merge prospects
        if "prospects" in entry:
            validated["prospects"] = self._validate_section(entry["prospects"])
        
        return validated
    
    def _validate_section(self, section_data):
        """Validate and normalize section data"""
        validated = self.create_empty_section_structure()
        
        # Validate call sections
        for call_section in ["call_connects", "call_nonconnects", "call_inbetweens"]:
            if call_section in section_data:
                for field in ["paid_lead", "organic_lead", "agents", "total"]:
                    value = section_data[call_section].get(field, 0)
                    validated[call_section][field] = self._to_int(value)
        
        # Validate other section
        if "other" in section_data:
            for field in ["sms", "email", "total"]:
                value = section_data["other"].get(field, 0)
                validated["other"][field] = self._to_int(value)
        
        # Validate standalone fields
        for field in ["grand_total", "enrolment_packs", "quotes", "cpd_booked", "grand_total_2"]:
            value = section_data.get(field, 0)
            validated[field] = self._to_int(value)
        
        return validated
    
    def _to_int(self, value):
        """Safely convert value to integer"""
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0
    
    def get_data_for_date_range(self, start_date, end_date):
        """Get all entries within a date range"""
        data = self._load_data()
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        filtered_entries = []
        for entry in data["entries"]:
            # Skip entries whose date is not a string
            if not isinstance(entry.get("date"), str):
                continue
            entry_date = datetime.strptime(entry["date"], "%Y-%m-%d")
            if start <= entry_date <= end:
                filtered_entries.append(entry)
        
        return filtered_entries

    def get_entry_for_user_and_date(self, user, date_str):
        """Return the entry for the specified user and date, or None if not found.
        Returns a validated entry with proper structure, filling in missing fields with defaults."""
        data = self._load_data()
        for entry in data.get("entries", []):
            if entry.get("user") == user and entry.get("date") == date_str:
                # Validate and return entry with proper structure
                return self._validate_entry(entry)
        return None