#!/usr/bin/env python3
"""Verify encoding issues and reimport if needed"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Medicamento

def check_encoding_issues():
    """Check if there are encoding issues in the database"""
    db: Session = SessionLocal()
    
    try:
        # Check a few records
        records = db.query(Medicamento).limit(100).all()
        
        issues = 0
        good = 0
        
        for record in records:
            empresa = record.empresa_detentora_registro or ""
            situacao = record.situacao_registro or ""
            
            # Check for missing Portuguese characters (encoding issues)
            has_issue = False
            if 'INDSTRIA' in empresa or 'FARMACUTICA' in empresa or 'VLIDO' in situacao:
                has_issue = True
                issues += 1
                if issues <= 3:
                    print(f"⚠️  Issue found - ID {record.id}:")
                    print(f"   EMPRESA: {empresa[:70]}")
                    print(f"   SITUACAO: {situacao}")
            else:
                # Check if it has correct Portuguese characters
                if 'Ú' in empresa or 'Ê' in empresa or 'Á' in situacao:
                    good += 1
        
        print(f"\n{'='*60}")
        print(f"Records checked: {len(records)}")
        print(f"Records with encoding issues: {issues}")
        print(f"Records with correct encoding: {good}")
        print(f"{'='*60}\n")
        
        if issues > 0:
            print("❌ Encoding issues detected!")
            print("You need to reimport the data.")
            print("\nRun: python3 scripts/import_csv.py")
            return True
        else:
            print("✓ No encoding issues found!")
            return False
            
    finally:
        db.close()

if __name__ == "__main__":
    has_issues = check_encoding_issues()
    sys.exit(1 if has_issues else 0)
