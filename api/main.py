from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
# from rag.inference import generate_response
from rag.embedder import embedd_product_data
from rag.retriever import retrieve_docs
from api.utils import create_access_token
import api.middleware as mw
import api.db.database as db
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Tokopoin RAG Chatbot API",
    description="Tokopoin chatbot with RAG capabilities",
    version="1.0.0"
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db_conn = db.db_connection()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RegisterRequest(BaseModel):
    name: str
    phone_number:str
    email: str
    password: str

class RegisterResponse(BaseModel):
    success: bool
    status_code: int
    message : str
    access_token : str

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    status_code: int
    message : str
    access_token : str

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    success: bool
    status_code: int
    message : str
    answer: str

class EmbeddingResponse(BaseModel):
    success: bool
    status_code: int
    message : str

class RetrievalResult(BaseModel):
    score: float
    document: str

class RetrievalResponse(BaseModel):
    success: bool
    status_code: int
    message : str
    result: List[RetrievalResult]

class RagConfiguration(BaseModel):
    main_instruction: str
    critical_instruction: str
    additional_guideline: str
    retriever_instruction: str
    top_k_retrieval: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class RagConfigResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: RagConfiguration

class UpdateRagConfigRequest(BaseModel):
    main_instruction: str
    critical_instruction: str
    additional_guideline: str
    retriever_instruction: str
    top_k_retrieval: int

@app.get("/api/status", tags=["Status"])
def status():
    return {
        "success" : True,
        "status_code": 200,
        "status": "RAG Chatbot API is running.",
        "version": "v1.0",
        "message": "Ready to process query."
    }

@app.post("/api/register/user",response_model=RegisterResponse, tags=["Register User"])
def register_user(payload: RegisterRequest):
    try:
        # Check if email already exists
        existing_user = db.get_user(db_conn, payload.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = pwd_context.hash(payload.password)
        user_id = db.create_user(db_conn, payload.name, payload.email, payload.phone_number, hashed_password)

        if not user_id:
            raise HTTPException(status_code=500, detail="Failed to register user")

        token = create_access_token(user_id=user_id, role="customer")
        return RegisterResponse(success=True, status_code=200, message="User registered successfully", access_token=token)
    except HTTPException as e:
        raise e
    except Exception as e:
        print("[DEBUG] User Register error :", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/login/user", response_model=LoginResponse, tags=["User Login"])
def login_user(payload: LoginRequest):
    try : 
        user = db.get_user(db_conn, payload.email)

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

@app.post("/api/login/admin", response_model=LoginResponse, tags=["Admin Login"])
def login_admin(payload: LoginRequest):
    try :
        admin = db.get_admin(db_conn, payload.email)

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

# @app.post("/api/query", response_model=QueryResponse, tags=["Chatbot RAG"])
# def answer_query(payload: QueryRequest, user_payload: dict = Depends(mw.user_middleware)):
#     try:
#         answer = generate_response(db_conn, payload.query, max_tokens=4096) # Change max tokens if needed
#         return QueryResponse(success=True, status_code=200, message="Successfully Generate answer", answer=answer)
#     except Exception as e:
#         print("[DEBUG] Chatbot Query error :", str(e))
#         raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/api/embedd-products", response_model=EmbeddingResponse, tags=["Embedd Product Data"])
def embedd_products(admin: dict = Depends(mw.admin_middleware)):
    try:
        embedd_product_data(db_conn)
        return EmbeddingResponse(success=True, status_code=200, message="Successfully Embedd Product Data")
    except Exception as e:
        print("[DEBUG] Embedding error :", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/retrieve-documents", response_model=RetrievalResponse, tags=["Retrieve Product Document Data"])
def embedd_products(payload: QueryRequest, admin: dict = Depends(mw.admin_middleware)):
    try:
        results = retrieve_docs(db_conn, payload.query)
        print(results[0]["text"])
        return RetrievalResponse(success=True, 
                                 status_code=200, 
                                 message="Successfully Retrieve Product Document Data", 
                                 result=[RetrievalResult(document=item["text"], score=item["score"]) for item in results])
    except Exception as e:
        print("[DEBUG] Retrieval error :", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rag-configurations", response_model=RagConfigResponse, tags=["Show RAG Configurations"])
def get_rag_configurations(admin: dict = Depends(mw.admin_middleware)):
    try:
        rag_config = db.get_rag_configuration(db_conn)
        return RagConfigResponse(
            success=True,
            status_code=200,
            message="Successfully retrieved RAG configurations",
            data=RagConfiguration(
                main_instruction = rag_config["main_instruction"],
                critical_instruction = rag_config["critical_instruction"],
                additional_guideline = rag_config["additional_guideline"],
                retriever_instruction = rag_config["retriever_instruction"],
                top_k_retrieval = rag_config["top_k_retrieval"],
                created_at = rag_config["created_at"],
                updated_at = rag_config["updated_at"]
            )
        )
    except Exception as e:
        print("[DEBUG] Retrieval RAG Configurations error:", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/api/rag-configurations", response_model=RagConfigResponse, tags=["Update RAG Configurations"])
def update_rag_configuration(payload: UpdateRagConfigRequest, admin: dict = Depends(mw.admin_middleware)):
    try:
        result = db.update_rag_configuration(db_conn, payload.model_dump())
        return RagConfigResponse(
            success=True,
            status_code=200,
            message="Successfully updated RAG configurations",
            data=RagConfiguration(
                main_instruction = result["main_instruction"],
                critical_instruction = result["critical_instruction"],
                additional_guideline = result["additional_guideline"],
                retriever_instruction = result["retriever_instruction"],
                top_k_retrieval = result["top_k_retrieval"],
                created_at = result["created_at"],
                updated_at = result["updated_at"]
            )
        )
    except Exception as e:
        print("[DEBUG] Update RAG Configurations error:", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

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