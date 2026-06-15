# Research Paper Explorer — Frontend

React + Vite + Tailwind. Connects to the FastAPI backend (semantic search) and MongoDB Atlas (auth + saved papers).

## Setup

```bash
cd frontend
cp .env.example .env       # adjust VITE_API_URL if backend runs elsewhere
npm install
npm run dev                # http://localhost:5173
```

## Pages
- `/login`, `/signup` — JWT auth via `/auth/login` and `/auth/signup`
- `/` — semantic search (calls `GET /search?q=...`)
- `/saved` — bookmarked papers (calls `/papers/saved`, `/papers/save`)
