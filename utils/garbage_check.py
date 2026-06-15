#from transformers import pipeline
import streamlit as st
from MLModels.models import get_classifier

# 1) Load the same BART-MNLI zero-shot pipeline

classifier = get_classifier()

def is_academic_query(query: str, threshold: float = 0.85) -> bool:
    """
    Returns True if the zero-shot classifier thinks `query` is more like an 'academic question'
    than 'trolling or off-topic', with probability >= threshold.
    """
    if not query.strip():
        return False

    # Feed the query into the NLI model with new candidate labels
    result = classifier(
        sequences=query,
        candidate_labels=["academic question", "trolling or off-topic"],
        multi_label=False
    )
  

    labels = result["labels"]
    scores = result["scores"]
    # Look up the probability for "academic question"
    try:
        acad_score = scores[labels.index("academic question")]
    except ValueError:
        # In case the order is different or label missing
        acad_score = 0.0
    print(f"score: {acad_score}")
    return acad_score >= threshold
