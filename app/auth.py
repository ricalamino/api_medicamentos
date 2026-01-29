from fastapi import Security, HTTPException, status, Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
import hashlib
from app.database import get_db
from app.models import APIKey
from datetime import datetime

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def hash_key(key: str) -> str:
    """Hash API key using SHA256"""
    return hashlib.sha256(key.encode()).hexdigest()


def verify_api_key(api_key: str, db: Session) -> bool:
    """Verify if API key exists and is active"""
    hashed_key = hash_key(api_key)
    db_key = db.query(APIKey).filter(APIKey.key == hashed_key).first()
    if not db_key or not db_key.is_active:
        return False
    
    # Update last_used_at
    db_key.last_used_at = datetime.utcnow()
    db.commit()
    return True


def get_api_key(api_key: str = Security(api_key_header), db: Session = Depends(get_db)):
    """Dependency to validate API key"""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key missing"
        )
    
    if not verify_api_key(api_key, db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API Key"
        )
    
    return api_key


def generate_api_key() -> str:
    """Generate a new API key"""
    import secrets
    return secrets.token_urlsafe(32)
