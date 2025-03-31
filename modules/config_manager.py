import json
import os

class ConfigManager:
    def __init__(self, config_path):
        self.config_path = config_path
        self.settings = {}
        self.load_settings()
    
    def load_settings(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    self.settings = json.load(f)
            except:
                self.settings = {}
        else:
            self.settings = {}
    
    def save_settings(self):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.settings, f, indent=4)
    
    def update_setting(self, key, value):
        self.settings[key] = value
        self.save_settings()
    
    def update_settings(self, settings_dict):
        self.settings.update(settings_dict)
        self.save_settings()