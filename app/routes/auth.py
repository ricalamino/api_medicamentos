from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import APIKey
from app.schemas import APIKeyCreate, APIKeyResponse, APIKeyCreateResponse
from app.auth import get_api_key, generate_api_key, hash_key
from app.ratelimit import check_rate_limit

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/keys/public", response_model=APIKeyCreateResponse)
def create_api_key_public(
    key_data: APIKeyCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    """Create a new API key (public, no auth). Rate limited by IP (5/hour)."""
    check_rate_limit(request)
    new_key = generate_api_key()
    hashed_key = hash_key(new_key)
    db_key = APIKey(
        key=hashed_key,
        name=key_data.name,
        is_active=True,
    )
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    return APIKeyCreateResponse(
        id=db_key.id,
        key=new_key,
        name=db_key.name,
        is_active=db_key.is_active,
        created_at=db_key.created_at,
    )


@router.post("/keys", response_model=APIKeyCreateResponse)
def create_api_key(
    key_data: APIKeyCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    """Create a new API key (requires authentication)"""
    # Generate new key
    new_key = generate_api_key()
    hashed_key = hash_key(new_key)
    
    # Create API key record
    db_key = APIKey(
        key=hashed_key,
        name=key_data.name,
        is_active=True
    )
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    
    # Return the plain key only once
    response = APIKeyCreateResponse(
        id=db_key.id,
        key=new_key,
        name=db_key.name,
        is_active=db_key.is_active,
        created_at=db_key.created_at
    )
    
    return response


@router.get("/keys", response_model=List[APIKeyResponse])
def list_api_keys(
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    """List all API keys (requires authentication)"""
    keys = db.query(APIKey).order_by(APIKey.created_at.desc()).all()
    return keys


@router.patch("/keys/{key_id}/toggle", response_model=APIKeyResponse)
def toggle_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    """Toggle API key active status (requires authentication)"""
    db_key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if not db_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API Key not found"
        )
    
    db_key.is_active = not db_key.is_active
    db.commit()
    db.refresh(db_key)
    
    return db_key


@router.delete("/keys/{key_id}")
def delete_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    """Delete API key (requires authentication)"""
    db_key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if not db_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API Key not found"
        )
    
    db.delete(db_key)
    db.commit()
    
    return {"message": "API Key deleted successfully"}
