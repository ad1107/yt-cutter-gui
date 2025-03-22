import os
import tkinter as tk
from tkinter import filedialog

# Global variable for the current working directory
current_dir = os.path.abspath('.') + os.sep

def converttime(time_str):
    """
    Converts a time string into total seconds as a float.
    Supported formats:
      - SS[.ms]
      - MM:SS[.ms]
      - HH:MM:SS[.ms]
    """
    time_str = time_str.strip().replace(",", ".")
    parts = time_str.split(':')
    # Ensure the seconds part has a decimal component.
    sec_part = parts[-1]
    if '.' not in sec_part:
        sec_part += ".0"
    sec, frac = sec_part.split('.')
    
    if len(parts) == 3:
        hours = int(parts[0])
        minutes = int(parts[1])
    elif len(parts) == 2:
        hours = 0
        minutes = int(parts[0])
    else:  # Only seconds provided
        hours = 0
        minutes = 0
    seconds = int(sec)
    total = hours * 3600 + minutes * 60 + seconds + float("0." + frac)
    return total


def select_path(title):
    """
    Opens a Tkinter dialog to allow the user to choose a directory.
    """
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askdirectory(title=title)
    if path:
        return path + os.sep
    else:
        return current_dir

def convertname(name):
    """
    Returns a sanitized output name. If the provided name is empty, returns "output".
    """
    return name if name.strip() else "output"

def check_ext(ext):
    """
    Checks if any file in the current directory ends with the given extension.
    """
    for filename in os.listdir(current_dir):
        if filename.endswith(ext):
            return True
    return False
