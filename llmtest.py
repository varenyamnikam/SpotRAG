from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
import json
import torch
from typing import List, Dict

def find_answers_with_timestamps(queries: List[str], file_path: str, qa_model="deepset/roberta-base-squad2", embedder_model="all-MiniLM-L6-v2", top_k=3, device=0) -> Dict[str, Dict]:
    """
    Find the best answers with timestamps for multiple queries from a transcription dataset.
    
    Args:
        queries (List[str]): List of questions to answer.
        file_path (str): Path to the transcription data (JSON format).
        qa_model (str): Hugging Face QA model.
        embedder_model (str): SentenceTransformer model for semantic similarity.
        top_k (int): Number of top matches to consider for each query.
        device (int): Device to use (0 for GPU, -1 for CPU).
    
    Returns:
        Dict[str, Dict]: Dictionary with each query's best answer, timestamp, and context.
    """
    # Load the QA pipeline
    qa_pipeline = pipeline(
        "question-answering",
        model=qa_model,
        tokenizer=qa_model,
        device=device
    )

    # Load the Sentence Transformer embedder
    embedder = SentenceTransformer(embedder_model)

    # Load transcription data
    with open(file_path, "r") as json_file:
        transcription_data = json.load(json_file)

    # Extract segments
    segments = [{"text": seg["text"], "start": seg["start"], "end": seg["end"]} for seg in transcription_data]

    # Compute embeddings for all segments (Corpus Embedding)
    corpus_texts = [seg["text"] for seg in segments]
    corpus_embeddings = embedder.encode(corpus_texts, convert_to_tensor=True)

    # Embed all queries at once (Batch Query Embedding)
    query_embeddings = embedder.encode(queries, convert_to_tensor=True)

    results = {}

    for i, query in enumerate(queries):
        # Compute similarity scores for the current query
        similarities = util.cos_sim(query_embeddings[i], corpus_embeddings).squeeze(0)

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

        # Find the best answer based on confidence score
        if answers:
            best_answer = max(answers, key=lambda x: x["score"])
            results[query] = {
                "answer": best_answer['answer'],
                "timestamp": f"{best_answer['start']} - {best_answer['end']}",
                "context": best_answer['text']
            }
        else:
            results[query] = {"error": "No valid answers found"}

    return results

# Example Usage
# queries = ["When does the speaker introduce histograms?", "What is the importance of natural light exposure?"]
# file_path = "timestamps.json"
# results = find_answers_with_timestamps(queries, file_path)

# for query, result in results.items():
#     print(f"Query: {query}")
#     if "error" in result:
#         print(f"Error: {result['error']}")
#     else:
#         print(f"Answer: {result['answer']}")
#         print(f"Timestamp: {result['timestamp']}")
#         print(f"Context: {result['context']}")
#     print("-" * 80)
