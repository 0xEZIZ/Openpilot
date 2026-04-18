"""
ADU OpenPilot — Universal CAN Dashboard
Windows | IXXAT USB-to-CAN | Standalone Startup
"""
import sys
import os
import time
import threading

# --- Fix stdout/stderr for frozen GUI mode (console=False) ---
# When PyInstaller builds with console=False, sys.stdout/stderr are None.
# Any print() call would crash with AttributeError.
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w', encoding='utf-8')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w', encoding='utf-8')

import tkinter as tk
from PIL import Image, ImageTk
import winsound

# PyInstaller path handler
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def get_app_dir():
    """Get persistent app directory (next to EXE, or script dir in dev)"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


# Resource paths
LOGO_PATH = resource_path("logo (2).jpg")
SOUND_PATH = resource_path("ENGINE BMW.wav")

def play_engine_sound():
    try:
        if os.path.exists(SOUND_PATH):
            winsound.PlaySound(SOUND_PATH, winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception as e:
        print(f"Sound error: {e}")

def show_splash():
    splash = tk.Tk()
    splash.title("ADU OpenPilot")

    # Borderless window
    splash.overrideredirect(True)

    # Always on top — splash is visible even with many windows open
    splash.attributes('-topmost', True)
    splash.lift()
    splash.focus_force()
    
    # Background and image
    try:
        img = Image.open(LOGO_PATH)
        # Resize to a reasonable splash size (e.g., 500x500)
        img = img.resize((500, 500), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        
        # Calculate centering
        img_width, img_height = 500, 500
        screen_width = splash.winfo_screenwidth()
        screen_height = splash.winfo_screenheight()
        
        x = (screen_width // 2) - (img_width // 2)
        y = (screen_height // 2) - (img_height // 2)
        
        splash.geometry(f"{img_width}x{img_height}+{x}+{y}")
        
        label = tk.Label(splash, image=photo, bg="black")
        label.pack()
        
        # Play sound in background
        threading.Thread(target=play_engine_sound, daemon=True).start()
        
        # Close after 3 seconds and start main app
        splash.after(3000, splash.destroy)
        splash.mainloop()
    except Exception as e:
        print(f"Splash error: {e}")
        splash.destroy()

# --- Main App Start ---

# Set working directory to app location (NOT _MEIPASS temp dir)
os.chdir(get_app_dir())

if '--demo' in sys.argv:
    import config
    config.DEMO_MODE = True

if __name__ == '__main__':
    # 1. Show Splash + Sound
    show_splash()
    
    # 2. Start Main App
    from gui import App
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
