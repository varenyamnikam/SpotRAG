import tkinter as tk
from tkinter import filedialog
import requests

# Function to handle the file selection
def select_video():
    file_path = filedialog.askopenfilename(
        title="Select a video file", 
        filetypes=[("Video files", "*.mp4 *.avi *.mov")]
    )
    video_file_entry.delete(0, tk.END)  # Clear existing entry
    video_file_entry.insert(0, file_path)  # Insert selected file path

# Function to handle the form submission and API request
def submit_request():
    video_path = video_file_entry.get()
    output_dir = output_dir_entry.get()
    file_path_val = file_path_entry.get()

    if not video_path:
        result_label.config(text="Please provide a video file.")
        return

    # Define preset timestamp queries
    queries_list = [
    "At what timestamp does Andrew Huberman announce the practical tools for optimizing your morning routine?",
    "At what timestamp does Andrew Huberman welcome the audience to a special episode of After School?",
    "At what timestamp does Andrew Huberman introduce himself as a professor at Stanford School of Medicine?",
    "At what timestamp does Andrew Huberman mention his role as the host of the Huberman Lab Podcast?",
    "At what timestamp does Andrew Huberman repeat his announcement about practical tools for optimizing your morning routine?",
    "At what timestamp does Andrew Huberman discuss the foundational behaviors that set the stage for success?",
    "At what timestamp does Andrew Huberman ask how one can lift more, focus better, and remember things better?",
    "At what timestamp does Andrew Huberman say 'Let's think about the foundation of that'?",
    "At what timestamp does Andrew Huberman mention that success comes down to sleep and non-sleep deep rest?",
    "At what timestamp does Andrew Huberman state that sleep is the fundamental?",
    "At what timestamp does Andrew Huberman discuss how inconsistent sleep affects overall performance?",
    "At what timestamp does Andrew Huberman mention that poor sleep screws up metabolism and the immune system?",
    "At what timestamp does Andrew Huberman warn that one night's bad sleep doesn't ruin performance completely?",
    "At what timestamp does Andrew Huberman say 'But let's talk about sleep'?",
    "At what timestamp does Andrew Huberman discuss shift work?",
    "At what timestamp does Andrew Huberman advise that you should try and get really good sleep?",
    "At what timestamp does Andrew Huberman mention '80% of the time, 80% of the nights'?",
    "At what timestamp does Andrew Huberman mention that the other 20% of nights might not be good?",
    "At what timestamp does Andrew Huberman state 'there are a couple of things you can do'?",
    "At what timestamp does Andrew Huberman explain that every cell has a 24-hour circadian rhythm?",
    "At what timestamp does Andrew Huberman advise aligning the clocks in your body?",
    "At what timestamp does Andrew Huberman explain why traveling overseas affects your gut?",
    "At what timestamp does Andrew Huberman warn that misaligned clocks can lead to sickness?",
    "At what timestamp does Andrew Huberman stress the importance of getting natural light within an hour of waking up?",
    "At what timestamp does Andrew Huberman advise turning on bright lights if you wake before the sun?",
    "At what timestamp does Andrew Huberman note that dense cloud cover still provides more photons than artificial lights?",
    "At what timestamp does Andrew Huberman instruct to get five to ten minutes of sunlight without sunglasses?",
    "At what timestamp does Andrew Huberman mention that this sunlight exposure should be done most days?",
    "At what timestamp does Andrew Huberman highlight the outsized effect of sunlight exposure?",
    "At what timestamp does Andrew Huberman state that sunlight modulates the timing of the cortisol pulse?",
    "At what timestamp does Andrew Huberman say you'll get a boost in cortisol once every 24 hours?",
    "At what timestamp does Andrew Huberman mention that a cortisol boost is healthy?",
    "At what timestamp does Andrew Huberman explain how cortisol sets your temperature rhythm and affects mood?",
    "At what timestamp does Andrew Huberman emphasize that the cortisol pulse should occur as early as possible?",
    "At what timestamp does Andrew Huberman ask what's triggering the cortisol pulse?",
    "At what timestamp does Andrew Huberman explain that genetic programs entrain the cortisol pulse but light anchors it?",
    "At what timestamp does Andrew Huberman instruct to anchor your cortisol pulse with bright light?",
    "At what timestamp does Andrew Huberman describe a late shifted cortisol pulse?",
    "At what timestamp does Andrew Huberman explain the circadian dead zone?",
    "At what timestamp does Andrew Huberman warn that being indoors causes the cortisol pulse to come in the afternoon?",
    "At what timestamp does Andrew Huberman state that a late cortisol pulse is a signature of depression?",
    "At what timestamp does Andrew Huberman caution that spending time indoors with sunglasses may be detrimental?",
    "At what timestamp does Andrew Huberman advise that you don't need to stare at bright light?",
    "At what timestamp does Andrew Huberman warn not to stare at any light that is too bright?",
    "At what timestamp does Andrew Huberman instruct you to blink as necessary?",
    "At what timestamp does Andrew Huberman explain that indirect sunlight triggers melanopsin ganglion cells?",
    "At what timestamp does Andrew Huberman state that these ganglion cells send a signal to the hypothalamus?",
    "At what timestamp does Andrew Huberman describe how the hypothalamus releases a wake-up peptide and sets a timer for melatonin release?",
    "At what timestamp does Andrew Huberman thank the audience for joining this special episode of After School?",
    "At what timestamp does Andrew Huberman mention his website and social media?"
]


    url = "http://127.0.0.1:8000/process_video_and_find_answer/"
    files = {"video_file": open(video_path, "rb")}
    
    # Prepare form data as a list of tuples to support multiple "queries" entries
    data = []
    for query in queries_list:
        data.append(("queries", query))
    data.append(("output_dir", output_dir))
    data.append(("file_path", file_path_val))
    
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

# Preset queries message (removed individual query input)
preset_label = tk.Label(root, text="Using preset timestamp queries.")
preset_label.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

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
