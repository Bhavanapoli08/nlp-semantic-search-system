from functools import lru_cache

from transformers import pipeline
from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=1)
def get_embedding_query_model():
    """
    Loads the SentenceTransformer model for encoding queries.
    Caches the model to avoid reloading it on every query.
    """
    return SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2", device="cpu")


@lru_cache(maxsize=1)
def get_qa_embedding_model():
    """
    Loads a sentence-transformer trained for question-answer retrieval.
    Used by /upload/ask to rank sentences against a question.
    """
    return SentenceTransformer("multi-qa-MiniLM-L6-cos-v1", device="cpu")


@lru_cache(maxsize=1)
def get_classifier():
    """
    Loads the zero-shot classification model for detecting academic queries.
    Caches the model to avoid reloading it on every query.
    """
    return pipeline("zero-shot-classification", model="facebook/bart-large-mnli")


@lru_cache(maxsize=2)
def get_summarizer(lang="en"):
    """
    Loads the summarization model based on the specified language.
    Caches the model to avoid reloading it on every request.
    """
    if lang == "en":
        return pipeline("summarization", model="facebook/bart-large-cnn")
    else:
        # Note: Ensure the model supports the desired language(For this project it support swedish that's why I use it)
        return pipeline(
            "summarization", model="facebook/mbart-large-50-many-to-many-mmt"
        )
        
  
