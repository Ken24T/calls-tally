import json
import os

class SettingsManager:
    def __init__(self, settings_file='data/app_settings.json'):
        self.settings_file = settings_file
        self.default_settings = {
            'remember_window_position': False,
            'window_position': {'x': 100, 'y': 100, 'width': 320, 'height': 1024, 'screen_name': ''},
            'default_emails': ''  # Only default_emails is needed now
        }
        self.settings = self.load_settings()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                settings = self.default_settings.copy()
                # Only update keys that are in default_settings to avoid keeping old ones
                for key in self.default_settings.keys():
                    if key in loaded_settings:
                        settings[key] = loaded_settings[key]
                return settings
            except Exception:
                return self.default_settings.copy()
        return self.default_settings.copy()

    def save_settings(self):
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        # Ensure only settings defined in default_settings are saved
        settings_to_save = {}
        for key in self.default_settings.keys():
            if key in self.settings:
                settings_to_save[key] = self.settings[key]
            else:
                settings_to_save[key] = self.default_settings[key] # ensure default value if not set

        with open(self.settings_file, 'w') as f:
            json.dump(settings_to_save, f, indent=2)

    def get(self, key, default=None):
        # If default is not provided, use the one from default_settings
        effective_default = default if default is not None else self.default_settings.get(key)
        return self.settings.get(key, effective_default)

    def set(self, key, value):
        if key in self.default_settings: # Only allow setting keys that are defined in defaults
            self.settings[key] = value
            self.save_settings()
        else:
            # Optionally, log a warning or raise an error for unknown settings keys
            print(f"Warning: Attempted to set an unknown setting '{key}'.")