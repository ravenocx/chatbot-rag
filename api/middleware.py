from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth_utils import verify_access_token

security = HTTPBearer()

def get_auth_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token."
        )
    return payload

def user_middleware(payload: dict = Depends(get_auth_token)):
    if payload.get("role") not in ["customer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized."
        )
    return payload

def admin_middleware(payload: dict = Depends(get_auth_token)):
    if payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized, you are not an admin."
        )
    return payload
