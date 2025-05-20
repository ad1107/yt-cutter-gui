import os
import zipfile
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import time
import urllib.request
from utils import current_dir

# Configure customtkinter appearance
ctk.set_appearance_mode("system")  # Use system theme (or "dark"/"light")
ctk.set_default_color_theme("blue")  # Set theme color


def download_dependency_gui(dep_name, url, parent):
    """
    Downloads a dependency (e.g. yt-dlp.exe or ffmpeg.zip) using urlretrieve.
    Uses a custom reporthook to update a Toplevel popup with a progress bar and status text:
      - Percentage complete
      - Downloaded size (in MB) out of total size
      - Average speed (in KB/s or MB/s)
      - Estimated time remaining (ETA)
    Returns the local file path if successful; otherwise, returns None.
    """
    try:
        popup = ctk.CTkToplevel(parent)
        popup.title(f"Downloading {dep_name}")
        popup.geometry("500x200")
        popup.transient(parent)
        
        # Make sure the popup is shown regardless of the parent's state
        popup.grab_set()
        popup.focus_force()
        
        # Ensure the window appears
        popup.update()
        
        ctk.CTkLabel(popup, text=f"Downloading {dep_name}...", font=("", 14)).pack(pady=10)

        progress_bar = ctk.CTkProgressBar(
            popup, width=300, mode="determinate"
        )
        progress_bar.set(0)  # Set initial value to 0
        progress_bar.pack(pady=15)

        status_label = ctk.CTkLabel(popup, text="Starting download...", font=("", 12))
        status_label.pack(pady=10)

        local_path = os.path.join(current_dir, dep_name)
        start_time = [None]  # mutable container for start time

        def reporthook(blocknum, blocksize, totalsize):
            if blocknum == 0:
                start_time[0] = time.time()
                return
            elapsed = time.time() - start_time[0]
            current = blocknum * blocksize
            pct = min(current * 100.0 / totalsize, 100)
            avg_speed = (current / elapsed) if elapsed > 0 else 0  # in bytes/s
            eta = (totalsize - current) / avg_speed if avg_speed else 0
            downloaded_mb = current / (1024 * 1024)
            total_mb = totalsize / (1024 * 1024)
            if avg_speed >= 1024 * 1024:
                speed_str = f"{avg_speed/(1024*1024):.1f} MB/s"
            else:
                speed_str = f"{avg_speed/1024:.1f} KB/s"
            status_label.configure(
                text=f"{pct:.0f}% | {downloaded_mb:.2f} MB / {total_mb:.2f} MB | {speed_str} | ETA: {eta:.0f}s"
            )
            progress_bar.set(pct/100)  # CTkProgressBar takes values between 0 and 1
            popup.update_idletasks()
            popup.update()  # Make sure the window updates

        try:
            urllib.request.urlretrieve(url, local_path, reporthook)
            # Wait a moment to show completion
            time.sleep(0.5)
            popup.destroy()
            return local_path
        except Exception as e:
            messagebox.showerror("Download Error", f"Error downloading {dep_name}:\n{e}")
            popup.destroy()
            return None
    except Exception as e:
        messagebox.showerror("Download Dialog Error", f"Error creating download dialog:\n{e}")
        return None

def extract_ffmpeg_gui(zip_path, output_filename, parent):
    try:
        popup = ctk.CTkToplevel(parent)
        popup.title("Extracting ffmpeg")
        popup.geometry("500x150")
        popup.transient(parent)
        
        # Make sure the popup is shown
        popup.grab_set()
        popup.focus_force()
        popup.update()
        
        ctk.CTkLabel(popup, text="Extracting ffmpeg...", font=("", 14)).pack(pady=15)
        progress_bar = ctk.CTkProgressBar(popup, width=400)
        progress_bar.pack(fill="x", padx=30, pady=10)
        progress_bar.configure(mode="indeterminate")
        progress_bar.start()
        popup.update()
        parent.update()
        
        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                for file_info in zip_ref.infolist():
                    if output_filename in file_info.filename:
                        extracted_path = os.path.join(current_dir, output_filename)
                        with open(extracted_path, "wb") as f:
                            f.write(zip_ref.read(file_info.filename))
                        break
            
            progress_bar.stop()
            ctk.CTkLabel(popup, text="Extraction complete!", font=("", 14)).pack(pady=10)
            popup.update()
            time.sleep(1)
            popup.destroy()
            return True
        except Exception as e:
            messagebox.showerror("Extraction Error", f"Error extracting ffmpeg:\n{e}")
            popup.destroy()
            return False
    except Exception as e:
        messagebox.showerror("Extraction Dialog Error", f"Error creating extraction dialog:\n{e}")
        return False


def check_dependencies_before_main(parent):
    """
    Checks for required dependencies (yt-dlp.exe and ffmpeg.exe) before showing the main window.
    """
    try:
        if not os.path.isfile("yt-dlp.exe"):
            downloaded = download_dependency_gui(
                "yt-dlp.exe",
                "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe",
                parent,
            )
            if not downloaded:
                messagebox.showerror("Dependency Error", "Failed to download yt-dlp.exe")
                return False
        
        if not os.path.isfile("ffmpeg.exe"):
            if not os.path.exists("ffmpeg.zip"):
                downloaded = download_dependency_gui(
                    "ffmpeg.zip",
                    "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip",
                    parent,
                )
                if not downloaded:
                    messagebox.showerror(
                        "Dependency Error", "Failed to download ffmpeg.zip"
                    )
                    return False
            
            extracted = extract_ffmpeg_gui("ffmpeg.zip", "ffmpeg.exe", parent)
            if not extracted:
                messagebox.showerror("Dependency Error", "Failed to extract ffmpeg.exe")
                return False
            else:
                try:
                    os.remove("ffmpeg.zip")
                except:
                    pass
        
        return True
    except Exception as e:
        messagebox.showerror("Dependency Check Error", f"Error checking dependencies:\n{e}")
        return False
