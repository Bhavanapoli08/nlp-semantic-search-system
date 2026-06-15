import numpy as np
from MLModels.models import get_embedding_query_model


# ---------------------------------------------------
# Generate embeddings for paper
# ---------------------------------------------------

def add_embeddings(paper_json):

    model = get_embedding_query_model()

    processed_paper = paper_json.copy()

    # ---------------------------------------------------
    # Extract metadata
    # ---------------------------------------------------

    title = paper_json.get("name", "")

    authors = ", ".join([
        a.get("name", "")
        for a in paper_json.get("author", [])
    ])

    summaries = "\n".join(
        paper_json.get("summaries", {}).values()
    )

    global_summary = paper_json.get(
        "global_summary",
        ""
    )

    # ---------------------------------------------------
    # Build section-aware embeddings
    # ---------------------------------------------------

    sections = []

    for section in paper_json.get("articleBody", []):

        if not section:
            continue

        # Example:
        # {"RESULTS": "..."}
        section_name = list(section.keys())[0]

        section_text = list(section.values())[0]

        if section_text is None:
            section_text = ""

        # IMPORTANT:
        # Include section title inside embedding text
        enriched_text = f"""
SECTION: {section_name}

{section_text}
"""

        sections.append(enriched_text)

    # ---------------------------------------------------
    # Global paper embedding text
    # ---------------------------------------------------

    global_text = "\n".join([
        title,
        authors,
        summaries,
        global_summary,
    ] + sections)

    # ---------------------------------------------------
    # Generate section embeddings
    # ---------------------------------------------------

    section_embeddings = model.encode(
        sections,
        convert_to_numpy=True
    )

    # Normalize section embeddings
    section_embeddings = (
        section_embeddings /
        np.linalg.norm(
            section_embeddings,
            axis=1,
            keepdims=True
        )
    )

    # ---------------------------------------------------
    # Generate global embedding
    # ---------------------------------------------------

    global_embedding = model.encode(
        global_text,
        convert_to_numpy=True
    )

    # Normalize global embedding
    global_embedding = (
        global_embedding /
        np.linalg.norm(global_embedding)
    )

    # ---------------------------------------------------
    # Store embeddings
    # ---------------------------------------------------

    processed_paper["embeddings"] = (
        section_embeddings.tolist()
    )

    processed_paper["global_embedding"] = (
        global_embedding.tolist()
    )

    return processed_paper