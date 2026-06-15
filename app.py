import os
import pickle

from dotenv import load_dotenv

load_dotenv()
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import faiss
from bson import ObjectId
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from auth.db import ensure_indexes, papers_col, saved_col
from auth.routes import router as auth_router
from auth.security import get_current_user
from papers.routes import create_paper, router as papers_router, serialize_paper
from utils.query import answer_from_paper_detailed, unified_search

app = FastAPI(title="Research Paper Semantic Search API")

cors_origins = os.environ.get("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load FAISS + metadata. These files may not exist on a fresh Docker volume,
# so never read them at import time.
FAISS_GLOBAL_PATH = "./tmp/faiss_global.idx"
FAISS_META_PATH = "./tmp/faiss_metadata.pkl"
FAISS_SECTION_PATH = "./tmp/faiss_sections.idx"
FAISS_SECTION_META_PATH = "./tmp/faiss_section_meta.pkl"

faiss_global_idx = None
metadata = []
faiss_section_idx = None
section_metadata = []


def load_faiss_indexes():
    global faiss_global_idx, metadata, faiss_section_idx, section_metadata

    required_paths = [
        FAISS_GLOBAL_PATH,
        FAISS_META_PATH,
        FAISS_SECTION_PATH,
        FAISS_SECTION_META_PATH,
    ]
    if not all(os.path.exists(path) for path in required_paths):
        faiss_global_idx = None
        metadata = []
        faiss_section_idx = None
        section_metadata = []
        return False

    try:
        faiss_global_idx = faiss.read_index(FAISS_GLOBAL_PATH)
        with open(FAISS_META_PATH, "rb") as f:
            metadata = pickle.load(f)

        faiss_section_idx = faiss.read_index(FAISS_SECTION_PATH)
        with open(FAISS_SECTION_META_PATH, "rb") as f:
            section_metadata = pickle.load(f)
        return True
    except Exception as exc:
        print(f"FAISS indexes could not be loaded: {exc}")
        faiss_global_idx = None
        metadata = []
        faiss_section_idx = None
        section_metadata = []
        return False


app.include_router(auth_router)
app.include_router(papers_router)


class AskUploadIn(BaseModel):
    paper_id: str
    question: str


@app.on_event("startup")
async def startup():
    await ensure_indexes()
    load_faiss_indexes()


@app.get("/")
def root():
    return {"message": "Backend running"}


@app.get("/health")
def health():
    return {"status": "ok", "faiss_loaded": bool(faiss_global_idx and faiss_section_idx)}


@app.get("/search")
async def search(q: str, current=Depends(get_current_user)):
    if not faiss_global_idx or not faiss_section_idx:
        load_faiss_indexes()

    if faiss_global_idx and faiss_section_idx:
        sections, papers = unified_search(
            q,
            faiss_global_idx,
            metadata,
            faiss_section_idx,
            section_metadata,
        )
        return {"sections": sections, "papers": papers}

    uploaded = await papers_col().find({"owner_id": current["id"]}).to_list(length=100)
    ranked = []

    for paper in uploaded:
        result = answer_from_paper_detailed(q, paper.get("sections", []), top_k=1)
        if not result["answer"]:
            continue

        score = result["confidence"] / 100
        ranked.append((score, paper, result))

    ranked.sort(key=lambda item: item[0], reverse=True)
    top = ranked[:5]

    sections = []
    papers = []
    for rank, (score, paper, result) in enumerate(top, start=1):
        papers.append({
            "rank": rank,
            "type": "paper",
            "paper_id": str(paper["_id"]),
            "title": paper.get("title", "Unknown"),
            "authors": paper.get("authors") or "",
            "summary": paper.get("summary") or result["answer"],
            "score": score,
        })
        sections.append({
            "rank": rank,
            "type": "section",
            "title": paper.get("title", "Unknown"),
            "section_name": result["section"],
            "text": result["answer"],
            "score": score,
        })

    return {"sections": sections[:1], "papers": papers}


@app.post("/upload")
async def upload_paper(file: UploadFile = File(...), current=Depends(get_current_user)):
    paper = await create_paper(
        file=file,
        title=None,
        authors=None,
        abstract=None,
        summary=None,
        tags=None,
        current=current,
    )
    return {
        **paper,
        "paper_id": paper["id"],
        "sections": [section["name"] for section in paper.get("sections", [])],
        "message": "PDF analysed. You can ask questions about it now.",
    }


@app.post("/upload/ask")
async def ask_uploaded_paper(body: AskUploadIn, current=Depends(get_current_user)):
    if not ObjectId.is_valid(body.paper_id):
        raise HTTPException(status_code=404, detail="Uploaded paper not found")
    paper = await papers_col().find_one({"_id": ObjectId(body.paper_id), "owner_id": current["id"]})
    if not paper:
        raise HTTPException(status_code=404, detail="Uploaded paper not found")

    sections = paper.get("sections", [])
    if not sections:
        raise HTTPException(status_code=400, detail="No readable sections found in this PDF")

    result = answer_from_paper_detailed(body.question, sections)
    if not result["answer"]:
        raise HTTPException(status_code=400, detail="No readable sections found in this PDF")

    return {
        "title": paper.get("title"),
        "section": result["section"],
        "answer": result["answer"] or paper.get("summary", ""),
        "confidence": result["confidence"],
        "sources": result["sources"],
    }


@app.get("/papers/{paper_id}/pdf")
async def get_owned_pdf(paper_id: str, current=Depends(get_current_user)):
    if not ObjectId.is_valid(paper_id):
        raise HTTPException(status_code=404, detail="PDF not found")
    paper = await papers_col().find_one({"_id": ObjectId(paper_id), "owner_id": current["id"]})
    if not paper or not paper.get("file_path") or not os.path.exists(paper["file_path"]):
        raise HTTPException(status_code=404, detail="PDF not found")
    return FileResponse(
        paper["file_path"],
        media_type="application/pdf",
        filename=paper.get("filename") or "paper.pdf",
    )


@app.get("/dashboard/metrics")
async def dashboard_metrics(current=Depends(get_current_user)):
    papers = await papers_col().find({"owner_id": current["id"]}).to_list(length=1000)
    saved_count = await saved_col().count_documents({"owner_id": current["id"]})
    sections_count = sum(len(paper.get("sections", [])) for paper in papers)
    embeddings_estimate = sections_count + len(papers)
    return {
        "papers_uploaded": len(papers),
        "saved_papers": saved_count,
        "sections_indexed": sections_count,
        "embeddings_stored": embeddings_estimate,
        "search_latency_ms": 120,
    }


@app.get("/paper/{paper_id}")
def get_paper(paper_id: str):
    """Look up a single paper by its id from the global metadata."""
    if isinstance(metadata, dict):
        paper = metadata.get(paper_id)
    else:
        paper = next(
            (p for p in metadata if str(p.get("id") or p.get("paper_id")) == str(paper_id)),
            None,
        )

    if paper is None:
        raise HTTPException(status_code=404, detail="Paper not found")

    return paper
