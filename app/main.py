from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag.inference import generate_response

app = FastAPI()

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
        answer = generate_response(payload.query, k=3, max_tokens=4096) # Change k for top (n) retrieval
        return QueryResponse(query=payload.query, answer=answer)
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ! uvicorn app.main:app --reload