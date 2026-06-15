FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (important for FAISS + NLP libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy rest of project files
COPY . .

# Create required directories (if your code expects them)
RUN mkdir -p tmp cache/embeddings cache/pdfs

# Disable tokenizer parallelism (prevents warnings/crashes)
ENV TOKENIZERS_PARALLELISM=false

# Force single thread for FAISS stability
ENV OMP_NUM_THREADS=1

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI (NO reload, NO multiple workers)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]