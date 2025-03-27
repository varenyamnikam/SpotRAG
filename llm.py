from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
import json
import os
import torch

# Global variable to store the cached transcription data
_TRANSCRIPTION_CACHE = {
    'file_path': None,
    'data': None,
    'mtime': None
}

def load_transcription_data(file_path):
    """
    Load transcription data with file modification time check.
    Caches the data to avoid repeated file reads.
    
    Args:
        file_path (str): Path to the JSON transcription file
    
    Returns:
        list: Transcription data
    """
    # Check if file path is the same and modification time hasn't changed
    current_mtime = os.path.getmtime(file_path)
    
    if (file_path == _TRANSCRIPTION_CACHE['file_path'] and 
        current_mtime == _TRANSCRIPTION_CACHE['mtime']):
        return _TRANSCRIPTION_CACHE['data']
    
    # Load new data
    with open(file_path, "r") as json_file:
        transcription_data = json.load(json_file)
    
    # Update cache
    _TRANSCRIPTION_CACHE['file_path'] = file_path
    _TRANSCRIPTION_CACHE['data'] = transcription_data
    _TRANSCRIPTION_CACHE['mtime'] = current_mtime
    
    return transcription_data

def find_answer_with_timestamp(query, file_path, qa_model="bert-large-uncased-whole-word-masking-finetuned-squad", embedder_model="all-MiniLM-L6-v2", top_k=3, device=0):
    """
    Find the best answer with a timestamp from a transcription dataset.
    
    Args:
        query (str): The question to answer.
        file_path (str): Path to the transcription data (JSON format).
        qa_model (str): Hugging Face QA model.
        embedder_model (str): SentenceTransformer model for semantic similarity.
        top_k (int): Number of top matches to consider.
        device (int): Device to use (0 for GPU, -1 for CPU).
    
    Returns:
        dict: Best answer with associated metadata.
    """
    try:
        # Load the QA pipeline
        qa_pipeline = pipeline(
            "question-answering",
            model=qa_model,
            tokenizer=qa_model,
            device=device
        )

        # Load the Sentence Transformer embedder
        embedder = SentenceTransformer(embedder_model)

        # Load transcription data using the caching mechanism
        transcription_data = load_transcription_data(file_path)

        # Extract segments
        segments = [{"text": seg["text"], "start": seg["start"], "end": seg["end"]} for seg in transcription_data]

        # Compute embeddings for all segments
        corpus_embeddings = embedder.encode([seg["text"] for seg in segments], convert_to_tensor=True)

        # Embed the query
        query_embedding = embedder.encode(query, convert_to_tensor=True)

        # Compute similarity scores
        similarities = util.cos_sim(query_embedding, corpus_embeddings).squeeze(0)

        # Select top-k most similar segments
        top_indices = torch.topk(similarities, k=top_k).indices.tolist()

        # Perform QA on the top-k segments
        answers = []
        for idx in top_indices:
            seg = segments[idx]
            result = qa_pipeline({
                "context": seg["text"],
                "question": query
            })
            answers.append({
                "text": seg["text"],
                "answer": result["answer"],
                "score": result["score"],
                "start": seg["start"],
                "end": seg["end"]
            })

        # Find the best answer
        if answers:
            best_answer = max(answers, key=lambda x: x["score"])
            return {
                "query": query,
                "answer": best_answer['answer'],
                "timestamp": f"{best_answer['start']} - {best_answer['end']}",
                "timestampstart": best_answer['start'],
                "timestampend": best_answer['end'],
                "context": best_answer['text']
            }
        else:
            return {"error": "No valid answers found"}

    except Exception as e:
        return {"error": str(e)}

# Example Usage
if __name__ == "__main__":
    query = "When does the speaker introduce histograms?"
    file_path = "timestamps.json"
    result = find_answer_with_timestamp(query, file_path)

    if "error" in result:
        print(result["error"])
    else:
        print(f"Query: {query}")
        print(f"Answer: {result['answer']}")
        print(f"Timestamp: {result['timestamp']}")
        print(f"Context: {result['context']}")