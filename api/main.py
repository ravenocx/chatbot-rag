from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
# from rag.inference import generate_response
from auth_utils import create_access_token
import middleware as mw
import db.database as db
from passlib.context import CryptContext

app = FastAPI(
    title="Tokopoin RAG Chatbot API",
    description="Tokopoin chatbot with RAG capabilities",
    version="1.0.0"
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
    success: bool
    status_code: int
    message : str
    answer: str

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    status_code: int
    message : str
    access_token : str

@app.get("/api/status", tags=["Status"])
def status():
    return {
        "success" : True,
        "status_code": 200,
        "status": "RAG Chatbot API is running.",
        "version": "v1.0",
        "message": "Ready to process query."
    }

@app.post("/api/login/user", tags=["User Login"])
def login_user(payload: LoginRequest):
    try : 
        conn = db.db_connection()
        user = db.get_user(conn, payload.email)

        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        if not pwd_context.verify(payload.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token = create_access_token(user_id=user["id"], role="customer")
        return LoginResponse(success=True, status_code=200, message="Login Successfully", access_token=token)
    except HTTPException as e:
        raise e
    except Exception as e :
        print("[DEBUG] User Login error :", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/login/admin", tags=["Admin Login"])
def login_admin(payload: LoginRequest):
    try :
        conn = db.db_connection()
        admin = db.get_admin(conn, payload.email)

        if not admin:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        if not pwd_context.verify(payload.password, admin["password"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token = create_access_token(user_id=admin["id"], role="admin")
        return LoginResponse(success=True, status_code=200, message="Login Successfully", access_token=token)
    except HTTPException as e:
        raise e
    except Exception as e :
        print("[DEBUG] User Login error :", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# @app.post("/api/query", response_model=QueryResponse, tags=["Chatbot"])
# def answer_query(payload: QueryRequest, user_payload: dict = Depends(mw.user_middleware)):
#     try:
#         answer = generate_response(payload.query, k=5, max_tokens=4096) # Change k for top (n) retrieval
#         return QueryResponse(success=True, status_code=200, message="Successfully Generate answer", answer=answer)
#     except Exception as e:
#         print("[DEBUG] Query error :", str(e))
#         raise HTTPException(status_code=500, detail=str(e))

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