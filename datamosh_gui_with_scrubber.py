import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import cv2
import subprocess
from datetime import datetime

# Function to generate unique output filenames
def generate_unique_filename(base_name="output", extension=".mp4"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}{extension}"

# Check if the video has enough I-frames and re-encode if necessary
def check_keyframes_and_reencode(input_path):
    # Command to count I-frames using FFmpeg
    command = f'ffmpeg -i {input_path} -vf "select=\'eq(pict_type,I)\'" -vsync vfr -vframes 1 -f null -'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    # If the video has very few I-frames, re-encode it
    if "frame=0" in result.stderr:  # Example check for no I-frames
        reencoded_file = generate_unique_filename("reencoded_video", ".mp4")
        messagebox.showinfo("Re-encoding", "Re-encoding video to add more I-frames.")
        subprocess.run(f"ffmpeg -i {input_path} -g 1 -c:v libx264 {reencoded_file}", shell=True)
        return reencoded_file
    return input_path

# Function to select video file
def select_file():
    file_path = filedialog.askopenfilename(title="Select video file", filetypes=[("MP4 files", "*.mp4")])
    input_video.set(file_path)
    file_path = check_keyframes_and_reencode(file_path)  # Re-encode if needed
    load_video(file_path)

# Load the video and update scrubber
def load_video(file_path):
    global cap, total_frames
    cap = cv2.VideoCapture(file_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    update_slider()
    display_frame(0)  # Start at the first frame

# Update scrubber to match video length
def update_slider():
    in_handle['to'] = total_frames - 1  # Set scrubber range to match video length
    out_handle['to'] = total_frames - 1

# Display the frame at the current scrubber position
def display_frame(frame_number):
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    if ret:
        frame = cv2.resize(frame, (480, 320))
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = tk.PhotoImage(master=root, data=cv2.imencode(".ppm", img)[1].tobytes())
        video_label.config(image=img)
        video_label.image = img
    frame_label.config(text=f"Frame: {frame_number}")  # Update frame label

# Scrub through the video with in/out handles
# Scrub through the video with in/out handles
def scrub_video(event):
    in_frame = int(in_handle.get())  # Get the in_handle value
    out_frame = int(out_handle.get())  # Get the out_handle value
    
    if event == str(in_handle.get()):  # Check if the 'in' handle is being moved
        display_frame(in_frame)
    else:  # If 'out' handle is being moved
        display_frame(out_frame)


# Add selected range to the list
def add_range():
    start = start_frame.get()
    end = end_frame.get()
    if start.isdigit() and end.isdigit():
        frame_ranges.append((start, end))
        update_frame_list()

# Update frame list display
def update_frame_list():
    frame_list.delete(0, tk.END)
    for start, end in frame_ranges:
        frame_list.insert(tk.END, f"Start: {start}, End: {end}")

# Apply datamosh effects
def apply_datamosh():
    input_path = input_video.get()
    delta = delta_frames.get()
    remove_i_frame = remove_iframes.get()
    
    if not os.path.isfile(input_path):
        messagebox.showerror("Error", "Please select a valid video file.")
        return

    output_file = generate_unique_filename("moshed_output", ".mp4")

    for start, end in frame_ranges:
        # Construct the command based on the user input
        if remove_i_frame:
            command = f"python mosh.py {input_path} -s {start} -e {end} -o {output_file}"
        else:
            command = f"python mosh.py {input_path} -s {start} -e {end} -d {delta} -o {output_file}"

        try:
            subprocess.run(command, shell=True, check=True)
            input_path = output_file  # Use the output of one range as input for the next
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"An error occurred while applying datamosh: {e}")
            return

    messagebox.showinfo("Success", f"Datamoshing complete! Output saved as '{output_file}'")

# GUI Setup
root = tk.Tk()
root.title("Datamosh GUI with Range Selection and Keyframe Check")

input_video = tk.StringVar()
start_frame = tk.StringVar(value="0")
end_frame = tk.StringVar(value="0")
delta_frames = tk.StringVar(value="5")
frame_ranges = []
remove_iframes = tk.BooleanVar()  # Add a checkbox for I-frame removal

# Widgets
tk.Label(root, text="Select video file:").grid(row=0, column=0, padx=10, pady=10)
tk.Entry(root, textvariable=input_video, width=50).grid(row=0, column=1, padx=10)
tk.Button(root, text="Browse", command=select_file).grid(row=0, column=2, padx=10)

tk.Label(root, text="Start Frame:").grid(row=1, column=0, padx=10)
tk.Entry(root, textvariable=start_frame).grid(row=1, column=1, padx=10)

tk.Label(root, text="End Frame:").grid(row=2, column=0, padx=10)
tk.Entry(root, textvariable=end_frame).grid(row=2, column=1, padx=10)

tk.Label(root, text="Delta Frames (P-frame repeats):").grid(row=3, column=0, padx=10)
tk.Entry(root, textvariable=delta_frames).grid(row=3, column=1, padx=10)

# Add I-frame removal checkbox
tk.Checkbutton(root, text="Remove I-frames", variable=remove_iframes).grid(row=3, column=2, padx=10)

tk.Button(root, text="Add Range", command=add_range).grid(row=4, column=0, padx=10, pady=10)
frame_list = tk.Listbox(root, height=5)
frame_list.grid(row=4, column=1, padx=10, pady=10)

tk.Button(root, text="Apply Datamosh", command=apply_datamosh).grid(row=5, column=0, columnspan=2, pady=20)

# Video scrubber with in/out handles
in_handle = ttk.Scale(root, from_=0, to=100, orient="horizontal", length=200, command=scrub_video)
in_handle.grid(row=6, column=0, pady=10)
out_handle = ttk.Scale(root, from_=0, to=100, orient="horizontal", length=200, command=scrub_video)
out_handle.grid(row=6, column=1, pady=10)

frame_label = tk.Label(root, text="Frame: 0")
frame_label.grid(row=6, column=2, padx=10)

video_label = tk.Label(root)
video_label.grid(row=7, column=0, columnspan=3, pady=10)

# Run the GUI
root.mainloop()
