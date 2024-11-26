import whisperx
from moviepy.audio.io.AudioFileClip import AudioFileClip
import json
import os

def process_video_for_transcription(video_file, output_dir=".", model_type="medium.en", 
                                    device="cuda", compute_type="float16"):
    """
    Extract audio from video, transcribe it using whisperx, align transcriptions, 
    and save the output in JSON and TXT formats.

    :param video_file: Path to the input video file.
    :param output_dir: Directory where the output files will be saved (default is the current directory).
    :param model_type: ASR model to use for transcription (default is "medium.en").
    :param device: Device to use for processing ("cuda" for GPU, "cpu" for CPU).
    :param compute_type: Compute type ("float16" or "float32").
    """
    # Helper function to print messages in green
    def print_green(message):
        print(f"\033[92m{message}\033[0m")  # ANSI code for green text

    # Step 1: Extract audio from video
    audio_file = video_file.rsplit('.', 1)[0] + ".wav"  # Use the same name as the video, with .wav extension
    print_green("Extracting audio from video...")
    try:
        clip = AudioFileClip(video_file)
        clip.write_audiofile(audio_file, fps=16000, codec="pcm_s16le")  # Ensures compatible WAV format
        clip.close()
        print_green(f"Audio extracted and saved to: {audio_file}")
    except Exception as e:
        print_green(f"Error extracting audio: {e}")
        return

    # Step 2: Load ASR model (equivalent to --model medium.en)
    print_green("Loading ASR model...")
    try:
        asr_model = whisperx.load_model(model_type, device=device, compute_type=compute_type)
    except Exception as e:
        print_green(f"Error loading ASR model: {e}")
        return

    # Step 3: Transcribe the audio file
    print_green("Transcribing the audio...")
    try:
        transcription_result = asr_model.transcribe(audio_file)
    except Exception as e:
        print_green(f"Error transcribing audio: {e}")
        return

    # Step 4: Load alignment model
    print_green("Loading alignment model...")
    try:
        alignment_model = whisperx.load_align_model(language_code="en", device=device)
    except Exception as e:
        print_green(f"Error loading alignment model: {e}")
        return

    # Step 5: Align transcriptions (equivalent to --align_model WAV2VEC2_ASR_LARGE_LV60K_960H)
    print_green("Aligning transcription...")
    try:
        aligned_result = whisperx.align(
            transcription_result["segments"],
            model=alignment_model[0],  # Use the first element of the tuple as the model
            align_model_metadata=alignment_model[1],  # Use the second element as metadata
            audio=audio_file,
            device=device
        )
    except Exception as e:
        print_green(f"Error aligning transcription: {e}")
        return

    # Step 6: Save outputs in all formats
    print_green("Saving transcription and alignment results...")

    # Save aligned output as JSON
    aligned_json_file = os.path.join(output_dir, "timestamps.json")
    filtered_segments = [
        {
            "start": segment["start"],
            "end": segment["end"],
            "text": segment["text"]
        }
        for segment in aligned_result["segments"]
    ]
    try:
        with open(aligned_json_file, "w") as json_file:
            json.dump(filtered_segments, json_file, indent=4)
        print_green(f"Aligned JSON with segment-level timestamps saved to: {aligned_json_file}")
    except Exception as e:
        print_green(f"Error saving aligned JSON: {e}")

    # Save aligned output as TXT
    aligned_txt_file = os.path.join(output_dir, "timestamps.txt")
    try:
        with open(aligned_txt_file, "w") as txt_file:
            for segment in aligned_result["segments"]:
                start = segment["start"]
                end = segment["end"]
                text = segment["text"]
                txt_file.write(f"[{start:.2f} - {end:.2f}]: {text}\n")
        print_green(f"Aligned TXT saved to: {aligned_txt_file}")
    except Exception as e:
        print_green(f"Error saving aligned TXT: {e}")

    # Save original transcription as TXT
    transcription_txt_file = os.path.join(output_dir, "transcription.txt")
    try:
        with open(transcription_txt_file, "w") as txt_file:
            for segment in transcription_result["segments"]:
                txt_file.write(f"{segment['text']}\n")
        print_green(f"Original transcription saved to: {transcription_txt_file}")
    except Exception as e:
        print_green(f"Error saving transcription TXT: {e}")

    # Optional: Cleanup (delete the audio file after processing)
    try:
        os.remove(audio_file)
        print_green(f"Deleted temporary audio file: {audio_file}")
    except Exception as e:
        print_green(f"Error deleting temporary audio file: {e}")


# Example usage of the function
# video_file = "new_video.mp4"  # Input video file
# output_dir = "."  # Directory to save the output
# process_video_for_transcription(video_file, output_dir)
