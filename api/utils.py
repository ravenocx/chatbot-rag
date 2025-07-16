import jwt
from jwt import PyJWTError
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")

def create_access_token(user_id: int, role: str, expires_delta: timedelta = None ):
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=6))
    claims = {
        "sub": str(user_id),
        "role": role,
        "iat" : datetime.utcnow(),
        "exp": expire,
    }
    encoded_jwt = jwt.encode(claims, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        print("[DEBUG] Decoded payload:", payload)
        return payload
    except PyJWTError as e:
        print("[DEBUG] JWT decode error:", str(e))
        return None
