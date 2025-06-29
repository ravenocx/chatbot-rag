from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag.inference import generate_response

app = FastAPI(
    title="Tokopoin RAG Chatbot API",
    description="Tokopoin chatbot with RAG capabilities",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query: str
    answer: str

@app.get("/", tags=["Status"])
def status():
    return {
        "status": "RAG Chatbot API is running",
        "version": "v1.0",
        "message": "Ready to process query."
    }

@app.post("/query", response_model=QueryResponse, tags=["Chatbot"])
def answer_query(payload: QueryRequest):
    try:
        answer = generate_response(payload.query, k=5, max_tokens=4096) # Change k for top (n) retrieval
        return QueryResponse(query=payload.query, answer=answer)
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ! uvicorn app.main:app --reload or run main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="127.0.0.1", 
        port=8000, 
        reload=True,
        log_level="info"
    )