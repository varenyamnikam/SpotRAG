import tkinter as tk
from tkinter import filedialog, messagebox
import requests
import cv2
import threading
import os

class VideoQueryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Query UI with Player")
        
        # Video playback variables
        self.video_path = None
        self.cap = None
        self.is_playing = False
        self.play_thread = None

        # Create UI components
        self.create_widgets()

    def create_widgets(self):
        # Video file selection
        video_file_label = tk.Label(self.root, text="Select Video File:")
        video_file_label.grid(row=0, column=0, padx=10, pady=10)
        self.video_file_entry = tk.Entry(self.root, width=40)
        self.video_file_entry.grid(row=0, column=1, padx=10, pady=10)
        select_button = tk.Button(self.root, text="Browse", command=self.select_video)
        select_button.grid(row=0, column=2, padx=10, pady=10)

        # Preset queries message
        preset_label = tk.Label(self.root, text="Using preset timestamp queries.")
        preset_label.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        # Output directory input
        output_dir_label = tk.Label(self.root, text="Output Directory (optional):")
        output_dir_label.grid(row=2, column=0, padx=10, pady=10)
        self.output_dir_entry = tk.Entry(self.root, width=40)
        self.output_dir_entry.grid(row=2, column=1, padx=10, pady=10)
        self.output_dir_entry.insert(0, ".")  # Default to current directory

        # File path input
        file_path_label = tk.Label(self.root, text="File Path (optional):")
        file_path_label.grid(row=3, column=0, padx=10, pady=10)
        self.file_path_entry = tk.Entry(self.root, width=40)
        self.file_path_entry.grid(row=3, column=1, padx=10, pady=10)
        self.file_path_entry.insert(0, "timestamps.json")  # Default to "timestamps.json"

        # Video Player Controls
        self.play_button = tk.Button(self.root, text="Play", command=self.play_video, state=tk.DISABLED)
        self.play_button.grid(row=4, column=0, padx=10, pady=10)

        self.pause_button = tk.Button(self.root, text="Pause", command=self.pause_video, state=tk.DISABLED)
        self.pause_button.grid(row=4, column=1, padx=10, pady=10)

        self.stop_button = tk.Button(self.root, text="Stop", command=self.stop_video, state=tk.DISABLED)
        self.stop_button.grid(row=4, column=2, padx=10, pady=10)

        # Submit button
        submit_button = tk.Button(self.root, text="Submit", command=self.submit_request)
        submit_button.grid(row=5, column=0, columnspan=3, pady=20)

        # Result display label
        self.result_label = tk.Label(self.root, text="Response will be shown here.")
        self.result_label.grid(row=6, column=0, columnspan=3, pady=10)

    def select_video(self):
        file_path = filedialog.askopenfilename(
            title="Select a video file", 
            filetypes=[("Video files", "*.mp4 *.avi *.mov")]
        )
        if file_path:
            self.video_path = file_path
            self.video_file_entry.delete(0, tk.END)  # Clear existing entry
            self.video_file_entry.insert(0, file_path)  # Insert selected file path

            # Enable video player controls
            self.play_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)

    def play_video(self):
        if not self.video_path:
            messagebox.showerror("Error", "Please select a video file first.")
            return

        if not self.is_playing:
            self.is_playing = True
            self.play_thread = threading.Thread(target=self._play_video_thread)
            self.play_thread.start()

    def _play_video_thread(self):
        try:
            self.cap = cv2.VideoCapture(self.video_path)
            
            while self.is_playing:
                ret, frame = self.cap.read()
                if not ret:
                    break

                # Resize frame to a reasonable size
                frame = cv2.resize(frame, (640, 480))
                cv2.imshow('Video Player', frame)
                
                # Wait for 25ms (40 fps) and check if 'q' is pressed
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break

            self.cap.release()
            cv2.destroyAllWindows()
            self.is_playing = False
        except Exception as e:
            messagebox.showerror("Playback Error", str(e))

    def pause_video(self):
        self.is_playing = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

    def stop_video(self):
        self.is_playing = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

    def submit_request(self):
        if not self.video_path:
            self.result_label.config(text="Please provide a video file.")
            return

        # Define preset timestamp queries
        queries_list = [
            "At what timestamp does Andrew Huberman announce the practical tools for optimizing your morning routine?",
            "At what timestamp does Andrew Huberman welcome the audience to a special episode of After School?",
            "At what timestamp does Andrew Huberman introduce himself as a professor at Stanford School of Medicine?",
            "At what timestamp does Andrew Huberman mention his role as the host of the Huberman Lab Podcast?",
        ]

        url = "http://127.0.0.1:8000/process_video_and_find_answer/"
        files = {"video_file": open(self.video_path, "rb")}
        
        # Prepare form data as a list of tuples to support multiple "queries" entries
        data = []
        for query in queries_list:
            data.append(("queries", query))
        data.append(("output_dir", self.output_dir_entry.get()))
        data.append(("file_path", self.file_path_entry.get()))
        
        try:
            response = requests.post(url, files=files, data=data)

            if response.ok:
                self.result_label.config(text="Response: " + str(response.json()))
            else:
                self.result_label.config(text=f"Error: {response.status_code} - {response.text}")
        except requests.RequestException as e:
            self.result_label.config(text=f"Request Error: {str(e)}")

def main():
    root = tk.Tk()
    app = VideoQueryApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()