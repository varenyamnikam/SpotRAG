import csv
import os
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from pathlib import Path
from typing import List, Dict
from whisperX import process_video_for_transcription
from llmtest import find_answers_with_timestamps  # Updated function for batch processing

app = FastAPI()

CSV_FILE = "better_results.csv"  # Define the CSV file name

# Expected timestamps mapping (You may need to update this based on actual expected values)
EXPECTED_TIMESTAMPS = {
    "At what timestamp does Andrew Huberman announce the practical tools for optimizing your morning routine?": "23.043 - 26.804",
    "At what timestamp does Andrew Huberman welcome the audience to a special episode of After School?": "8.339 - 10.92",
    "At what timestamp does Andrew Huberman introduce himself as a professor at Stanford School of Medicine?": "11.44 - 16.041",
    "At what timestamp does Andrew Huberman mention his role as the host of the Huberman Lab Podcast?": "16.321 - 22.463",
    "At what timestamp does Andrew Huberman repeat his announcement about practical tools for optimizing your morning routine?": "27.184 - 31.305",
    "At what timestamp does Andrew Huberman discuss the foundational behaviors that set the stage for success?": "32.591 - 38.055",
    "At what timestamp does Andrew Huberman ask how one can lift more, focus better, and remember things better?": "38.095 - 43.439",
    "At what timestamp does Andrew Huberman say 'Let's think about the foundation of that'?": "43.459 - 45.961",
    "At what timestamp does Andrew Huberman mention that success comes down to sleep and non-sleep deep rest?": "46.442 - 52.786",
    "At what timestamp does Andrew Huberman state that sleep is the fundamental?": "53.707 - 55.529",
    "At what timestamp does Andrew Huberman discuss how inconsistent sleep affects overall performance?": "56.963 - 68.156",
    "At what timestamp does Andrew Huberman mention that poor sleep screws up metabolism and the immune system?": "68.416 - 70.979",
    "At what timestamp does Andrew Huberman warn that one night's bad sleep doesn't ruin performance completely?": "72.541 - 77.985",
    "At what timestamp does Andrew Huberman say 'But let's talk about sleep'?": "78.406 - 81.028",
    "At what timestamp does Andrew Huberman discuss shift work?": "81.048 - 88.474",
    "At what timestamp does Andrew Huberman advise that you should try and get really good sleep?": "89.214 - 90.615",
    "At what timestamp does Andrew Huberman mention '80% of the time, 80% of the nights'?": "91.836 - 94.258",
    "At what timestamp does Andrew Huberman mention that the other 20% of nights might not be good?": "94.418 - 97.659",
    "At what timestamp does Andrew Huberman state 'there are a couple of things you can do'?": "98.22 - 100.561",
    "At what timestamp does Andrew Huberman explain that every cell has a 24-hour circadian rhythm?": "100.641 - 107.265",
    "At what timestamp does Andrew Huberman advise aligning the clocks in your body?": "107.705 - 112.087",
    "At what timestamp does Andrew Huberman explain why traveling overseas affects your gut?": "112.387 - 115.269",
    "At what timestamp does Andrew Huberman warn that misaligned clocks can lead to sickness?": "116.089 - 122.474",
    "At what timestamp does Andrew Huberman stress the importance of getting natural light within an hour of waking up?": "123.615 - 130.881",
    "At what timestamp does Andrew Huberman advise turning on bright lights if you wake before the sun?": "131.261 - 136.385",
    "At what timestamp does Andrew Huberman note that dense cloud cover still provides more photons than artificial lights?": "137.026 - 143.651",
    "At what timestamp does Andrew Huberman instruct to get five to ten minutes of sunlight without sunglasses?": "144.272 - 149.549",
    "At what timestamp does Andrew Huberman mention that this sunlight exposure should be done most days?": "150.382 - 151.843",
    "At what timestamp does Andrew Huberman highlight the outsized effect of sunlight exposure?": "152.403 - 154.744",
    "At what timestamp does Andrew Huberman state that sunlight modulates the timing of the cortisol pulse?": "154.844 - 157.605",
    "At what timestamp does Andrew Huberman say you'll get a boost in cortisol once every 24 hours?": "157.725 - 161.467",
    "At what timestamp does Andrew Huberman mention that a cortisol boost is healthy?": "161.487 - 162.267",
    "At what timestamp does Andrew Huberman explain how cortisol sets your temperature rhythm and affects mood?": "162.427 - 168.05",
    "At what timestamp does Andrew Huberman emphasize that the cortisol pulse should occur as early as possible?": "168.41 - 171.251",
    "At what timestamp does Andrew Huberman ask what's triggering the cortisol pulse?": "171.291 - 172.892",
    "At what timestamp does Andrew Huberman explain that genetic programs entrain the cortisol pulse but light anchors it?": "173.012 - 178.835",
    "At what timestamp does Andrew Huberman instruct to anchor your cortisol pulse with bright light?": "179.595 - 182.197",
    "At what timestamp does Andrew Huberman describe a late shifted cortisol pulse?": "182.957 - 194.044",
    "At what timestamp does Andrew Huberman explain the circadian dead zone?": "194.404 - 203.469",
    "At what timestamp does Andrew Huberman warn that being indoors causes the cortisol pulse to come in the afternoon?": "203.769 - 208.292",
    "At what timestamp does Andrew Huberman state that a late cortisol pulse is a signature of depression?": "208.792 - 213.354",
    "At what timestamp does Andrew Huberman caution that spending time indoors with sunglasses may be detrimental?": "214.194 - 221.377",
    "At what timestamp does Andrew Huberman advise that you don't need to stare at bright light?": "221.557 - 225.339",
    "At what timestamp does Andrew Huberman warn not to stare at any light that is too bright?": "225.359 - 225.819",
    "At what timestamp does Andrew Huberman instruct you to blink as necessary?": "226.139 - 227.18",
    "At what timestamp does Andrew Huberman explain that indirect sunlight triggers melanopsin ganglion cells?": "227.22 - 232.882",
    "At what timestamp does Andrew Huberman state that these ganglion cells send a signal to the hypothalamus?": "233.682 - 237.828",
    "At what timestamp does Andrew Huberman describe how the hypothalamus releases a wake-up peptide and sets a timer for melatonin release?": "238.288 - 248.761",
    "At what timestamp does Andrew Huberman thank the audience for joining this special episode of After School?": "925.745 - 928.126",
    "At what timestamp does Andrew Huberman mention his website and social media?": "949.153 - 956.165"
}



@app.post("/process_video_and_find_answer/")
async def process_video_and_find_answer(
    video_file: UploadFile = File(...),
    queries: List[str] = Form(...),
    output_dir: str = Form(default="."),
    file_path: str = Form(default="timestamps.json"),
):
    """
    API endpoint that processes a video, transcribes it, and returns the best answers for each query.
    Answers are also stored in a CSV file.
    """
    print("Request received.")

    try:
        # Save uploaded video file safely
        video_path = Path(f"./{video_file.filename}")
        with video_path.open("wb") as buffer:
            buffer.write(await video_file.read())

        # Step 1: Process the video for transcription (only once)
        process_video_for_transcription(str(video_path), output_dir)

        # Step 2: Process all queries using batch processing
        query_results = find_answers_with_timestamps(queries, file_path)

        # Prepare results for CSV storage
        results = []
        for query, result in query_results.items():
            if "error" in result:
                answer = "No valid answer found."
                timestamp = "N/A"
                context = "N/A"
            else:
                answer = result["answer"]
                timestamp = result["timestamp"]
                context = result["context"]

            # Get expected timestamp and determine correctness
            expected_timestamp = EXPECTED_TIMESTAMPS.get(query, "N/A")
            correct = "True" if timestamp == expected_timestamp else "False"

            results.append([query, answer, timestamp, expected_timestamp, context, correct])

        # Check if file exists to determine if header is needed
        file_exists = os.path.isfile(CSV_FILE)

        # Append results to the CSV file (if exists), else create a new one
        with open(CSV_FILE, mode="a" if file_exists else "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            # Write header if the file is new
            if not file_exists:
                writer.writerow(["Query", "Answer", "Timestamp", "Expected Timestamp", "Context", "Correct (True/False)"])

            writer.writerows(results)

        return {
            "message": "Processing complete.",
            "csv_file": CSV_FILE,
            "answers": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
