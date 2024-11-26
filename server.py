from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from whisperX import process_video_for_transcription
from llm import find_answer_with_timestamp

app = FastAPI()

@app.post("/process_video_and_find_answer/")
async def process_video_and_find_answer(
    video_file: UploadFile = File(...),
    query: str = Form(...),
    output_dir: str = Form(default="."),
    file_path: str = Form(default="timestamps.json"),
):
    """
    API endpoint that processes a video, transcribes it, and returns the best answer to the query.
    """
    print("Request received.")

    try:
        # Save the uploaded video file temporarily
        video_path = f"./{video_file.filename}"
        with open(video_path, "wb") as buffer:
            buffer.write(await video_file.read())

        # Step 1: Process the video for transcription
        process_video_for_transcription(video_path, output_dir)

        # Step 2: Find the best answer based on the query
        result = find_answer_with_timestamp(query, file_path)

        if "error" in result:
            raise HTTPException(status_code=404, detail="No valid answer found.")

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
