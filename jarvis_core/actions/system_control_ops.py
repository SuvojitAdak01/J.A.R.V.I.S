import platform
import subprocess

OS_NAME = platform.system().lower()

if OS_NAME == "windows":
    try:
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        VOLUME_CONTROL = interface.QueryInterface(IAudioEndpointVolume)
    except (ImportError, OSError) as e:
        print(f"Warning: pycaw library not found or failed to initialize: {e}. Windows volume control will not work.")
        VOLUME_CONTROL = None

else:
    VOLUME_CONTROL = None

def set_volume(level):
    if not (0 <= level <= 100):
        return "Please specify a volume level between 0 and 100."

    try:
        if OS_NAME == "windows":
            if not VOLUME_CONTROL: return "Windows volume control is not available."

            VOLUME_CONTROL.SetMasterVolumeLevelScalar(level / 100.0, None)
        elif OS_NAME == "darwin":  # macOS
            subprocess.run(["osascript", "-e", f"set volume output volume {level}"])
        elif OS_NAME == "linux":
            subprocess.run(["amixer", "-D", "pulse", "sset", "Master", f"{level}%"])

        return f"Volume set to {level}%."
    except Exception as e:
        print(f"Error setting volume: {e}")
        return "Sorry, I encountered an error trying to set the volume."

def increase_volume(step=10):
    try:
        if OS_NAME == "windows":
            if not VOLUME_CONTROL: return "Windows volume control is not available."
            current_level_scalar = VOLUME_CONTROL.GetMasterVolumeLevelScalar()
            new_level_scalar = min(1.0, current_level_scalar + (step / 100.0))
            VOLUME_CONTROL.SetMasterVolumeLevelScalar(new_level_scalar, None)
            return f"Increasing volume. New level is around {int(new_level_scalar * 100)}%."
        elif OS_NAME == "darwin":
            subprocess.run(["osascript", "-e", "set volume output volume (output volume of (current date)) + 10"])
            return "Increasing Volume"
        elif OS_NAME == "linux":
            subprocess.run(["amixer", "-D", "pulse", "sset", "Master", f"{step}%+"])
            return "Increasing volume."
    except Exception as e:
        print(f"Error increasing volume: {e}")
        return "Sorry, I couldn't increase the volume."

def decrease_volume(step=10):
    try:
        if OS_NAME == "windows":
            if not VOLUME_CONTROL: return "Windows volume control is not available."
            current_level_scalar = VOLUME_CONTROL.GetMasterVolumeLevelScalar()
            new_level_scalar = max(0.0, current_level_scalar - (step / 100.0))
            VOLUME_CONTROL.SetMasterVolumeLevelScalar(new_level_scalar, None)
            return f"Decreasing volume. New level is around {int(new_level_scalar * 100)}%."
        elif OS_NAME == "darwin":
            subprocess.run(["osascript", "-e", "set volume output volume (output volume of (current date)) - 10"])
            return "Decreasing volume."
        elif OS_NAME == "linux":
            subprocess.run(["amixer", "-D", "pulse", "sset", "Master", f"{step}%-"])
            return "Decreasing volume."
    except Exception as e:
        print(f"Error decreasing volume: {e}")
        return "Sorry, I couldn't decrease the volume."

def mute_unmute_volume():
    try:
        if OS_NAME == "windows":
            if not VOLUME_CONTROL: return "Windows volume control is not available."
            is_muted = VOLUME_CONTROL.GetMute()
            VOLUME_CONTROL.SetMute(not is_muted, None)
            return "Volume muted." if not is_muted else "Volume unmuted."
        elif OS_NAME == "darwin":
            # This script toggles mute
            subprocess.run(["osascript", "-e", "set volume output muted not (output muted of (get volume settings))"])
            return "Toggling mute."
        elif OS_NAME == "linux":
            subprocess.run(["amixer", "-D", "pulse", "sset", "Master", "toggle"])
            return "Toggling mute."
    except Exception as e:
        print(f"Error toggling mute: {e}")
        return "Sorry, I couldn't toggle the mute state."
