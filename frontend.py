import tkinter as tk
from tkinter import filedialog
import requests

# Function to handle the file selection
def select_video():
    file_path = filedialog.askopenfilename(title="Select a video file", filetypes=[("Video files", "*.mp4 *.avi *.mov")])
    video_file_entry.delete(0, tk.END)  # Clear existing entry
    video_file_entry.insert(0, file_path)  # Insert selected file path

# Function to handle the form submission and API request
def submit_request():
    video_path = video_file_entry.get()
    query = query_entry.get()
    output_dir = output_dir_entry.get()
    file_path = file_path_entry.get()

    if not video_path or not query:
        result_label.config(text="Please provide both video file and query.")
        return

    url = "http://127.0.0.1:8000/process_video_and_find_answer/"
    files = {"video_file": open(video_path, "rb")}
    data = {
        "query": query,
        "output_dir": output_dir,
        "file_path": file_path
    }

    response = requests.post(url, files=files, data=data)

    if response.ok:
        result_label.config(text="Response: " + str(response.json()))
    else:
        result_label.config(text=f"Error: {response.status_code} - {response.text}")

# Create the main window
root = tk.Tk()
root.title("Video Query UI")

# Video file selection
video_file_label = tk.Label(root, text="Select Video File:")
video_file_label.grid(row=0, column=0, padx=10, pady=10)
video_file_entry = tk.Entry(root, width=40)
video_file_entry.grid(row=0, column=1, padx=10, pady=10)
select_button = tk.Button(root, text="Browse", command=select_video)
select_button.grid(row=0, column=2, padx=10, pady=10)

# Query input
query_label = tk.Label(root, text="Enter Query:")
query_label.grid(row=1, column=0, padx=10, pady=10)
query_entry = tk.Entry(root, width=40)
query_entry.grid(row=1, column=1, padx=10, pady=10)

# Output directory input
output_dir_label = tk.Label(root, text="Output Directory (optional):")
output_dir_label.grid(row=2, column=0, padx=10, pady=10)
output_dir_entry = tk.Entry(root, width=40)
output_dir_entry.grid(row=2, column=1, padx=10, pady=10)
output_dir_entry.insert(0, ".")  # Default to current directory

# File path input
file_path_label = tk.Label(root, text="File Path (optional):")
file_path_label.grid(row=3, column=0, padx=10, pady=10)
file_path_entry = tk.Entry(root, width=40)
file_path_entry.grid(row=3, column=1, padx=10, pady=10)
file_path_entry.insert(0, "timestamps.json")  # Default to "timestamps.json"

# Submit button
submit_button = tk.Button(root, text="Submit", command=submit_request)
submit_button.grid(row=4, column=0, columnspan=3, pady=20)

# Result display label
result_label = tk.Label(root, text="Response will be shown here.")
result_label.grid(row=5, column=0, columnspan=3, pady=10)

# Run the Tkinter event loop
root.mainloop()
