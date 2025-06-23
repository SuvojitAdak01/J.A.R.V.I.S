import webbrowser
import subprocess
import platform
import os
import json

RUNNING_PROCESSES = {}

def load_app_paths():
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'app_paths.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Warning: config/app_paths.json not found. Application launching will be limited.")
        return {}
    except json.JSONDecodeError:
        print("Warning: Could not decode config/app_paths.json. Check for syntax errors.")
        return {}

APP_PATHS = load_app_paths()

def open_target_action(entities):
    """
    Opens a target application or website and directly tracks the process object.
    """
    target_name = entities.get('target')
    if not target_name:
        return "I'm not sure what you want me to open. Please specify an application or website."

    target_lower = target_name.lower()
    os_name = platform.system().lower()
    os_apps = APP_PATHS.get(os_name, {})

    app_key_to_open = None

    if target_lower in os_apps:
        app_key_to_open = target_lower
    else:
        for key in os_apps.keys():
            if key in target_lower:
                app_key_to_open = key
                break

    if app_key_to_open:
        if app_key_to_open in RUNNING_PROCESSES and RUNNING_PROCESSES[app_key_to_open].poll() is None:
            return f"{target_name} is already running under my supervision."

        app_path = os_apps[app_key_to_open]
        try:
            print(f"DEBUG: Match found. Key: '{app_key_to_open}', Path: '{app_path}'")
            proc = subprocess.Popen(app_path)
            RUNNING_PROCESSES[app_key_to_open] = proc
            return f"Opening {target_name}."
        except Exception as e:
            print(f"Error opening application '{target_name}': {e}")
            return f"Sorry, I encountered an error trying to open {target_name}."

    # --- Fallback to website/search logic (no changes here) ---
    website_indicators = ['.com', '.org', '.net', '.in', '.io', '.co', '.edu', '.gov']
    known_websites = {
        "google": "https://www.google.com", "youtube": "https://www.youtube.com",
        "wikipedia": "https://www.wikipedia.org", "github": "https://www.github.com",
        "amazon": "https://www.amazon.in"
    }
    if target_lower in known_websites:
        url = known_websites[target_lower]
    elif any(indicator in target_lower for indicator in website_indicators):
        url = target_name if target_name.startswith("http") else f"https://{target_name}"
    else:
        url = f"https://www.google.com/search?q={target_name}"
        try:
            webbrowser.open(url, new=2)
            return f"I couldn't find a configured application or website for '{target_name}', so I'm searching for it."
        except Exception as e:
            print(f"Error opening web browser: {e}")
            return "Sorry, I couldn't open the web browser to search."

    try:
        webbrowser.open(url, new=2)
        return f"Navigating to {target_name}."
    except Exception as e:
        print(f"Error opening web browser: {e}")
        return f"Sorry, I had trouble opening the web browser for {target_name}."

def close_target_action(entities):
    """
    Closes a running application that was opened by JARVIS.
    """
    target_name = entities.get('target')
    if not target_name:
        return "I'm not sure what you want me to close. Please specify an application."

    target_lower = target_name.lower()

    if target_lower not in RUNNING_PROCESSES:
        return f"It doesn't look like {target_name} is currently running under my supervision. I can only close apps that I've opened."

    proc = RUNNING_PROCESSES[target_lower]
    # Check if the process is still running before trying to kill it
    if proc.poll() is None:
        os_name = platform.system().lower()
        print(f"DEBUG: Attempting to close '{target_name}' (PID: {proc.pid}) on {os_name}.")
        try:
            if os_name == "windows":
                # /F = Forcefully terminate, /T = Terminate child processes, /PID = specify Process ID
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], check=True, capture_output=True)
            else:  # macOS and Linux
                proc.kill()

            # Wait a moment for the process to terminate
            proc.wait(timeout=5)
            print(f"DEBUG: Process for '{target_name}' terminated.")

        except subprocess.TimeoutExpired:
            print(f"Warning: Process for '{target_name}' did not terminate within the timeout.")
            return f"I sent the command to close {target_name}, but it's not responding."
        except Exception as e:
            print(f"Error closing application '{target_name}': {e}")
            return f"Sorry, I encountered an error trying to close {target_name}."
    else:
        print(f"DEBUG: Process for '{target_name}' was already closed.")

    # Clean up the entry from our dictionary
    del RUNNING_PROCESSES[target_lower]
    return f"Closing {target_name}."