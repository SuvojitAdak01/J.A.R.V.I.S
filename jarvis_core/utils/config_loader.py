import json
import os

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config')
API_KEYS_FILE = os.path.join(CONFIG_DIR, 'api_keys.json')
SETTINGS_FILE = os.path.join(CONFIG_DIR, 'settings.json')

def load_api_keys():
    try:
        with open(API_KEYS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: API keys file not found at {API_KEYS_FILE}. Some features may not work.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {API_KEYS_FILE}.")
        return {}

def load_settings():
    try:
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {SETTINGS_FILE}.")
        return {}

if __name__ == '__main__':
    keys = load_api_keys()
    print("Loaded API Keys:", keys)
    settings = load_settings()
    print("Setings loaded:", settings)
    if 'openweathermap' in keys:
        print("OpenWeatherMap Key:", keys['openweathermap'])