# 🔍 AI-Powered Research Paper Semantic Search & RAG System

> *Retrieval-Augmented Generation | Vector Search | NLP*

An intelligent full-stack platform for discovering, exploring, and interacting with academic research papers using semantic search and AI-powered question answering.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Technologies Used](#technologies-used)
- [Screenshots](#screenshots)
- [Installation & Setup](#installation--setup)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [Results & Performance](#results--performance)
- [Limitations](#limitations)
- [Future Enhancements](#future-enhancements)
- [References](#references)

---

## Overview

The exponential growth of scientific literature has created a significant challenge for researchers: finding relevant papers quickly and efficiently. Traditional keyword-based search systems fail to understand the *meaning* behind a query, often returning results that match words but not intent.

This project presents an **AI-Powered Research Paper Semantic Search and RAG System** — a complete intelligent platform that enables:

- Uploading research paper PDFs with automatic content extraction
- **Natural language semantic search** across uploaded papers
- **AI-generated question answering** grounded in document content (RAG)
- Confidence scores and source references for every answer
- Secure multi-user access with JWT authentication
- Cloud deployment on Google Cloud Platform via Docker

---

## Features

| Feature | Description |
|---|---|
| 📤 PDF Upload | Drag-and-drop upload with automatic text extraction, section detection, and metadata parsing |
| 🔍 Semantic Search | Natural language queries matched using 768-dim vector embeddings (SentenceTransformers + FAISS) |
| 🤖 RAG Q&A | Ask specific questions about any uploaded paper and receive grounded AI-generated answers |
| 📊 Confidence Scores | Every result and answer is accompanied by a cosine similarity confidence percentage |
| 🔖 Saved Papers | Bookmark papers for quick access and future Q&A sessions |
| 📖 PDF Viewer | In-browser PDF viewer with highlighted sections matching RAG answers |
| 🔐 Auth | JWT-based authentication for secure, stateless multi-user access |
| ☁️ Cloud Deployed | Fully containerized with Docker and deployed on Google Cloud Platform |

---

## System Architecture

The system follows a layered microservices-inspired architecture with 8 major layers:

```
User (Browser)
      │
      ▼
[Frontend — React SPA]
  - PDF Upload UI
  - Semantic Search UI
  - AI Q&A Chat Interface
  - PDF Viewer
  - Dashboard & Saved Papers
      │ REST API (HTTP)
      ▼
[Backend — FastAPI]
  - JWT Auth & Middleware
  - REST API Routes (/upload, /search, /ask, /saved)
  - Business Logic Controllers
      │
      ├──────────────────────────────────┐
      ▼                                  ▼
[Document Processing Pipeline]     [MongoDB]
  1. PDF Parse (PyMuPDF)             Users, Papers, Metadata
  2. Text Extraction                 Search History, Sessions
  3. Section Detection               Saved Papers, Logs
  4. Metadata Extraction
  5. Text Chunking
      │
      ▼
[NLP & Embedding Layer]
  SentenceTransformers → 768-dim Dense Vectors
      │
      ▼
[FAISS Vector Index]
  Global Index + Per-Paper Section Index
  ANN Search → Top-K Retrieval
      │
      ▼
[RAG Pipeline]
  1. Query Embedding
  2. Semantic Retrieval (FAISS)
  3. Reranking & Confidence Scoring
  4. Answer Generation
      │
      ▼
[Output: JSON Response]
  - AI Answer + Confidence Score
  - Highlighted Source Sections
  - Extracted References
      │
      ▼
[Google Cloud Platform — Docker + NGINX]
```
<img width="391" height="530" alt="image" src="https://github.com/user-attachments/assets/050afce8-cbc4-484d-8305-dabe4915f328" />

---

## Technologies Used

| Technology | Category | Role |
|---|---|---|
| **React.js** | Frontend | Component-based UI, state management, routing |
| **FastAPI** | Backend | High-performance Python API framework |
| **MongoDB** | Database | NoSQL storage for users, papers, metadata, history |
| **FAISS** | Vector Store | Fast similarity search over 768-dim embeddings |
| **SentenceTransformers** | NLP / AI | Semantic embedding generation (Hugging Face) |
| **PyMuPDF (fitz)** | PDF Processing | Text, image, and structure extraction from PDFs |
| **Docker** | DevOps | Containerization of all services |
| **Google Cloud Platform** | Cloud | Compute Engine VM hosting + persistent storage |
| **JWT** | Auth | Stateless token-based user authentication |
| **NGINX** | Web Server | Reverse proxy + frontend serving |
| **Docker Compose** | Orchestration | Multi-container service management |

---

## Screenshots

> **Note:** Replace the placeholder descriptions below with your actual screenshots.

### 13.1 — Login Page

<img width="684" height="391" alt="image" src="https://github.com/user-attachments/assets/84325418-f9dd-4ac1-a833-4557d776f207" />



*The login form with email and password fields. Users enter credentials here to receive a JWT token for authenticated access.*

---

### 13.2 — Signup / Registration Page
<img width="684" height="391" alt="image" src="https://github.com/user-attachments/assets/50d09ad7-49b6-4cda-b012-56e69dff8a3e" />



*New user registration form collecting name, email, and password with client-side validation.*

---

### 13.3 — User Dashboard
<img width="679" height="398" alt="image" src="https://github.com/user-attachments/assets/c2cf865e-d407-4596-abbb-d6c2d630a8cd" />


*Main dashboard showing total uploaded papers, recent searches, saved papers count, and quick-access buttons for Upload and Search.*

---

### 13.4 — PDF Upload Page
<img width="679" height="398" alt="image" src="https://github.com/user-attachments/assets/41580d52-dd09-4141-bb0d-a8ec0e2c5b09" />



*Drag-and-drop upload interface with progress bar and live processing status: Extracting Text → Generating Embeddings → Indexing.*

---

### 13.5 — Semantic Search Page
![Uploading image.png…]()



*Search bar with natural language query input. Left panel includes filters for date range, paper type, and confidence threshold.*


## Installation & Setup

### Prerequisites

- Docker & Docker Compose installed
- Git
- A Google Cloud Platform account (for cloud deployment)

### Local Development

```bash
# 1. Clone the repository
git clone https://github.com/your-username/ai-research-rag.git
cd ai-research-rag

# 2. Create environment variables
cp .env.example .env
# Edit .env with your settings:
# MONGO_URI=mongodb://mongo:27017/ragdb
# JWT_SECRET=your_secret_key

# 3. Start all services
docker-compose up --build

# Frontend: http://localhost:8080
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Docker Compose Configuration

```yaml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports: ["8080:80"]
    depends_on: [backend]

  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      - MONGO_URI=mongodb://mongo:27017/ragdb
      - JWT_SECRET=your_secret_key
    depends_on: [mongo]
    volumes: ["./faiss_index:/app/faiss_index"]

  mongo:
    image: mongo:6.0
    volumes: ["mongo_data:/data/db"]

volumes:
  mongo_data:
```

### Google Cloud Platform Deployment

```bash
# 1. Create a Compute Engine VM (e2-standard-4, Ubuntu 22.04)
# 2. SSH into the VM
gcloud compute ssh your-vm-name

# 3. Install Docker and Docker Compose
sudo apt update && sudo apt install -y docker.io docker-compose

# 4. Clone the repository
git clone https://github.com/your-username/ai-research-rag.git
cd ai-research-rag

# 5. Configure environment variables
cp .env.example .env && nano .env

# 6. Start all services in detached mode
docker-compose up -d

# 7. Configure GCP firewall rules to allow ports 8080 and 8000
```

---

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/auth/register` | POST | Register a new user (username, email, password) |
| `/auth/login` | POST | Authenticate user and return JWT access token |
| `/papers/upload` | POST | Upload PDF — triggers full processing pipeline |
| `/papers/` | GET | List all papers uploaded by the authenticated user |
| `/search/` | GET | Semantic search — `?q=your+natural+language+query` |
| `/qa/ask` | POST | Ask a question about a paper — returns RAG answer |
| `/saved/` | GET/POST | Get or save bookmarked papers |
| `/history/` | GET | Retrieve recent search and Q&A history |

All protected endpoints require the header: `Authorization: Bearer <jwt_token>`

Full interactive API documentation available at `/docs` (Swagger UI) when running locally.

---

## Project Structure

```
project-root/
├── backend/
│   ├── main.py                    # FastAPI entry point
│   ├── auth/
│   │   ├── jwt_handler.py         # Token creation & validation
│   │   └── routes.py              # /register, /login endpoints
│   ├── api/
│   │   ├── search.py              # /search endpoint
│   │   ├── upload.py              # /upload endpoint
│   │   └── qa.py                  # /ask endpoint
│   ├── processing/
│   │   ├── pdf_extractor.py       # PyMuPDF text extraction
│   │   ├── section_detector.py    # Section identification
│   │   └── chunker.py             # Text chunking logic
│   ├── embeddings/
│   │   ├── encoder.py             # SentenceTransformer wrapper
│   │   └── faiss_index.py         # FAISS index management
│   ├── models/
│   │   ├── user.py                # MongoDB User model
│   │   └── paper.py               # MongoDB Paper model
│   └── config.py                  # Environment variables & settings
│
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── Navbar.jsx
│       │   ├── SearchBar.jsx
│       │   ├── ResultCard.jsx
│       │   └── PdfViewer.jsx
│       ├── pages/
│       │   ├── Login.jsx
│       │   ├── Signup.jsx
│       │   ├── Dashboard.jsx
│       │   ├── Upload.jsx
│       │   ├── Search.jsx
│       │   ├── QnA.jsx
│       │   └── SavedPapers.jsx
│       ├── services/
│       │   └── api.js             # Axios API calls
│       ├── context/
│       │   └── AuthContext.jsx    # JWT state management
│       └── App.jsx
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Results & Performance

### Semantic Search Accuracy

| User Query | Top Result | Confidence |
|---|---|---|
| attention mechanism in neural translation | Attention Is All You Need | 94% |
| image segmentation using deep learning | U-Net: Convolutional Networks for Biomedical Segmentation | 89% |
| reinforcement learning game playing | Playing Atari with Deep Reinforcement Learning | 91% |
| BERT language model pre-training | BERT: Pre-training of Deep Bidirectional Transformers | 96% |
| graph neural network node classification | Semi-Supervised Classification with GCN | 88% |

### RAG Q&A Examples

| Question | Answer Summary | Score |
|---|---|---|
| What dataset was used? | WMT 2014 English-German dataset with 4.5M sentence pairs | 92% |
| What is the model architecture? | Transformer with 6 encoder/decoder layers, 8-head attention, d_model=512 | 95% |
| What was the main contribution? | Introduced self-attention, removing recurrence and convolutions in sequence models | 90% |

### Performance Metrics

| Metric | Value |
|---|---|
| Average Semantic Search Confidence | 87–95% |
| FAISS Query Time (1,000 papers) | < 50 ms |
| PDF Processing Time (10-page paper) | 3–7 seconds |
| RAG Answer Generation Time | 2–4 seconds |
| API Authentication Overhead | < 10 ms |
| System Uptime (Cloud, 30-day test) | 99.2% |

### Confidence Score Guide

| Score | Interpretation |
|---|---|
| 90–100% | Highly Relevant — use with full confidence |
| 75–89% | Relevant — good match, verify key claims |
| 60–74% | Possibly Relevant — review source section directly |
| < 60% | Low Relevance — may not directly answer the query |

---

## Limitations

- Embedding quality depends on the SentenceTransformer model — highly specialized domains may need fine-tuning
- FAISS is in-memory — very large collections (millions of papers) would require IVF-PQ configurations
- RAG answer quality is bounded by the context window of the underlying language model
- Scanned/image-based PDFs without OCR will not extract text correctly
- Currently optimized for English-language papers only
- No offline mode — backend must be running for all operations

---

## Future Enhancements

- **Full LLM Integration** — GPT-4, Claude, or locally hosted Llama for richer Q&A
- **Conversational Chatbot** — multi-turn chat interface with session memory
- **Multi-Language Support** — multilingual models (LaBSE, mBERT) for non-English papers
- **Cross-Encoder Re-Ranking** — improve result ordering after initial FAISS retrieval
- **Voice-Based Search** — Web Speech API for hands-free query input
- **Collaborative Workspaces** — shared paper collections, annotations, and search results for teams
- **Citation Network Visualization** — interactive graph of paper citation relationships
- **Fine-Tuned Domain Models** — user-trainable embeddings for specific research domains
- **Mobile App** — React Native companion app for on-the-go access
- **Export & Reporting** — export Q&A sessions and summaries as PDF or Word documents

---



*M.Tech Project — AI-Powered Research Paper Semantic Search & RAG System | Department of Computer Science & Engineering | 2024–2025*
