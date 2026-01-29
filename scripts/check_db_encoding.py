#!/usr/bin/env python3
"""Check encoding of data in database"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Medicamento

def check_encoding():
    db: Session = SessionLocal()
    try:
        # Get a few sample records
        records = db.query(Medicamento).limit(10).all()
        
        print("Checking encoding of database records...\n")
        
        for record in records:
            nome = record.nome_produto or ""
            empresa = record.empresa_detentora_registro or ""
            
            # Check for encoding issues (replacement characters)
            has_issues = False
            if '\ufffd' in nome or '\ufffd' in empresa:
                has_issues = True
                print(f"⚠️  Record ID {record.id} has encoding issues:")
            else:
                print(f"✓ Record ID {record.id} looks good:")
            
            print(f"  NOME: {repr(nome[:60])}")
            print(f"  EMPRESA: {repr(empresa[:60])}")
            print()
            
            if not has_issues:
                # Check if Portuguese characters are present
                portuguese_chars = ['ã', 'ç', 'é', 'ê', 'ô', 'õ', 'á', 'í', 'ó', 'ú']
                has_portuguese = any(char in (nome + empresa).lower() for char in portuguese_chars)
                if has_portuguese:
                    print("  ✓ Contains Portuguese characters correctly")
                print()
                break
        
    finally:
        db.close()

if __name__ == "__main__":
    check_encoding()
