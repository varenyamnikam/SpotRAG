from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends, Body
from pathlib import Path
from whisperX import process_video_for_transcription
from llm import find_answer_with_timestamp
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp as youtube_dl
import logging
from pydantic import BaseModel
import os
import uuid
import hashlib
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for testing)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Cache configuration
CACHE_DIR = "video_cache"
CACHE_INDEX_FILE = "cache_index.json"

class YouTubeRequest(BaseModel):
    youtube_url: str
    query: str
    output_dir: str = "."
    file_path: str = "timestamps.json"

def ensure_cache_directory():
    """Ensure cache directory and index file exist."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    if not os.path.exists(CACHE_INDEX_FILE):
        with open(CACHE_INDEX_FILE, 'w') as f:
            json.dump({}, f)

def get_video_id_from_url(url: str) -> str:
    """Extract video ID from YouTube URL using yt-dlp."""
    try:
        with youtube_dl.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get('id', '')
    except Exception as e:
        logging.warning(f"Could not extract video ID from URL: {e}")
        # Fallback: create hash from URL
        return hashlib.md5(url.encode()).hexdigest()

def get_cache_key(video_url: str) -> str:
    """Generate cache key from video URL."""
    video_id = get_video_id_from_url(video_url)
    return f"youtube_{video_id}"

def load_cache_index() -> dict:
    """Load the cache index from file."""
    try:
        with open(CACHE_INDEX_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_cache_index(cache_index: dict):
    """Save the cache index to file."""
    with open(CACHE_INDEX_FILE, 'w') as f:
        json.dump(cache_index, f, indent=2)

def get_cached_video_info(cache_key: str) -> dict:
    """Get cached video information if it exists."""
    cache_index = load_cache_index()
    cached_entry = cache_index.get(cache_key)
    
    if not cached_entry:
        return None
    
    cache_dir = cached_entry.get('cache_dir')
    if not cache_dir or not os.path.exists(cache_dir):
        # Cache directory doesn't exist, remove from index
        cache_index.pop(cache_key, None)
        save_cache_index(cache_index)
        return None
    
    # Verify that required files exist
    required_files = [
        os.path.join(cache_dir, "timestamps.json"),
        os.path.join(cache_dir, "timestamps.txt"),
        os.path.join(cache_dir, "transcription.txt")
    ]
    
    if not all(os.path.exists(f) for f in required_files):
        logging.warning(f"Cache incomplete for {cache_key}, will reprocess")
        return None
    
    return cached_entry

def cache_video_info(cache_key: str, cache_dir: str, video_info: dict):
    """Cache video information."""
    cache_index = load_cache_index()
    cache_index[cache_key] = {
        'cache_dir': cache_dir,
        'video_info': video_info,
        'timestamp': os.path.getctime(cache_dir) if os.path.exists(cache_dir) else None
    }
    save_cache_index(cache_index)

def transcription_files_exist(output_dir: str, file_path: str) -> bool:
    """
    Check if transcription files already exist in the output directory.
    """
    timestamps_path = os.path.join(output_dir, file_path)
    txt_path = os.path.join(output_dir, "timestamps.txt")
    transcription_path = os.path.join(output_dir, "transcription.txt")
    
    return all(os.path.exists(path) for path in [timestamps_path, txt_path, transcription_path])

@app.post("/process_youtube_video/")
async def process_youtube_video(request: YouTubeRequest):
    """
    API endpoint that processes a YouTube video, transcribes it, and returns the best answer to the query.
    Uses caching to avoid redownloading and reprocessing the same video.
    """
    logging.info(f"YouTube request received for URL: {request.youtube_url}")

    try:
        # Ensure cache directory exists
        ensure_cache_directory()
        
        # Generate cache key
        cache_key = get_cache_key(request.youtube_url)
        logging.info(f"Cache key for video: {cache_key}")
        
        # Check if video is already cached
        cached_info = get_cached_video_info(cache_key)
        
        if cached_info:
            logging.info(f"Video found in cache: {cache_key}")
            cache_dir = cached_info['cache_dir']
            video_info = cached_info['video_info']
            
            # Use cached transcription files
            result = find_answer_with_timestamp(request.query, os.path.join(cache_dir, request.file_path))
            
            if not result or (isinstance(result, dict) and "error" in result):
                raise HTTPException(status_code=404, detail="No valid answer found.")
            
            response = {
                "answer": result,
                "video_info": video_info,
                "cached": True
            }
            return response
        
        # Video not in cache, proceed with download and processing
        logging.info(f"Video not in cache, downloading: {request.youtube_url}")
        
        # Create cache directory for this video
        cache_dir = os.path.join(CACHE_DIR, cache_key)
        os.makedirs(cache_dir, exist_ok=True)

        # Download YouTube video using yt-dlp
        logging.info(f"Downloading YouTube video using yt-dlp: {request.youtube_url}")

        ydl_opts = {
            'outtmpl': os.path.join(cache_dir, f"{cache_key}.%(ext)s"),
            'format': 'best', # Try to get the best quality
            'noplaylist': True,
            'quiet': True, # Suppress yt-dlp output
            'merge_output_format': 'mp4' # Ensure output is mp4 if merging happens
        }

        video_info = None
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            # Extract info and download the video
            info_dict = ydl.extract_info(request.youtube_url, download=True)
            video_info = {
                "title": info_dict.get('title', 'N/A'),
                "author": info_dict.get('uploader', 'N/A'),
                "length_seconds": info_dict.get('duration', 'N/A'),
                "thumbnail_url": info_dict.get('thumbnail', 'N/A')
            }

        # Find the actual downloaded file path
        downloaded_files = [f for f in os.listdir(cache_dir) if f.startswith(cache_key)]
        if not downloaded_files:
             raise Exception("yt-dlp failed to download the video.")

        video_filename = downloaded_files[0]
        video_path = os.path.join(cache_dir, video_filename)
        logging.info(f"Video downloaded to: {video_path}")

        # Process the video for transcription (always needed for new cache entries)
        logging.info("Processing video for transcription...")
        process_video_for_transcription(video_path, cache_dir)
        
        # Cache the video information
        cache_video_info(cache_key, cache_dir, video_info)
        logging.info(f"Video cached successfully: {cache_key}")

        # Find the best answer based on the query
        result = find_answer_with_timestamp(request.query, os.path.join(cache_dir, request.file_path))

        if not result or (isinstance(result, dict) and "error" in result):
            raise HTTPException(status_code=404, detail="No valid answer found.")

        # Add video metadata to the response
        response = {
            "answer": result,
            "video_info": video_info,
            "cached": False
        }

        return response

    except youtube_dl.DownloadError as e:
        logging.error(f"yt-dlp download error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Video download error: {str(e)}")
    except Exception as e:
        logging.error(f"Error processing YouTube video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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
    logging.info("File upload request received.")

    try:
        # Create a unique directory for this request
        request_id = str(uuid.uuid4())
        request_output_dir = os.path.join(output_dir, request_id)
        os.makedirs(request_output_dir, exist_ok=True)

        # Save uploaded file safely
        video_path = Path(f"{request_output_dir}/{video_file.filename}")
        with video_path.open("wb") as buffer:
            buffer.write(await video_file.read())

        logging.info(f"Video saved to: {video_path}")

        # Check if transcription files already exist
        if not transcription_files_exist(request_output_dir, file_path):
            logging.info("Transcription files not found, processing video...")
            # Step 1: Process the video for transcription
            process_video_for_transcription(str(video_path), request_output_dir)
        else:
            logging.info("Using existing transcription files...")

        # Step 2: Find the best answer based on the query
        result_file_path = os.path.join(request_output_dir, file_path)
        result = find_answer_with_timestamp(query, result_file_path)

        if not result or (isinstance(result, dict) and "error" in result):
            raise HTTPException(status_code=404, detail="No valid answer found.")

        return {"answer": result}

    except Exception as e:
        logging.error(f"Error processing uploaded video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cache/status")
async def get_cache_status():
    """Get information about the current cache status."""
    ensure_cache_directory()
    cache_index = load_cache_index()
    
    cache_stats = {
        "total_cached_videos": len(cache_index),
        "cache_directory": CACHE_DIR,
        "cached_videos": []
    }
    
    for cache_key, cache_info in cache_index.items():
        video_info = cache_info.get('video_info', {})
        cache_stats["cached_videos"].append({
            "cache_key": cache_key,
            "title": video_info.get("title", "N/A"),
            "author": video_info.get("author", "N/A"),
            "cache_dir": cache_info.get('cache_dir'),
            "exists": os.path.exists(cache_info.get('cache_dir', ''))
        })
    
    return cache_stats

@app.delete("/cache/clear")
async def clear_cache():
    """Clear all cached videos."""
    try:
        ensure_cache_directory()
        cache_index = load_cache_index()
        
        # Remove cache directories
        removed_count = 0
        for cache_key, cache_info in cache_index.items():
            cache_dir = cache_info.get('cache_dir')
            if cache_dir and os.path.exists(cache_dir):
                import shutil
                shutil.rmtree(cache_dir)
                removed_count += 1
        
        # Clear the cache index
        save_cache_index({})
        
        return {
            "message": f"Cache cleared successfully. Removed {removed_count} cached videos.",
            "removed_count": removed_count
        }
    except Exception as e:
        logging.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")

@app.delete("/cache/{cache_key}")
async def remove_cached_video(cache_key: str):
    """Remove a specific video from cache."""
    try:
        ensure_cache_directory()
        cache_index = load_cache_index()
        
        if cache_key not in cache_index:
            raise HTTPException(status_code=404, detail="Video not found in cache")
        
        # Remove the cache directory
        cache_info = cache_index[cache_key]
        cache_dir = cache_info.get('cache_dir')
        if cache_dir and os.path.exists(cache_dir):
            import shutil
            shutil.rmtree(cache_dir)
        
        # Remove from index
        del cache_index[cache_key]
        save_cache_index(cache_index)
        
        return {"message": f"Cached video {cache_key} removed successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error removing cached video: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error removing cached video: {str(e)}")