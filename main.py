from gui import GUIApp
import customtkinter as ctk
import traceback
import tkinter.messagebox as messagebox

if __name__ == "__main__":
    try:
        # Configure customtkinter appearance
        ctk.set_appearance_mode("system")  # Use system theme (or "dark"/"light")
        ctk.set_default_color_theme("blue")  # Set theme color
        
        # Create the root window
        root = ctk.CTk()
        
        # Handle exceptions gracefully
        try:
            app = GUIApp(root)
            root.mainloop()
        except Exception as e:
            traceback_text = traceback.format_exc()
            messagebox.showerror("Application Error", f"An error occurred:\n{str(e)}\n\nDetails:\n{traceback_text}")
    except Exception as e:
        # This would catch errors even before the GUI starts
        print(f"Critical error: {str(e)}")
        traceback.print_exc()
