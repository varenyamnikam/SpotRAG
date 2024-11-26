import whisperx
from moviepy.audio.io.AudioFileClip import AudioFileClip
import json

# Configuration
video_file = "new_video.mp4"  # Input video file
audio_file = "new_video.wav"  # Extracted audio file (temporary)
output_dir = "."  # Directory to save the output
model_type = "WAV2VEC2_ASR_LARGE_LV60K_960H"
device = "cuda"  # Use "cuda" if GPU available, otherwise "cpu"
compute_type = "float16"  # Use "float32" for CPUs

# print green on cli
def print_green(message):
    print(f"\033[92m{message}\033[0m")  # ANSI code for green text

# Step 1: Extract audio from video
print_green("Extracting audio from video...")
try:
    clip = AudioFileClip(video_file)
    clip.write_audiofile(audio_file, fps=16000, codec="pcm_s16le")  # Ensures compatible WAV format
    clip.close()
    print_green(f"Audio extracted and saved to: {audio_file}")
except Exception as e:
    print_green(f"Error extracting audio: {e}")
    exit()

# Step 2: Load ASR model (equivalent to --model medium.en)
whisper_arch = "medium.en"
print_green("Loading ASR model...")
asr_model = whisperx.load_model(whisper_arch, device=device, compute_type=compute_type)

# Step 3: Transcribe the audio file
print_green("Transcribing the audio...")
transcription_result = asr_model.transcribe(audio_file)

# Step 4: Load alignment model
print_green("Loading alignment model...")
alignment_model = whisperx.load_align_model(language_code="en", device=device)

# Step 5: Align transcriptions (equivalent to --align_model WAV2VEC2_ASR_LARGE_LV60K_960H)
print_green("Aligning transcription...")
aligned_result = whisperx.align(
    transcription_result["segments"],
    model=alignment_model[0],  # Use the first element of the tuple as the model
    align_model_metadata=alignment_model[1],  # Use the second element as metadata 
    audio=audio_file, 
    device=device
)

# Step 6: Save outputs in all formats
print_green("Saving transcription and alignment results...")

# Save aligned output as JSON
aligned_json_file = f"{output_dir}/timestamps.json"
with open(aligned_json_file, "w") as json_file:
    json.dump(aligned_result, json_file, indent=4)
print_green(f"Aligned JSON saved to: {aligned_json_file}")

# Save aligned output as TXT
aligned_txt_file = f"{output_dir}/timestamps.txt"
with open(aligned_txt_file, "w") as txt_file:
    for segment in aligned_result["segments"]:
        start = segment["start"]
        end = segment["end"]
        text = segment["text"]
        txt_file.write(f"[{start:.2f} - {end:.2f}]: {text}\n")
print_green(f"Aligned TXT saved to: {aligned_txt_file}")


# Save original transcription as TXT
transcription_txt_file = f"{output_dir}/transcription.txt"
with open(transcription_txt_file, "w") as txt_file:
    for segment in transcription_result["segments"]:
        txt_file.write(f"{segment['text']}\n")
print_green(f"Original transcription saved to: {transcription_txt_file}")

# Cleanup: Optional (delete the audio file)
# import os
# os.remove(audio_file)
