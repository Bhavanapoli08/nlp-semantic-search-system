import streamlit as st
import json
import os
import numpy as np
import tempfile
import spacy
import scispacy
import fitz
import pdfplumber
import re
import pandas as pd
import datetime
import pdfreader
import shutil
import requests
import pickle
import faiss
from langdetect import detect
from sentence_transformers import SentenceTransformer
from scispacy.linking import EntityLinker
from transformers import pipeline

# Set up Streamlit configuration
st.set_page_config(page_title="Research Paper Explorer", layout="wide")

# utils notebooks 
from utils.pdfExt import process_pdf
from utils.summarize import add_summaries
from utils.embeddingsPDF import add_embeddings
from utils.classification import classify_by_global
from utils.query import unified_search
from utils.appendFiass import append_embeddings_to_faiss
from utils.garbage_check import is_academic_query


os.environ["TOKENIZERS_PARALLELISM"] = "false"
# === CONFIG ===
directory_path = "./entity"
directory_path_emb = "./embeddings"
directory_path_pdf = "./pdfs"
# Ensure the directories exist
if not os.path.exists(directory_path):
    os.makedirs(directory_path, exist_ok=True)
if not os.path.exists(directory_path_emb):
    os.makedirs(directory_path_emb, exist_ok=True)
if not os.path.exists(directory_path_pdf):
    os.makedirs(directory_path_pdf, exist_ok=True)
    
# === FAISS PATHS ===
# These paths are used to read/write the FAISS indexes and metadata.
# If you want to use a different path, change the values in the faiss_paths dictionary.
# The cache_path is used to store the FAISS indexes and metadata in a cache directory.
# If you want to use a different path, change the values in the cache_path dictionary.
faiss_paths = {
    'global_idx': "./tmp/faiss_global.idx",
    'meta_pkl': "./tmp/faiss_metadata.pkl",
    'sec_idx': "./tmp/faiss_sections.idx",
    'sec_meta': "./tmp/faiss_section_meta.pkl",
}    

cache_path={
    'global_idx': "./cache/faiss/faiss_global.idx",
    'meta_pkl': "./cache/faiss/faiss_metadata.pkl",
    'sec_idx': "./cache/faiss/faiss_sections.idx",
    'sec_meta': "./cache/faiss/faiss_section_meta.pkl",
}
# === LOAD FAISS INDEXES and METADATA ===
faiss_section_idx = faiss.read_index(faiss_paths["sec_idx"])
section_metadata = pickle.load(open(faiss_paths["sec_meta"], "rb"))
faiss_global_idx = faiss.read_index(faiss_paths["global_idx"])
metadata = pickle.load(open(faiss_paths["meta_pkl"], "rb"))

# === CACHE DIRS ===
CACHE_DIR = os.path.join(os.getcwd(), "cache")
EMB_DIR = os.path.join(CACHE_DIR, "embeddings")
PDF_DIR = os.path.join(CACHE_DIR, "pdfs")
for p in [EMB_DIR, PDF_DIR]: os.makedirs(p, exist_ok=True)

# === STREAMLIT ===
#st.cache_data.clear()
st.title("📚 Research Paper Explorer")

# === CSS STYLING ===
st.markdown("""
<style>
.tab-content { padding:1rem; background:#f9f9f9; border-radius:10px; }
.btn-reset { background:#e74c3c; color:#fff; border:none; padding:0.5rem; border-radius:5px; cursor:pointer; }
.btn-reset:hover { background:#c0392b; }
</style>
""", unsafe_allow_html=True)


#=== CACHED FUNCTIONS ===
@st.cache_data
def load_embedded_papers():
    papers=[]
    for f in os.listdir(directory_path):
        if f.endswith('.json'):
            papers.append(add_embeddings(json.load(open(os.path.join(directory_path,f)))))
    return papers



# === STATE INIT ===
if 'clusters' not in st.session_state: st.session_state.clusters={}
if 'show_clusters' not in st.session_state: st.session_state.show_clusters=False
if 'uploaded_path' not in st.session_state: st.session_state.uploaded_path=None
if 'current_emb' not in st.session_state: st.session_state.current_emb=None
if 'clusters_upload' not in st.session_state: st.session_state.clusters_upload={}
if 'clusters_upload_show' not in st.session_state: st.session_state.clusters_upload_show=False

# === TABS ===
tab1, tab2 = st.tabs(["🔎 Query/Cluster Existing", "📤 Upload & Cluster"])

# --- TAB1: existing ---
with tab1:
    st.header("Existing Papers")
    # 1) Load existing papers
    papers = load_embedded_papers()
    c1,c2 = st.columns(2)
 
    if c1.button("Cluster Existing Papers", key="cluster_existing"):
        st.session_state.clusters = classify_by_global(papers, k=3)
        st.session_state.show_clusters=True
    if c2.button("Reset Clusters", key="reset_existing"):
        st.session_state.show_clusters=False
        st.session_state.clusters={}
    if st.session_state.show_clusters:
        for cid,titles in st.session_state.clusters.items():
            st.markdown(f"**Cluster {cid+1}:** {', '.join(titles)}")


    st.markdown("---")
    q1=st.text_input("Query existing papers", key='q1')
    if q1:
        # 2) First check: is the question even about research papers?
        if not is_academic_query(q1, threshold=0.70):
            st.warning("🚫 This question does not appear related to any of the stored papers.")
            st.info("Please ask something about the domain (e.g., biology, enzyme design, gene finding).")
        else:
            # 3) If it is “relevant,” run your usual FAISS search:
            sections, papers = unified_search(q1,
                                             faiss_global_idx,
                                             metadata,
                                             faiss_section_idx,
                                             section_metadata,
                                              )
                    
            if not sections and not papers:
                st.warning("🚫 No relevant results found for your query.")
                st.info("Try rephrasing in more specific, scientific terms.")
            else:
                if sections:
                    st.subheader("🧩 Matching Sections")
                    for r in sections:
                        st.markdown(f"**📄 {r['title']} ({r['section_name']})**")
                        st.write(r["text"])
                        st.caption(f"Score: {r['score']:.2f}")
                else:
                    st.info("No matching sections found.")

                if papers:
                    st.subheader("📚 Matching Papers")
                    for r in papers:
                        authors = r["authors"] or "N/A"
                        st.markdown(f"**#{r['rank']} 📄 {r['title']}**")
                        st.markdown(f"👨‍🔬 **Authors:** {authors}")
                        st.markdown(f"📝 **Summary:** {r['summary']}")
                       
                else:
                    st.info("No matching papers found.")

# --- TAB2: Upload & Cluster ---
with tab2:
    st.header("Upload & Cluster New Paper")
    st.markdown("<div class='tab-content'>", unsafe_allow_html=True)

    # 1) FILE-UPLOAD
    uploaded = st.file_uploader("Upload PDF", type='pdf')
    if uploaded:
        # Initialize wn_paper on every render so it can be used later
        wn_paper = load_embedded_papers()

        # If this is the first time processing this particular upload:
        if not st.session_state.uploaded_path:
            original_filename = uploaded.name  
            # e.g. "Energy and Policy Considerations for Deep Learning in NLP" from "Energy and Policy Considerations for Deep Learning in NLP.pdf"
            title = os.path.splitext(original_filename)[0]
            st.session_state.title = title
            # 1a) Save uploaded file to a temp file
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            tmp.write(uploaded.read())
            tmp.close()
            st.session_state.uploaded_path = tmp.name

            # 1c) Run the processing pipeline
            j = process_pdf(st.session_state.uploaded_path, st.session_state.title)
            s = add_summaries(j, "user")
            emb = add_embeddings(s)
            st.session_state.current_emb = emb

            # 1d) Cache JSON + embeddings on disk
            with open(os.path.join(EMB_DIR, f"{st.session_state.title}_emb.json"), "w") as f:
                f.write(json.dumps(emb, indent=2))
            with open(os.path.join(PDF_DIR, f"{st.session_state.title}.pdf"), "wb") as f:
                f.write(uploaded.getvalue())

            # 1e) Show the title and summary
            st.session_state.current_emb = emb
            st.markdown(f"**Title:** {st.session_state.title}")
            st.markdown(f"**Summary:** {s['global_summary']}")
            st.session_state.current_emb = emb
            st.success("Processed and cached")

            # 1e) Show how many papers (including the new one) exist
            num_embeddings = len(wn_paper) + 1
            st.markdown(f"**Total papers available for clustering:** {num_embeddings}")

            # 1f) Ask user for K
            st.session_state.cluster_k = st.number_input(
                "Select number of clusters (K):",
                min_value=2,
                max_value=num_embeddings,
                value=min(4, num_embeddings),
                step=1,
            )

        # 2) CLUSTER BUTTON
        c3, c4 = st.columns(2)
        if c3.button("Cluster with Uploaded & Existing PDF", key="cluster_uploaded"):
            # Recompute embedding (or simply reuse the one in state)
            all_emb = add_embeddings(st.session_state.current_emb)
            wn_paper.append(all_emb)
            
            # Allow user to determine the number of clusters
            k = int(st.session_state.cluster_k)
            st.session_state.clusters_upload = classify_by_global(wn_paper, k=k)
            st.session_state.clusters_upload_show = True
            
        # A button that allow the users to clean the listed clusters
        if c4.button("Reset Clusters", key="reset_uploaded"):
            st.session_state.clusters_upload_show = False
            st.session_state.clusters_upload = {}

        # 2a) Show clusters if they exist
        if st.session_state.clusters_upload_show:
            for cid, titles in st.session_state.clusters_upload.items():
                st.markdown(f"**Cluster {cid+1}:** {', '.join(titles)}")
                
        # append the new file to existing faiss disk.
        idx, meta, sidx, smeta = append_embeddings_to_faiss(
                                [st.session_state.current_emb], 
                                faiss_paths["global_idx"],
                                faiss_paths["meta_pkl"],
                                faiss_paths["sec_idx"],
                                faiss_paths["sec_meta"],
                            )
        # 3) Save indexes and metadata to session state
        st.session_state.global_idx = idx
        st.session_state.meta_pkl = meta
        st.session_state.sec_idx = sidx
        st.session_state.sec_meta = smeta
        
        
        
        # 4) QUERY LOOP ON THE NEW + EXISTING COLLECTION
        q2 = st.text_input("Query this paper + existing", key="q2")
        if q2:
                # 2) First check: is the question even about research papers?
            if not is_academic_query(q2, threshold=0.70):
                st.warning("🚫 This question does not appear related to any of the stored papers.")
                st.info("Please ask something about the domain (e.g., biology, enzyme design, gene finding).")
            else:
            #     # 3) If it is “relevant,” run your usual FAISS search:
                sections, papers = unified_search(
                    q2,
                    st.session_state.global_idx,
                    st.session_state.meta_pkl,
                    st.session_state.sec_idx,
                    st.session_state.sec_meta,
                    )
                if not sections and not papers:
                    st.warning("🚫 No relevant results found for your query.")
                    st.info("Try rephrasing in more specific, scientific terms.")
                else:
                    if sections:
                        st.subheader("🧩 Matching Sections")
                        for r in sections:
                            st.markdown(f"**📄 {r['title']} ({r['section_name']})**")
                            st.write(r["text"])
                    else:
                        st.info("No matching sections found.")

                    if papers:
                        st.subheader("📚 Matching Papers")
                        for r in papers:
                            authors = r["authors"] or "N/A"
                            st.markdown(f"**#{r['rank']} 📄 {r['title']}**")
                            st.markdown(f"👨‍🔬 **Authors:** {authors}")
                            st.markdown(f"📝 **Summary:** {r['summary']}")
                            
                    else:
                        st.info("No matching papers found.")

        else:
                st.info("Please upload a PDF to start.")
        
        # 5) SAVE RADIO
        save = st.radio("Save this paper to existing?", ["No", "Yes"], key="save")
        if save == "Yes":
            # Move the cached JSON and embbeded file into the permanent directory
            # We rename it so it uses the paper's title as its filename.
            json_src = os.path.join(EMB_DIR, f"{st.session_state.title}_emb.json")
            json_dst = os.path.join(directory_path_emb, f"{st.session_state.title}.json")

            if os.path.exists(json_src):
                shutil.move(json_src, json_dst)
            else:
                st.warning("⚠️ Embedding file not found or already moved")
            # Move the cached PDF into the permanent directory
            pdf_src = os.path.join(PDF_DIR, f"{st.session_state.title}.pdf")
            pdf_dst = os.path.join(directory_path_pdf, f"{st.session_state.title}.pdf")
            
            if os.path.exists(json_src):
                shutil.move(json_src, json_dst)
            else:
                st.warning("⚠️ Embedding file not found or already moved")

            # 3) Save the new FAISS indexes and metadata
            # Move the cached faiss disk into the permanent directory
            faiss.write_index(st.session_state.global_idx, faiss_paths["global_idx"])
            pickle.dump(st.session_state.meta_pkl, open(faiss_paths["meta_pkl"], "wb"))
            faiss.write_index(st.session_state.sec_idx, faiss_paths["sec_idx"])
            pickle.dump(st.session_state.sec_meta, open(faiss_paths["sec_meta"], "wb"))
            st.success("Saved and FAISS updated")

        else:
            # 4) CLEAR UPLOAD / CACHE BUTTON
            if st.button("Clear Upload and Cache"):
                shutil.rmtree(CACHE_DIR)
                os.makedirs(CACHE_DIR, exist_ok=True)
                st.session_state.uploaded_path = None
                st.session_state.current_emb = None
                st.session_state.title = None
                st.session_state.cluster_k = None
                for key in ["global_idx", "meta_pkl", "sec_idx", "sec_meta"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.success("Cleared")

    st.markdown("</div>", unsafe_allow_html=True)




