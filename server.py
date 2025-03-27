from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from pathlib import Path
from whisperX import process_video_for_transcription
from llm import find_answer_with_timestamp
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for testing)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


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
        # Save uploaded file safely
        video_path = Path(f"./{video_file.filename}")
        with video_path.open("wb") as buffer:
            buffer.write(await video_file.read())

        # Step 1: Process the video for transcription
        process_video_for_transcription(str(video_path), output_dir)

        # Step 2: Find the best answer based on the query
        result = find_answer_with_timestamp(query, file_path)

        if not result or (isinstance(result, dict) and "error" in result):
            raise HTTPException(status_code=404, detail="No valid answer found.")

        return {"answer": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
