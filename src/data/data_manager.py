import json
import os
from datetime import datetime

class DataManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self._ensure_data_file()
    
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
        
        # Check if there's an existing entry for the same date and user
        found = False
        for existing_entry in data["entries"]:
            if (existing_entry["user"] == entry["user"] and 
                existing_entry["date"] == entry["date"]):
                # Overwrite all counters instead of adding to them
                for key, value in entry.items():
                    if key not in ["user", "date", "comments"]:
                        existing_entry[key] = value
                # Overwrite comments entirely
                existing_entry["comments"] = entry["comments"]
                found = True
                break
        
        if not found:
            data["entries"].append(entry)
        
        self._save_data(data)
    
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
        """Return the entry for the specified user and date, or None if not found."""
        data = self._load_data()
        for entry in data.get("entries", []):
            if entry.get("user") == user and entry.get("date") == date_str:
                return entry
        return None