import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
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

# Configure customtkinter appearance
ctk.set_appearance_mode("system")  # Use system theme (or "dark"/"light")
ctk.set_default_color_theme("blue")  # Set theme color


# --- GUI Application Class ---
class GUIApp:
    def __init__(self, master):
        self.master = master
        master.title("YouTube Cutter GUI")
        master.geometry("550x950")

        # Variables for user input
        self.media_type = ctk.StringVar(value="Video")
        self.mode = ctk.StringVar(value="Full")
        self.url = ctk.StringVar()
        self.output_name = ctk.StringVar()
        self.start_time = ctk.StringVar()
        self.end_time = ctk.StringVar()
        self.out_dir = ctk.StringVar(value=current_dir)

        # Dependency check on startup (hide main window until done)
        self.check_dependencies_on_startup()

        # Media Type Frame
        frame_media = ctk.CTkFrame(master)
        frame_media.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(frame_media, text="Media Type", font=("", 14, "bold")).pack(
            anchor="w", padx=10, pady=5
        )

        media_type_container = ctk.CTkFrame(frame_media)
        media_type_container.pack(fill="x", padx=10, pady=5)

        ctk.CTkRadioButton(
            media_type_container,
            text="Video",
            variable=self.media_type,
            value="Video",
            command=self.update_mode_options,
        ).pack(side="left", padx=20, pady=5)
        ctk.CTkRadioButton(
            media_type_container,
            text="Audio",
            variable=self.media_type,
            value="Audio",
            command=self.update_mode_options,
        ).pack(side="left", padx=20, pady=5)

        # Mode Frame
        frame_mode = ctk.CTkFrame(master)
        frame_mode.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(frame_mode, text="Mode", font=("", 14, "bold")).pack(
            anchor="w", padx=10, pady=5
        )

        mode_container = ctk.CTkFrame(frame_mode)
        mode_container.pack(fill="x", padx=10, pady=5)

        ctk.CTkRadioButton(
            mode_container,
            text="Full",
            variable=self.mode,
            value="Full",
            command=self.update_cut_fields,
        ).pack(side="left", padx=20, pady=5)
        ctk.CTkRadioButton(
            mode_container,
            text="Cut",
            variable=self.mode,
            value="Cut",
            command=self.update_cut_fields,
        ).pack(side="left", padx=20, pady=5)

        # URL Entry
        frame_url = ctk.CTkFrame(master)
        frame_url.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(frame_url, text="Video/Audio URL:").pack(side="left", padx=10)
        self.entry_url = ctk.CTkEntry(frame_url, textvariable=self.url, width=350)
        self.entry_url.pack(side="left", padx=5, fill="x", expand=True)

        # Output Name Entry
        frame_output = ctk.CTkFrame(master)
        frame_output.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(frame_output, text="Output Name:").pack(side="left", padx=10)
        self.entry_output = ctk.CTkEntry(
            frame_output, textvariable=self.output_name, width=300
        )
        self.entry_output.pack(side="left", padx=5, fill="x", expand=True)

        # Output Directory selection
        frame_dir = ctk.CTkFrame(master)
        frame_dir.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(frame_dir, text="Output Directory:").pack(side="left", padx=10)
        self.label_dir = ctk.CTkLabel(
            frame_dir, text=self.out_dir.get(), width=300,
            fg_color=("gray85", "gray25"), corner_radius=6
        )
        self.label_dir.pack(side="left", padx=5, fill="x", expand=True)
        ctk.CTkButton(frame_dir, text="Browse", command=self.browse_directory).pack(
            side="left", padx=10
        )

        # Cut fields and Visualize Cutting button in one row
        self.frame_cut = ctk.CTkFrame(master)
        self.frame_cut.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(self.frame_cut, text="Start Time:").pack(side="left", padx=10)
        self.entry_start = ctk.CTkEntry(
            self.frame_cut, textvariable=self.start_time, width=100
        )
        self.entry_start.pack(side="left", padx=5)
        ctk.CTkLabel(self.frame_cut, text="End Time:").pack(side="left", padx=10)
        self.entry_end = ctk.CTkEntry(self.frame_cut, textvariable=self.end_time, width=100)
        self.entry_end.pack(side="left", padx=5)
        # Visualize Cutting button next to end time box
        self.visualize_btn = ctk.CTkButton(
            self.frame_cut, text="Visualize Cutting", command=self.visualize_cutting
        )
        self.visualize_btn.pack(side="left", padx=10)
        self.update_cut_fields()

        self.button_run = ctk.CTkButton(
            master, text="Run", command=self.start_process_thread,
            font=("Helvetica", 16), height=40
        )
        self.button_run.pack(pady=15, fill="x", padx=50)

        self.log_text = ctk.CTkTextbox(master, state="disabled", height=200)
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)

        # Centered Button group for Open Output Directory / Open Output File
        frame_buttons = ctk.CTkFrame(master)
        frame_buttons.pack(pady=15)

        self.open_dir_btn = ctk.CTkButton(
            frame_buttons, text="Open Output Directory", command=self.open_directory,
            font=("Helvetica", 14), height=35
        )
        self.open_dir_btn.pack(side="left", padx=10)

        self.open_file_btn = ctk.CTkButton(
            frame_buttons, text="Open Output File", command=self.open_output_file,
            font=("Helvetica", 14), height=35
        )
        self.open_file_btn.pack(side="left", padx=10)
        self.open_file_btn.configure(state="disabled")  # Disabled until process complete

        # Status frame containing progress bar and status
        status_frame = ctk.CTkFrame(master)
        status_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        # Overall progress bar
        self.overall_progress = ctk.CTkProgressBar(status_frame)
        self.overall_progress.pack(side="top", fill="x", padx=5, pady=5)
        self.overall_progress.set(0)  # Initialize to 0

        # Bottom status label
        self.status_label = ctk.CTkLabel(
            status_frame, text="Ready", anchor="w", height=20
        )
        self.status_label.pack(side="bottom", fill="x", padx=5, pady=5)

    def check_dependencies_on_startup(self):
        # Don't withdraw the window initially - this causes issues with CTk
        # self.master.withdraw()
        
        # Instead, show a loading label
        loading_frame = ctk.CTkFrame(self.master)
        loading_frame.pack(expand=True, fill="both")
        loading_label = ctk.CTkLabel(
            loading_frame, 
            text="Checking dependencies...", 
            font=("Helvetica", 18)
        )
        loading_label.pack(expand=True, pady=50)
        self.master.update()
        
        result = check_dependencies_before_main(self.master)
        
        # Remove the loading frame
        loading_frame.destroy()
        
        if not result:
            messagebox.showerror("Fatal Error", "Dependency check failed. Exiting.")
            self.master.after(100, self.master.quit)
            return False
        
        return True

    def browse_directory(self):
        path = filedialog.askdirectory(title="Select Output Directory")
        if path:
            self.out_dir.set(path + "/")
            self.label_dir.configure(text=self.out_dir.get())

    def visualize_cutting(self):
        webbrowser.open("https://ytcutter.com/")

    def update_cut_fields(self):
        if self.mode.get() == "Cut":
            self.entry_start.configure(state="normal")
            self.entry_end.configure(state="normal")
            self.visualize_btn.configure(state="normal")
        else:
            self.entry_start.configure(state="disabled")
            self.entry_end.configure(state="disabled")
            self.visualize_btn.configure(state="disabled")

    def update_mode_options(self):
        self.mode.set("Full")
        self.update_cut_fields()

    def log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def set_status(self, message):
        self.status_label.configure(text=message)

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
        self.button_run.configure(state="disabled")
        self.open_file_btn.configure(state="disabled")
        thread = threading.Thread(target=self.run_process)
        thread.start()

    def run_process(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
        self.set_status("Starting process...")
        self.overall_progress.set(0)

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
        self.overall_progress.set(1)  # Set to 100%
        self.button_run.configure(state="normal")
        self.open_file_btn.configure(state="normal")


if __name__ == "__main__":
    root = ctk.CTk()
    app = GUIApp(root)
    root.mainloop()
