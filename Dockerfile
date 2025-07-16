# Use an official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install OS dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Optional: explicitly copy embedding index or other data
# COPY rag/data /app/rag/data

# Expose the port FastAPI will run on
EXPOSE 8000

# Set Huggingface cache for prod
ENV HF_HOME=/workspace/hf-home
# ENV TRANSFORMERS_CACHE=/workspace/hf-cache
ENV SENTENCE_TRANSFORMERS_HOME=/workspace/st-cache

# Set Another env
ENV INDEX_FILE=./rag/data/tokopoin_product.index
ENV CHUNK_FILE=./rag/data/chunk_texts.pkl
ENV HUGGINGFACE_TOKEN=

# Run using Gunicorn with Uvicorn workers for production
# comment if want to build the app
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "api.main:app", "--bind", "0.0.0.0:8000", "--workers", "1", "--timeout", "300"]