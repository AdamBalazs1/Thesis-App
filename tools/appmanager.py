import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SETTINGS_PATH = BASE_DIR / "settings"


class AppManager:
    def __init__(self, user_name='default_user'):
        self.user_name = user_name
        self.default_settings_path = DEFAULT_SETTINGS_PATH / "default_settings.json"   # ToDo fix this for future! - login implementation
        self.user_settings_path = DEFAULT_SETTINGS_PATH / f"{self.user_name}_settings.json"

        self.settings = self.load_settings()


    def load_settings(self):
        if os.path.exists(self.user_settings_path):
            with open(self.user_settings_path, "r") as f:
                return json.load(f)
        else:
            return self.load_default_settings()

    def load_default_settings(self):
        try:
            with open(self.default_settings_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Default settings file '{self.default_settings_path}' is missing.")
        except json.JSONDecodeError:
            raise ValueError(f"Default settings file '{self.default_settings_path}' is not a valid JSON file.")

    def save_settings(self):
        with open(self.user_settings_path, "w") as f:
            json.dump(self.settings, f, indent=4)

    def set_setting(self, key, value):
        self.settings[key] = value
        self.save_settings()


if __name__ == '__main__':
    app_manager = AppManager(user_name="Adam")


    print('name: ' + app_manager.user_name)
