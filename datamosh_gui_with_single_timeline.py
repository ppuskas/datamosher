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
    command = f'ffmpeg -i {input_path} -vf "select=\'eq(pict_type,I)\'" -vsync vfr -vframes 1 -f null -'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
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
    timeline['to'] = total_frames - 1  # Set scrubber range to match video length
    set_end_handle_offset()

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

# Update the end handle with a default offset of 10 frames from the start handle
def set_end_handle_offset():
    start_frame = int(start_handle_position.get())
    end_handle_position.set(min(start_frame + 10, total_frames - 1))

# Scrub through the video with the timeline
def scrub_timeline(event):
    start_frame = int(start_handle_position.get())
    end_frame = int(end_handle_position.get())
    
    if event == str(start_frame):  # If adjusting start handle
        set_end_handle_offset()
        display_frame(start_frame)
    elif event == str(end_frame):  # If adjusting end handle
        display_frame(end_frame) 
    frame_label.config(text=f"Start: {start_frame}, End: {end_frame}")

# Add selected range to the list
def add_range():
    start = int(start_handle_position.get())
    end = int(end_handle_position.get())
    frame_ranges.append((start, end))
    update_frame_list()

# Clear all ranges
def clear_ranges():
    frame_ranges.clear()  # Clear the frame ranges
    update_frame_list()  # Refresh the frame list display

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
root.title("Datamosh GUI with Range Selection, Viewer Feedback, and Clear Ranges")

input_video = tk.StringVar()
delta_frames = tk.StringVar(value="5")
frame_ranges = []
remove_iframes = tk.BooleanVar()

# Widgets
tk.Label(root, text="Select video file:").grid(row=0, column=0, padx=10, pady=10)
tk.Entry(root, textvariable=input_video, width=50).grid(row=0, column=1, padx=10)
tk.Button(root, text="Browse", command=select_file).grid(row=0, column=2, padx=10)

tk.Label(root, text="Delta Frames (P-frame repeats):").grid(row=1, column=0, padx=10)
tk.Entry(root, textvariable=delta_frames).grid(row=1, column=1, padx=10)

# Add I-frame removal checkbox
tk.Checkbutton(root, text="Remove I-frames", variable=remove_iframes).grid(row=1, column=2, padx=10)

# Button to clear ranges
tk.Button(root, text="Clear Ranges", command=clear_ranges).grid(row=2, column=0, padx=10, pady=10)

tk.Button(root, text="Add Range", command=add_range).grid(row=2, column=1, padx=10, pady=10)
frame_list = tk.Listbox(root, height=5)
frame_list.grid(row=2, column=2, padx=10, pady=10)

tk.Button(root, text="Apply Datamosh", command=apply_datamosh).grid(row=3, column=0, columnspan=2, pady=20)

# Timeline with start/end handles simulation
start_handle_position = tk.IntVar()
end_handle_position = tk.IntVar()

timeline = ttk.Scale(root, from_=0, to=100, orient="horizontal", length=300, variable=start_handle_position, command=scrub_timeline)
timeline.grid(row=4, column=0, pady=10)

# The end handle will be adjusted programmatically
end_handle_position = ttk.Scale(root, from_=0, to=100, orient="horizontal", length=300, variable=end_handle_position, command=scrub_timeline)
end_handle_position.grid(row=4, column=1, pady=10)

frame_label = tk.Label(root, text="Start: 0, End: 10")
frame_label.grid(row=4, column=2, padx=10)

video_label = tk.Label(root)
video_label.grid(row=5, column=0, columnspan=3, pady=10)

# Run the GUI
root.mainloop()
