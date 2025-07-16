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