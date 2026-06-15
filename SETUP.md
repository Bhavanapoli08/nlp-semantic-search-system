# Setup — Full-Stack CRUD Research Paper Search

End-to-end setup for the FastAPI, MongoDB, React, Docker, JWT, and FAISS application.

## Local Development

1. Create backend environment variables.

```bash
cp .env.example .env
```

Use a local MongoDB or Atlas URI:

```bash
MONGO_URI=mongodb://localhost:27017
MONGO_DB=research_search
JWT_SECRET=replace-with-a-long-random-value
CORS_ORIGINS=http://localhost:5173
PDF_UPLOAD_DIR=./pdfs
```

2. Install and run the FastAPI backend.

```bash
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

3. Install and run the React frontend.

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

4. Open the app.

```text
Frontend: http://localhost:5173
Backend docs: http://localhost:8000/docs
```

## CRUD API

All routes below are protected with `Authorization: Bearer <jwt>`.

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/papers` | Create paper metadata and optional PDF upload |
| `GET` | `/papers?q=&tag=` | List/filter owned papers |
| `GET` | `/papers/{id}` | Get one owned paper |
| `PUT` | `/papers/{id}` | Update paper metadata |
| `DELETE` | `/papers/{id}` | Delete owned paper and saved references |
| `POST` | `/papers/save` | Save or upsert a paper |
| `GET` | `/papers/saved?q=` | List/filter saved papers |
| `PUT` | `/papers/save/{id}` | Update saved-paper notes/tags/metadata |
| `DELETE` | `/papers/save/{id}` | Delete saved-paper record |
| `GET` | `/auth/me` | Get current user profile |
| `PUT` | `/auth/update` | Update name, email, or password |
| `DELETE` | `/auth/delete` | Delete user, owned papers, and saved papers |

Compatibility routes remain available:

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/upload` | Upload PDF through the new Mongo-backed paper create flow |
| `POST` | `/upload/ask` | Ask questions against uploaded paper sections |
| `GET` | `/search?q=` | Existing FAISS semantic search |

## Docker Compose

1. Set production-ish environment variables.

```bash
export JWT_SECRET="$(openssl rand -hex 32)"
export CORS_ORIGINS="http://YOUR_VM_IP:8080"
export VITE_API_URL="http://YOUR_VM_IP:8000"
```

2. Build and start the stack.

```bash
docker compose up --build -d
```

3. Verify services.

```bash
docker compose ps
curl http://localhost:8000/
```

4. Open:

```text
Frontend: http://YOUR_VM_IP:8080
Backend: http://YOUR_VM_IP:8000
MongoDB: internal service mongo:27017
```

## Google Cloud VM Notes

1. Install Docker and Docker Compose plugin on the VM.
2. Clone or copy this repository onto the VM.
3. Ensure firewall rules allow TCP `8080` for the frontend and `8000` for the API.
4. Keep `pdfs/` and `tmp/` mounted as volumes so uploaded PDFs and FAISS index files survive container rebuilds.
5. Replace default secrets before exposing the VM publicly.

## Data Model

MongoDB collections:

| Collection | Main fields |
| --- | --- |
| `users` | `name`, `email`, `password`, `created_at`, `updated_at` |
| `papers` | `owner_id`, `title`, `authors`, `abstract`, `summary`, `tags`, `filename`, `file_path`, `sections`, timestamps |
| `saved_papers` | `owner_id`, `paper_id`, `title`, `authors`, `summary`, `notes`, `tags`, timestamps |

Ownership validation is enforced by querying each CRUD record with the authenticated user id.
