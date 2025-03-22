import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import threading
import os
import webbrowser
from utils import convertname, current_dir
from dependency import check_dependencies_before_main
from processing_gui import (
    process_full_video_gui,
    process_cut_video_gui,
    process_full_audio_gui,
    process_cut_audio_gui,
)


# --- GUI Application Class ---
class GUIApp:
    def __init__(self, master):
        self.master = master
        master.title("YouTube Cutter GUI")
        master.geometry("490x900")  # New initial window size

        # Variables for user input
        self.media_type = tk.StringVar(value="Video")
        self.mode = tk.StringVar(value="Full")
        self.url = tk.StringVar()
        self.output_name = tk.StringVar()
        self.start_time = tk.StringVar()
        self.end_time = tk.StringVar()
        self.out_dir = tk.StringVar(value=current_dir)

        # Dependency check on startup (hide main window until done)
        self.check_dependencies_on_startup()

        # Media Type Frame
        frame_media = ttk.LabelFrame(master, text="Media Type")
        frame_media.pack(fill="x", padx=10, pady=5)
        ttk.Radiobutton(
            frame_media,
            text="Video",
            variable=self.media_type,
            value="Video",
            command=self.update_mode_options,
        ).pack(side="left", padx=10, pady=5)
        ttk.Radiobutton(
            frame_media,
            text="Audio",
            variable=self.media_type,
            value="Audio",
            command=self.update_mode_options,
        ).pack(side="left", padx=10, pady=5)

        # Mode Frame
        frame_mode = ttk.LabelFrame(master, text="Mode")
        frame_mode.pack(fill="x", padx=10, pady=5)
        ttk.Radiobutton(
            frame_mode,
            text="Full",
            variable=self.mode,
            value="Full",
            command=self.update_cut_fields,
        ).pack(side="left", padx=10, pady=5)
        ttk.Radiobutton(
            frame_mode,
            text="Cut",
            variable=self.mode,
            value="Cut",
            command=self.update_cut_fields,
        ).pack(side="left", padx=10, pady=5)

        # URL Entry
        frame_url = ttk.Frame(master)
        frame_url.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame_url, text="Video/Audio URL:").pack(side="left")
        self.entry_url = ttk.Entry(frame_url, textvariable=self.url, width=50)
        self.entry_url.pack(side="left", padx=5)

        # Output Name Entry
        frame_output = ttk.Frame(master)
        frame_output.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame_output, text="Output Name:").pack(side="left")
        self.entry_output = ttk.Entry(
            frame_output, textvariable=self.output_name, width=30
        )
        self.entry_output.pack(side="left", padx=5)

        # Output Directory selection
        frame_dir = ttk.Frame(master)
        frame_dir.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame_dir, text="Output Directory:").pack(side="left")
        self.label_dir = ttk.Label(
            frame_dir, text=self.out_dir.get(), relief="sunken", width=40
        )
        self.label_dir.pack(side="left", padx=5)
        ttk.Button(frame_dir, text="Browse", command=self.browse_directory).pack(
            side="left", padx=5
        )

        # Cut fields and Visualize Cutting button in one row
        self.frame_cut = ttk.Frame(master)
        self.frame_cut.pack(fill="x", padx=10, pady=5)
        ttk.Label(self.frame_cut, text="Start Time:").pack(side="left")
        self.entry_start = ttk.Entry(
            self.frame_cut, textvariable=self.start_time, width=15
        )
        self.entry_start.pack(side="left", padx=5)
        ttk.Label(self.frame_cut, text="End Time:").pack(side="left")
        self.entry_end = ttk.Entry(self.frame_cut, textvariable=self.end_time, width=15)
        self.entry_end.pack(side="left", padx=5)
        # Visualize Cutting button next to end time box
        self.visualize_btn = ttk.Button(
            self.frame_cut, text="Visualize Cutting", command=self.visualize_cutting
        )
        self.visualize_btn.pack(side="left", padx=5)
        self.update_cut_fields()

        # Bigger Run Button with larger text
        self.button_run = ttk.Button(
            master, text="Run", command=self.start_process_thread
        )
        self.button_run.config(style="Big.TButton")
        self.button_run.pack(pady=15, ipadx=20, ipady=10)
        # Set style for bigger Run button
        style = ttk.Style()
        style.configure("Big.TButton", font=("Helvetica", 14))

        # Log Text widget for output messages (status box), adaptive to resizing
        self.log_text = scrolledtext.ScrolledText(master, state="disabled")
        self.log_text.pack(fill="both", expand=True, padx=10, pady=5)

        # Centered Button group for Open Output Directory / Open Output File
        frame_buttons = ttk.Frame(master)
        frame_buttons.pack(pady=10)
        self.open_dir_btn = ttk.Button(
            frame_buttons, text="Open Output Directory", command=self.open_directory
        )
        self.open_dir_btn.pack(side="left", padx=10)
        self.open_dir_btn.config(style="Big.TButton")
        self.open_file_btn = ttk.Button(
            frame_buttons, text="Open Output File", command=self.open_output_file
        )
        self.open_file_btn.pack(side="left", padx=10)
        self.open_file_btn.config(style="Big.TButton")
        self.open_file_btn.config(state="disabled")  # Disabled until process complete

        # Bottom status bar
        self.status_label = tk.Label(
            master, text="Ready", bd=1, relief=tk.SUNKEN, anchor="w"
        )
        self.status_label.pack(side="bottom", fill="x")

        # Overall progress bar (under status bar)
        self.overall_progress = ttk.Progressbar(master, mode="determinate", maximum=100)
        self.overall_progress.pack(side="bottom", fill="x", padx=10, pady=2)

    def check_dependencies_on_startup(self):
        self.master.withdraw()
        if check_dependencies_before_main(self.master):
            self.master.deiconify()
        else:
            messagebox.showerror("Fatal Error", "Dependency check failed. Exiting.")
            self.master.quit()

    def browse_directory(self):
        path = filedialog.askdirectory(title="Select Output Directory")
        if path:
            self.out_dir.set(path + "/")
            self.label_dir.config(text=self.out_dir.get())

    def visualize_cutting(self):
        webbrowser.open("https://ytcutter.com/")

    def update_cut_fields(self):
        if self.mode.get() == "Cut":
            self.entry_start.config(state="normal")
            self.entry_end.config(state="normal")
            self.visualize_btn.config(state="normal")
        else:
            self.entry_start.config(state="disabled")
            self.entry_end.config(state="disabled")
            self.visualize_btn.config(state="disabled")

    def update_mode_options(self):
        self.mode.set("Full")
        self.update_cut_fields()

    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def set_status(self, message):
        self.status_label.config(text=message)

    def open_directory(self):
        dir_path = self.out_dir.get()
        if os.path.isdir(dir_path):
            os.startfile(dir_path)
        else:
            messagebox.showerror("Error", "Output directory not found.")

    def open_output_file(self):
        name = convertname(self.output_name.get() or "output")
        ext = ".mp4" if self.media_type.get() == "Video" else ".mp3"
        file_path = os.path.join(self.out_dir.get(), name + ext)
        if os.path.exists(file_path):
            os.startfile(file_path)
        else:
            messagebox.showerror("Error", "Output file not found.")

    def start_process_thread(self):
        self.button_run.config(state="disabled")
        self.open_file_btn.config(state="disabled")
        thread = threading.Thread(target=self.run_process)
        thread.start()

    def run_process(self):
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")
        self.set_status("Starting process...")
        self.overall_progress["value"] = 0

        media = self.media_type.get()
        mode = self.mode.get()
        url = self.url.get().strip()
        output_name = self.output_name.get().strip() or "output"
        out_dir = self.out_dir.get()

        if media == "Video":
            if mode == "Full":
                process_full_video_gui(
                    url,
                    output_name,
                    out_dir,
                    self.log,
                    self.set_status,
                    self.overall_progress,
                )
            elif mode == "Cut":
                start = self.start_time.get().strip()
                end = self.end_time.get().strip()
                process_cut_video_gui(
                    url,
                    output_name,
                    out_dir,
                    start,
                    end,
                    self.log,
                    self.set_status,
                    self.overall_progress,
                )
        elif media == "Audio":
            if mode == "Full":
                process_full_audio_gui(
                    url,
                    output_name,
                    out_dir,
                    self.log,
                    self.set_status,
                    self.overall_progress,
                )
            elif mode == "Cut":
                start = self.start_time.get().strip()
                end = self.end_time.get().strip()
                process_cut_audio_gui(
                    url,
                    output_name,
                    out_dir,
                    start,
                    end,
                    self.log,
                    self.set_status,
                    self.overall_progress,
                )
        self.log("Process completed.")
        self.set_status("Ready")
        self.overall_progress["value"] = 100
        self.button_run.config(state="normal")
        self.open_file_btn.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = GUIApp(root)
    root.mainloop()
