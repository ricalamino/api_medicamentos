import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.models import APIKey
from app.auth import generate_api_key, hash_key


def create_first_api_key(name: str = "Initial Admin Key"):
    """Create the first API key (bypasses auth requirement)"""
    db: Session = SessionLocal()
    
    try:
        # Initialize database
        init_db()
        
        # Check if any keys exist
        existing_keys = db.query(APIKey).count()
        if existing_keys > 0:
            print("API keys already exist. Use the API to create new keys.")
            print("Or delete existing keys first if you want to create a new initial key.")
            return
        
        # Generate new key
        new_key = generate_api_key()
        hashed_key = hash_key(new_key)
        
        # Create API key record
        db_key = APIKey(
            key=hashed_key,
            name=name,
            is_active=True
        )
        db.add(db_key)
        db.commit()
        db.refresh(db_key)
        
        print("\n" + "="*60)
        print("API Key created successfully!")
        print("="*60)
        print(f"Key ID: {db_key.id}")
        print(f"Name: {db_key.name}")
        print(f"\nAPI Key (save this securely, it won't be shown again):")
        print(f"{new_key}")
        print("\n" + "="*60)
        print("\nUse this key in the X-API-Key header for all API requests.")
        print("Example:")
        print(f"  curl -H 'X-API-Key: {new_key}' http://localhost:8000/api/v1/medicamentos")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"Error creating API key: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    name = "Initial Admin Key"
    if len(sys.argv) > 1:
        name = sys.argv[1]
    
    create_first_api_key(name)
