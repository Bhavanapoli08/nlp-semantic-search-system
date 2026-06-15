import faiss
import numpy as np
import pickle

def append_embeddings_to_faiss(
    new_paper_embeddings,
    global_idx_path,
    metadata_pkl_path,
    section_idx_path,
    section_pkl_path,
):
    # Load existing indexes
    global_index = faiss.read_index(global_idx_path)
    with open(metadata_pkl_path, "rb") as f:
        global_metadata = pickle.load(f)

    section_index = faiss.read_index(section_idx_path)
    with open(section_pkl_path, "rb") as f:
        section_metadata = pickle.load(f)

    # -------- GLOBAL EMBEDDINGS --------
    for paper in new_paper_embeddings:
        if paper is None or "global_embedding" not in paper:
            print("⚠️ Skipping invalid paper (no global embedding)")
            continue

        vec = np.array(paper["global_embedding"], dtype=np.float32).reshape(1, -1)
        global_index.add(vec)

        global_metadata.append({
            "title": paper.get("name", "Unknown"),
            "authors": [
                a.get("name") for a in paper.get("author", [])
                if isinstance(a, dict)
            ],
            "summary": paper.get("global_summary", ""),
        })

    # -------- SECTION EMBEDDINGS --------
    for paper in new_paper_embeddings:
        if paper is None:
            continue

        title = paper.get("name", "")
        bodies = paper.get("articleBody", [])
        embs = paper.get("embeddings", [])

        if not bodies or not embs:
            print(f"⚠️ Skipping sections for {title} (missing data)")
            continue

        for sec_dict, sec_emb in zip(bodies, embs):
            if not isinstance(sec_dict, dict) or len(sec_dict) != 1:
                continue

            sec_name = next(iter(sec_dict))
            sec_text = sec_dict[sec_name]

            try:
                vec = np.array(sec_emb, dtype=np.float32).reshape(1, -1)
                section_index.add(vec)

                section_metadata.append({
                    "title": title,
                    "section_name": sec_name,
                    "section_text": sec_text,
                })

            except Exception as e:
                print(f"⚠️ Error adding section: {e}")
                continue

    return global_index, global_metadata, section_index, section_metadata