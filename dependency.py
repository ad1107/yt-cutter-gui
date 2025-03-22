import os
import zipfile
import tkinter as tk
from tkinter import ttk, messagebox
import time
import urllib.request
from utils import current_dir


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
    popup = tk.Toplevel(parent)
    popup.title(f"Downloading {dep_name}")
    popup.geometry("400x150")

    tk.Label(popup, text=f"Downloading {dep_name}...").pack(pady=5)

    progress_bar = ttk.Progressbar(
        popup, orient="horizontal", length=300, mode="determinate"
    )
    progress_bar.pack(pady=10)

    status_label = tk.Label(popup, text="Starting download...")
    status_label.pack(pady=5)

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
        status_label.config(
            text=f"{pct:.0f}% | {downloaded_mb:.2f} MB / {total_mb:.2f} MB | {speed_str} | ETA: {eta:.0f}s"
        )
        progress_bar["value"] = pct
        popup.update_idletasks()

    try:
        urllib.request.urlretrieve(url, local_path, reporthook)
    except Exception as e:
        messagebox.showerror("Download Error", f"Error downloading {dep_name}:\n{e}")
        popup.destroy()
        return None

    popup.destroy()
    return local_path

def extract_ffmpeg_gui(zip_path, output_filename, parent):
    popup = tk.Toplevel(parent)
    popup.title("Extracting ffmpeg")
    popup.geometry("400x100")
    tk.Label(popup, text="Extracting ffmpeg...").pack(pady=10)
    progress_bar = ttk.Progressbar(popup, mode="indeterminate")
    progress_bar.pack(fill="x", padx=20, pady=5)
    progress_bar.start(10)
    parent.update_idletasks()
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            for file_info in zip_ref.infolist():
                if output_filename in file_info.filename:
                    extracted_path = os.path.join(current_dir, output_filename)
                    with open(extracted_path, "wb") as f:
                        f.write(zip_ref.read(file_info.filename))
                    break
    except Exception as e:
        messagebox.showerror("Extraction Error", f"Error extracting ffmpeg:\n{e}")
        popup.destroy()
        return False
    progress_bar.stop()
    tk.Label(popup, text="Extraction complete!").pack(pady=5)
    parent.update_idletasks()
    time.sleep(0.5)
    popup.destroy()
    return True


def check_dependencies_before_main(parent):
    """
    Checks for required dependencies (yt-dlp.exe and ffmpeg.exe) before showing the main window.
    If missing, downloads/extracts them while displaying progress.
    Aborts (quits) if a dependency fails or is canceled.
    """
    if not os.path.isfile("yt-dlp.exe"):
        downloaded = download_dependency_gui(
            "yt-dlp.exe",
            "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe",
            parent,
        )
        if not downloaded:
            messagebox.showerror("Dependency Error", "Failed to download yt-dlp.exe")
            parent.quit()
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
                parent.quit()
                return False
        extracted = extract_ffmpeg_gui("ffmpeg.zip", "ffmpeg.exe", parent)
        if not extracted:
            messagebox.showerror("Dependency Error", "Failed to extract ffmpeg.exe")
            parent.quit()
            return False
        else:
            os.remove("ffmpeg.zip")
    return True
