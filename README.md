# SpotRAG

**VidQueryRAG** is a Retrieval-Augmented Generation (RAG) powered project designed to summarize or retrieve specific timestamps from videos based on user queries. This tool allows users to easily navigate long videos by pinpointing relevant moments, enhancing productivity and user experience.

---

## Features
- 🚀 **Query-Based Timestamp Retrieval**: Retrieve specific moments in a video based on natural language queries.
- 📝 **Summarization**: Generate concise summaries of video content.
- ⚡ **Efficient Navigation**: Quickly locate relevant video sections without manual scrubbing.
- 🎯 **Powered by RAG**: Combines retrieval techniques with generative AI for accurate results.

---

## Use Cases
- **Educational Content**: Quickly locate key moments in lectures or tutorials.
- **Media Analysis**: Extract timestamps for insights or reporting.
- **Enhanced Productivity**: Navigate lengthy videos with ease.

---

## How It Works
1. **Input a Video**: Upload a video or provide a link.
2. **Query**: Ask a question or provide a keyword to search for.
3. **Result**: Get a timestamp and optionally a summary of the relevant video section.

---

## Setup and Installation
  
### Run the Application
 Download mp4 file using
   https://ytmp3.la/en-UNh4

 Requirements:
  Cuda 11.8

(venv) F:\PHD>dir /b /s cudnn*.dll
 How to start:
   ```bash
   create venv in root dir (imp)
   git clone https://github.com/varenyamnikam/SpotRAG.git
   cd SpotRAG
   pip install -r requirements.txt
   python versions.py (should output true else there are cuda and pytorch incompatibility issues)
   python whisperX.py

