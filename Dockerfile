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
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the entire project
COPY . .

# Optional: explicitly copy your embedding index and chunks
# Adjust the paths if your index/chunk files are elsewhere
# COPY rag/data /app/rag/data

# Expose the port FastAPI will run on
EXPOSE 8000

# Default command to run the app
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]