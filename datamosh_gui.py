import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import subprocess

def select_file():
    file_path = filedialog.askopenfilename(title="Select video file", filetypes=[("MP4 files", "*.mp4")])
    input_video.set(file_path)

def apply_datamosh():
    input_path = input_video.get()
    start = start_frame.get()
    end = end_frame.get()
    delta = delta_frames.get()

    if not os.path.isfile(input_path):
        messagebox.showerror("Error", "Please select a valid video file.")
        return

    if not start.isdigit() or not end.isdigit() or not delta.isdigit():
        messagebox.showerror("Error", "Please enter valid numeric values for start frame, end frame, and delta frames.")
        return

    output_path = "moshed_output.mp4"
    command = f"python mosh.py {input_path} -s {start} -e {end} -d {delta} -o {output_path}"

    try:
        subprocess.run(command, shell=True, check=True)
        messagebox.showinfo("Success", f"Datamoshing applied successfully! Output saved to {output_path}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"An error occurred while applying datamosh: {e}")

# Set up the Tkinter window
root = tk.Tk()
root.title("Datamosh GUI")

# Variables to hold the input data
input_video = tk.StringVar()
start_frame = tk.StringVar(value="0")
end_frame = tk.StringVar(value="500")
delta_frames = tk.StringVar(value="5")

# Create and place the widgets
tk.Label(root, text="Select video file:").grid(row=0, column=0, padx=10, pady=10)
tk.Entry(root, textvariable=input_video, width=50).grid(row=0, column=1, padx=10)
tk.Button(root, text="Browse", command=select_file).grid(row=0, column=2, padx=10)

tk.Label(root, text="Start Frame:").grid(row=1, column=0, padx=10)
tk.Entry(root, textvariable=start_frame).grid(row=1, column=1, padx=10)

tk.Label(root, text="End Frame:").grid(row=2, column=0, padx=10)
tk.Entry(root, textvariable=end_frame).grid(row=2, column=1, padx=10)

tk.Label(root, text="Delta Frames (P-frame repeats):").grid(row=3, column=0, padx=10)
tk.Entry(root, textvariable=delta_frames).grid(row=3, column=1, padx=10)

tk.Button(root, text="Apply Datamosh", command=apply_datamosh).grid(row=4, column=0, columnspan=3, pady=20)

# Run the GUI event loop
root.mainloop()
