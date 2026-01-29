"""
Script para verificar e corrigir encoding dos dados já importados.
Execute este script se você já importou dados com encoding incorreto.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Medicamento
import chardet

def detect_encoding(text):
    """Detect encoding of a text string"""
    if not text:
        return None
    try:
        result = chardet.detect(text.encode('latin-1'))
        return result['encoding']
    except:
        return None

def check_encoding_issues(db: Session):
    """Check for encoding issues in the database"""
    print("Checking for encoding issues...")
    
    # Sample some records
    records = db.query(Medicamento).limit(100).all()
    
    issues_found = 0
    for record in records:
        fields_to_check = [
            record.nome_produto,
            record.categoria_regulatoria,
            record.classe_terapeutica,
            record.empresa_detentora_registro,
            record.principio_ativo
        ]
        
        for field in fields_to_check:
            if field and ('' in field or 'ASSSOCIAC' in field or 'FARMACUTICA' in field):
                issues_found += 1
                print(f"Issue found in record ID {record.id}: {field[:50]}")
                break
    
    if issues_found > 0:
        print(f"\nFound {issues_found} records with potential encoding issues.")
        print("You should reimport the CSV with the corrected import script.")
    else:
        print("No encoding issues detected!")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        check_encoding_issues(db)
    finally:
        db.close()
