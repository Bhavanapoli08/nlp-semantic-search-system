import faiss
import pickle
import numpy as np
import re
from collections import Counter

from sentence_transformers import SentenceTransformer
from MLModels.models import (
    get_embedding_query_model,
)

model = get_embedding_query_model()


# ---------------------------------------------------
# Utility: truncate text nicely
# ---------------------------------------------------
def truncate_to_sentences(text, max_chars=350, min_sentences=1):

    if not text:
        return ""

    sentences = re.split(r"(?<=[.!?])\s+", text.strip())

    out = ""
    count = 0

    for s in sentences:

        if not s.strip():
            continue

        if len(out) + len(s) <= max_chars or count < min_sentences:
            out += s.strip() + " "
            count += 1
        else:
            break

    return out.strip()


# ---------------------------------------------------
# Intelligent section boosting
# ---------------------------------------------------
def boost_section_score(query: str, section_name: str, score: float):

    query = query.lower()
    section_name = section_name.lower()
    asks_references = any(
        word in query
        for word in ["reference", "references", "bibliography", "citation", "citations"]
    )

    if ("reference" in section_name or "bibliography" in section_name) and not asks_references:
        score -= 8.0

    section_boost = {
        "summary": ["abstract", "summary"],
        "abstract": ["abstract"],
        "introduction": ["introduction", "background"],
        "method": ["method", "methodology", "approach", "architecture", "training", "framework"],
        "approach": ["method", "methodology", "approach", "architecture", "training", "framework"],
        "architecture": ["method", "methodology", "architecture", "approach", "training"],
        "training": ["training", "method", "approach", "methodology"],
        "dataset": ["dataset", "data", "datasets", "corpus", "repository", "benchmark", "experiment"],
        "data": ["data", "dataset", "datasets", "corpus", "repository", "benchmark"],
        "result": ["results", "experiment", "evaluation", "analysis"],
        "accuracy": ["results", "accuracy", "performance", "analysis"],
        "performance": ["results", "performance", "evaluation", "analysis"],
        "conclusion": ["conclusion", "future work", "discussion"],
        "future": ["future work", "conclusion", "discussion"],
        "related": ["related work", "literature", "comparison"],
        "comparison": ["related work", "comparison", "results"],
        "reference": ["references", "bibliography"],
        "citation": ["references", "bibliography"],
        "author": ["references", "bibliography"],
        "limitation": ["discussion", "conclusion", "limitations"],
        "discussion": ["discussion", "conclusion", "limitations"],
        "experiment": ["experiments", "results", "evaluation"],
    }

    for qword, targets in section_boost.items():
        if qword in query:
            for target in targets:
                if target in section_name:
                    score += 1.0

    return score


# ---------------------------------------------------
# Keyword extraction
# ---------------------------------------------------
def _keywords(text: str) -> set[str]:

    stopwords = {
        "a", "an", "and", "are", "as", "at", "be", "by", "for",
        "from", "how", "in", "is", "it", "of", "on", "or",
        "paper", "that", "the", "this", "to", "used", "uses",
        "what", "which", "with", "tell", "about", "give", "show",
        "find", "research", "classification",
    }

    return {
        token
        for token in re.findall(r"[a-zA-Z][a-zA-Z0-9-]{2,}", text.lower())
        if token not in stopwords
    }


# ---------------------------------------------------
# Question intent classification
# ---------------------------------------------------

def _question_intents(question: str) -> set[str]:
    text = question.lower()
    intents = set()

    if any(word in text for word in ["methodology", "method", "approach", "algorithm", "framework", "pipeline", "training", "architecture"]):
        intents.add("method")

    if any(word in text for word in ["dataset", "data set", "data used", "repository", "uci", "database", "corpus", "samples"]):
        intents.add("dataset")

    if any(word in text for word in ["accuracy", "performance", "result", "results", "score", "precision", "recall", "f1", "roc"]):
        intents.add("result")

    if any(word in text for word in ["limitation", "limitations", "challenge", "challenges", "draw accurate", "shortcoming", "weakness", "constraint"]):
        intents.add("limitations")

    if any(word in text for word in ["contribution", "contributions", "key role", "novel", "significant", "impact", "benefit"]):
        intents.add("contribution")

    if any(word in text for word in ["reference", "references", "bibliography", "citation", "citations", "author", "authors"]):
        intents.add("reference")

    if any(word in text for word in ["conclusion", "future work", "discussion"]):
        intents.add("conclusion")

    if not intents:
        intents.add("general")

    return intents


def _is_prior_work_sentence(sentence: str) -> bool:
    if re.search(r"\b(paper|study|work|research|experiment)\s*\[\d+\]", sentence):
        return True
    if re.search(r"\bet al\b", sentence):
        return True
    if re.search(r"\baccording to\b|\bprevious\b|\bprior\b|\breported\b|\bcited\b|\bfrom \[\d+\]\b", sentence):
        return True
    if re.search(r"\bpaper\s*\d+\b|\bstudy\s*\d+\b", sentence):
        return True
    if re.search(r"\[\d+\]", sentence) and not re.search(r"\btable\b|\bfigure\b", sentence):
        return True
    return False


# ---------------------------------------------------
# Sentence scoring
# ---------------------------------------------------

def _sentence_score(
    question_terms: set[str],
    question: str,
    section_name: str,
    sentence: str,
) -> float:

    sentence_lower = sentence.lower()
    sentence_terms = _keywords(sentence)
    section_lower = section_name.lower()
    question_lower = question.lower()
    intents = _question_intents(question)

    overlap = question_terms & sentence_terms
    score = len(overlap) * 4.0

    if question_terms:
        score += len(overlap) / len(question_terms)

    asks_references = any(
        word in question_lower
        for word in ["reference", "references", "bibliography", "citation", "citations"]
    )

    if ("reference" in section_lower or "bibliography" in section_lower) and not asks_references:
        score -= 10.0

    is_prior_work = _is_prior_work_sentence(sentence_lower)
    if any(word in sentence_lower for word in ["we ", "our ", "this paper", "this study", "proposed", "we have", "we used", "we used"]):
        score += 4.0

    if "dataset" in intents:
        if any(word in sentence_lower for word in ["dataset", "data set", "data used", "uci", "repository", "database", "benchmarks", "benchmark"]):
            score += 10.0
        if "dataset" in section_lower or "data" in section_lower or "experiment" in section_lower:
            score += 4.0
        if is_prior_work:
            score -= 8.0

    if "method" in intents:
        if any(word in sentence_lower for word in ["method", "methodology", "approach", "algorithm", "pipeline", "framework", "model", "architecture", "training", "learning", "data mining"]):
            score += 10.0
        if any(word in sentence_lower for word in ["naïve bayes", "naive bayes", "k nearest", "knn", "decision tree", "random forest", "artificial neural network", "ann", "svm"]):
            score += 12.0
        if any(word in section_lower for word in ["method", "methodology", "approach", "architecture", "training"]):
            score += 4.0
        if is_prior_work:
            score -= 8.0

    if "result" in intents:
        if any(word in sentence_lower for word in ["accuracy", "%", "performance", "precision", "recall", "f1", "roc", "best accuracy", "highest accuracy", "achieved"]):
            score += 12.0
        if re.search(r"\b\d+(?:\.\d+)?\s*%", sentence_lower) or re.search(r"\b\d+\.\d+\b", sentence_lower):
            score += 22.0
        if any(word in section_lower for word in ["result", "results", "experiment", "evaluation", "analysis"]):
            score += 4.0
        if is_prior_work:
            score -= 20.0

    if "limitations" in intents:
        if any(word in sentence_lower for word in ["limitation", "limitations", "challenge", "challenges", "problem", "not satisfactory", "cannot", "unable", "draw accurate"]):
            score += 12.0
        if any(word in section_lower for word in ["discussion", "conclusion", "limitations"]):
            score += 4.0
        if is_prior_work:
            score -= 8.0

    if "contribution" in intents:
        if any(word in sentence_lower for word in ["key role", "contribute", "contribution", "provide", "help", "improve", "enable", "support"]):
            score += 10.0
        if any(word in section_lower for word in ["introduction", "abstract", "conclusion"]):
            score += 3.0
        if is_prior_work:
            score -= 8.0

    if "reference" in intents or "author" in question_lower:
        if any(word in section_lower for word in ["reference", "bibliography"]):
            score += 18.0
        if re.search(r"\[\d+\]|\bet al\b|\bdoi\b|\bhttp[s]?://\b", sentence_lower):
            score += 8.0

    if "conclusion" in intents:
        if any(word in section_lower for word in ["conclusion", "future work", "discussion"]):
            score += 10.0

    if "classification" in question_lower:
        if any(word in sentence_lower for word in ["classifier", "classification", "classif", "model", "predict"]):
            score += 5.0

    if "transformer" in question_lower and ("transformer" in sentence_lower or "vit" in sentence_lower):
        score += 5.0

    if "cancer" in question_lower and "cancer" in sentence_lower:
        score += 3.0

    length = len(sentence)
    if 50 <= length <= 250:
        score += 3.0
    elif length > 700:
        score -= 2.0

    return score


def _clean_sentence(sentence: str) -> str:
    sentence = " ".join(sentence.split())
    sentence = re.sub(r"^\[\d+\]\s*", "", sentence)
    return sentence.strip()


def _candidate_section_name(section_name: str, sentence: str) -> str:
    match = re.match(
        r"^(methodology|methods?|dataset|results?|conclusion|references?)\s*:",
        sentence,
        flags=re.IGNORECASE,
    )
    if match:
        label = match.group(1).upper()
        return "METHOD" if label.startswith("METHOD") else label.rstrip("S")
    return section_name


# ---------------------------------------------------
# Answer extraction
# ---------------------------------------------------
def answer_from_paper_detailed(question: str, sections: list[dict], top_k: int = 2):

    if not sections:
        return {
            "answer": "",
            "section": "",
            "confidence": 0,
            "sources": [],
        }

    question_terms = _keywords(question)

    candidates = []
    seen_sentences = set()

    for section in sections:

        section_name = (
            section.get("section_name")
            or section.get("name")
            or "Unknown"
        )

        text = section.get("text", "") or ""

        sentences = re.split(r"(?<=[.!?])\s+", text)

        for sentence in sentences:

            sentence = _clean_sentence(sentence)

            if len(sentence) < 25:
                continue

            sentence_key = re.sub(r"[^a-z0-9]+", " ", sentence.lower()).strip()
            if sentence_key in seen_sentences:
                continue
            seen_sentences.add(sentence_key)

            score = _sentence_score(
                question_terms,
                question,
                section_name,
                sentence,
            )

            score = boost_section_score(
                question,
                section_name,
                score,
            )

            candidates.append((score, _candidate_section_name(section_name, sentence), sentence))

    if not candidates:
        return {
            "answer": "",
            "section": "",
            "confidence": 0,
            "sources": [],
        }

    candidates.sort(
        key=lambda item: item[0],
        reverse=True
    )

    max_score = max(candidates[0][0], 1)

    if candidates[0][0] < 4.0:
        return {
            "answer": "",
            "section": "",
            "confidence": 0,
            "sources": [],
        }

    min_related_score = max(4.0, candidates[0][0] * 0.45)
    best = [candidate for candidate in candidates if candidate[0] >= min_related_score][:top_k]

    dominant_section = Counter(
        section_name for _, section_name, _ in best
    ).most_common(1)[0][0]

    answer = " ".join(sentence for _, _, sentence in best)
    confidence = max(35, min(98, round((best[0][0] / (max_score + 4)) * 100)))
    sources = [
        {
            "section": section_name,
            "page": None,
            "confidence": max(20, min(98, round((score / (max_score + 4)) * 100))),
            "snippet": truncate_to_sentences(sentence, max_chars=220, min_sentences=1),
        }
        for score, section_name, sentence in best
    ]

    return {
        "answer": truncate_to_sentences(answer, max_chars=650, min_sentences=1),
        "section": dominant_section,
        "confidence": confidence,
        "sources": sources,
    }


def answer_from_paper(question: str, sections: list[dict], top_k: int = 1):
    result = answer_from_paper_detailed(question, sections, top_k=top_k)

    return (
        result["answer"],
        result["section"],
    )


# ---------------------------------------------------
# Main semantic retrieval
# ---------------------------------------------------
def unified_search(
    query: str,
    faiss_global_idx=None,
    metadata=None,
    faiss_section_idx=None,
    section_metadata=None,
    top_k_sections: int = 5,
    top_k_papers: int = 3,
    cosine_threshold: float = 0.35,
):

    try:

        sec_idx = faiss_section_idx
        sec_meta = section_metadata

        glob_idx = faiss_global_idx
        glob_meta = metadata

    except Exception as e:

        print("Error loading indexes:", e)

        return [], []

    qvec = model.encode(
        [query],
        convert_to_numpy=True
    ).astype("float32")

    qvec = qvec / np.linalg.norm(qvec)

    # ---------------------------------------------------
    # SECTION SEARCH
    # ---------------------------------------------------
    D_sec, I_sec = sec_idx.search(
        qvec,
        top_k_sections
    )

    ranked_sections = []

    for rank, idx in enumerate(I_sec[0]):

        cos_sim = float(D_sec[0][rank])

        meta = sec_meta[idx]

        section_name = meta.get(
            "section_name",
            "Unknown"
        )

        boosted_score = boost_section_score(
            query,
            section_name,
            cos_sim
        )

        if boosted_score < cosine_threshold:
            continue

        section_text = meta.get("section_text", "") or ""
        answer_result = answer_from_paper_detailed(
            query,
            [{"section_name": section_name, "text": section_text}],
            top_k=1,
        )
        section_answer = answer_result.get("answer") or truncate_to_sentences(section_text, max_chars=700)

        ranked_sections.append({

            "rank": rank + 1,
            "type": "section",

            "title": meta.get(
                "title",
                "Unknown"
            ),

            "section_name": section_name,

            "text": section_answer,

            "score": boosted_score,
        })

    ranked_sections = sorted(
        ranked_sections,
        key=lambda x: x["score"],
        reverse=True
    )

    best_section = (
        ranked_sections[0]
        if ranked_sections
        else None
    )

    # ---------------------------------------------------
    # PAPER SEARCH
    # ---------------------------------------------------
    paper_results = []

    if best_section:

        D_glob, I_glob = glob_idx.search(
            qvec,
            top_k_papers
        )

        for rank, idx in enumerate(
            I_glob[0],
            start=1
        ):

            cos_sim = float(
                D_glob[0][rank - 1]
            )

            if cos_sim < cosine_threshold:
                continue

            meta = glob_meta[idx]

            paper_results.append({

                "rank": rank,
                "type": "paper",

                "title": meta.get(
                    "title",
                    "Unknown"
                ),

                "authors": ", ".join(
                    meta.get("authors", [])
                ),

                "summary": truncate_to_sentences(
                    meta.get("summary", "")
                ),

                "score": cos_sim,
            })

    # ---------------------------------------------------
    # REMOVE DUPLICATES
    # ---------------------------------------------------
    unique_titles = set()

    filtered_papers = []

    for paper in paper_results:

        if paper["title"] not in unique_titles:

            filtered_papers.append(paper)

            unique_titles.add(
                paper["title"]
            )

    return (
        [best_section] if best_section else [],
        filtered_papers
    )
