# qa_engine.py
from transformers import pipeline, AutoModelForQuestionAnswering, AutoTokenizer, Trainer, TrainingArguments
from sentence_transformers import SentenceTransformer, util
import json
import torch
import numpy as np
from typing import List, Dict, Tuple
from datasets import Dataset

def find_answers_with_timestamps(
    queries: List[str], 
    file_path: str, 
    qa_model="deepset/roberta-base-squad2", 
    embedder_model="all-mpnet-base-v2", 
    top_k=5, 
    similarity_threshold=0.7, 
    qa_confidence_threshold=0.5, 
    device=0,
    context_size=3
) -> Dict[str, Dict]:
    """
    Find the best answers with timestamps for multiple queries from a transcription dataset.
    
    Args:
        queries (List[str]): List of questions to answer.
        file_path (str): Path to the transcription data (JSON format).
        qa_model (str): Hugging Face QA model or path to fine-tuned model.
        embedder_model (str): SentenceTransformer model for semantic similarity.
        top_k (int): Number of top matches to consider for each query.
        similarity_threshold (float): Minimum similarity score to consider a match valid.
        qa_confidence_threshold (float): Minimum confidence score for the QA model to accept an answer.
        device (int): Device to use (0 for GPU, -1 for CPU).
        context_size (int): Number of segments to include in the context window.
    
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

        # Apply similarity threshold and select top-k most relevant segments
        filtered_indices = [idx for idx, score in enumerate(similarities) if score > similarity_threshold]

        if not filtered_indices:
            results[query] = {"error": "No relevant segments found"}
            continue

        # If we have too many matches, take only the top ones
        if len(filtered_indices) > top_k * 3:  # We'll expand by context_size, so get more initial candidates
            filtered_indices = torch.topk(similarities, k=top_k * 3).indices.tolist()

        # Create expanded contexts by including surrounding segments
        expanded_contexts = []
        for idx in filtered_indices:
            # Calculate the range of indices to include (context_size segments before and after)
            start_idx = max(0, idx - context_size // 2)
            end_idx = min(len(segments) - 1, idx + context_size // 2)
            
            # Combine the segments into a single context
            combined_text = " ".join([segments[j]["text"] for j in range(start_idx, end_idx + 1)])
            start_time = segments[start_idx]["start"]
            end_time = segments[end_idx]["end"]
            
            expanded_contexts.append({
                "text": combined_text,
                "start": start_time,
                "end": end_time,
                "center_idx": idx,
                "similarity": similarities[idx].item()
            })
        
        # Sort by similarity and take the top_k
        expanded_contexts.sort(key=lambda x: x["similarity"], reverse=True)
        top_contexts = expanded_contexts[:top_k]

        # Perform QA on the expanded contexts
        answers = []
        for context in top_contexts:
            # Check if the context is too long for the model
            if len(context["text"].split()) > 500:  # Arbitrary threshold, adjust as needed
                # If too long, truncate from both ends to keep the most relevant part
                words = context["text"].split()
                truncated_context = " ".join(words[:250] + words[-250:])
            else:
                truncated_context = context["text"]
                
            result = qa_pipeline({
                "context": truncated_context,
                "question": query
            })

            # Calculate answer-query relevance for additional filtering
            answer_embedding = embedder.encode(result["answer"], convert_to_tensor=True)
            answer_relevance = util.cos_sim(query_embeddings[i], answer_embedding).item()

            # Only keep results with high confidence and relevance
            if result["score"] >= qa_confidence_threshold and answer_relevance > similarity_threshold * 0.8:
                answers.append({
                    "text": context["text"],
                    "answer": result["answer"],
                    "score": result["score"] * (1 + answer_relevance),  # Boost score based on relevance
                    "start": context["start"],
                    "end": context["end"]
                })

        # Find the best answer based on combined confidence score
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

def fine_tune_qa_model(
    training_data_path: str,
    output_model_path: str = "fine_tuned_qa_model",
    base_model: str = "deepset/roberta-base-squad2",
    epochs: int = 3
):
    """
    Fine-tune a QA model on domain-specific data.
    
    Args:
        training_data_path (str): Path to the training data JSON file.
        output_model_path (str): Path to save the fine-tuned model.
        base_model (str): Base model to fine-tune.
        epochs (int): Number of training epochs.
        
    Returns:
        dict: Training metrics.
    """
    # Load training data
    with open(training_data_path, "r") as f:
        training_data = json.load(f)
    
    # Convert to datasets format
    train_dataset = Dataset.from_list(training_data)
    
    # Load model and tokenizer
    model = AutoModelForQuestionAnswering.from_pretrained(base_model)
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    
    # Tokenize dataset
    def preprocess_function(examples):
        questions = [q for q in examples["question"]]
        contexts = [c for c in examples["context"]]
        
        inputs = tokenizer(
            questions,
            contexts,
            max_length=384,
            truncation="only_second",
            stride=128,
            return_overflowing_tokens=True,
            return_offsets_mapping=True,
            padding="max_length",
        )
        
        # Find the start and end positions of the answers
        start_positions = []
        end_positions = []
        
        for i, context in enumerate(contexts):
            answer = examples["answer"][i]
            answer_start = context.find(answer)
            answer_end = answer_start + len(answer)
            
            # Convert character positions to token positions
            start_token = None
            end_token = None
            
            for j, (offset_start, offset_end) in enumerate(inputs.offset_mapping[i]):
                if offset_start <= answer_start < offset_end:
                    start_token = j
                if offset_start <= answer_end <= offset_end:
                    end_token = j
            
            # If we couldn't find proper token indices, use defaults
            if start_token is None:
                start_token = 0
            if end_token is None:
                end_token = 0
                
            start_positions.append(start_token)
            end_positions.append(end_token)
        
        inputs["start_positions"] = start_positions
        inputs["end_positions"] = end_positions
        return inputs
    
    tokenized_train_dataset = train_dataset.map(
        preprocess_function, 
        batched=True,
        remove_columns=train_dataset.column_names
    )
    
    # Define training arguments
    training_args = TrainingArguments(
        output_dir=output_model_path,
        per_device_train_batch_size=8,
        num_train_epochs=epochs,
        save_strategy="epoch",
        learning_rate=3e-5,
        weight_decay=0.01,
    )
    
    # Define trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train_dataset
    )
    
    # Train the model
    trainer.train()
    
    # Save the model
    model.save_pretrained(output_model_path)
    tokenizer.save_pretrained(output_model_path)
    
    return {
        "base_model": base_model,
        "training_examples": len(training_data),
        "epochs": epochs
    }