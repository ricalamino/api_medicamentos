import csv
import sys
import os
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.models import Medicamento


def parse_date(date_str):
    """Parse date from DD/MM/YYYY format"""
    if not date_str or date_str.strip() == "":
        return None
    try:
        return datetime.strptime(date_str.strip(), "%d/%m/%Y").date()
    except (ValueError, AttributeError):
        return None


def clean_string(value):
    """Clean string values, handling encoding issues"""
    if not value:
        return None
    value = value.strip()
    if value == "":
        return None
    # Try to fix common encoding issues
    try:
        # Try to decode as latin-1 and re-encode as utf-8
        value = value.encode('latin-1').decode('utf-8', errors='ignore')
    except:
        pass
    return value if value else None


def import_csv(csv_path: str, batch_size: int = 1000):
    """Import CSV file to database"""
    db: Session = SessionLocal()
    
    try:
        # Initialize database
        print("Initializing database...")
        init_db()
        
        # Check if file exists
        if not os.path.exists(csv_path):
            print(f"Error: File {csv_path} not found")
            return
        
        print(f"Reading CSV file: {csv_path}")
        
        # Read CSV with different encodings
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        csv_data = None
        
        for encoding in encodings:
            try:
                with open(csv_path, 'r', encoding=encoding, newline='') as f:
                    # Try to detect if it's semicolon or comma separated
                    sample = f.read(1024)
                    f.seek(0)
                    delimiter = ';' if ';' in sample else ','
                    f.seek(0)
                    reader = csv.DictReader(f, delimiter=delimiter)
                    csv_data = list(reader)
                    print(f"Successfully read CSV with encoding: {encoding}")
                    break
            except UnicodeDecodeError:
                continue
        
        if csv_data is None:
            print("Error: Could not read CSV with any encoding")
            return
        
        print(f"Found {len(csv_data)} rows to import")
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        # print("Clearing existing data...")
        # db.query(Medicamento).delete()
        # db.commit()
        
        # Import in batches
        batch = []
        imported = 0
        errors = 0
        
        for i, row in enumerate(csv_data, 1):
            try:
                medicamento = Medicamento(
                    tipo_produto=clean_string(row.get('TIPO_PRODUTO')),
                    nome_produto=clean_string(row.get('NOME_PRODUTO')),
                    data_finalizacao_processo=parse_date(row.get('DATA_FINALIZACAO_PROCESSO')),
                    categoria_regulatoria=clean_string(row.get('CATEGORIA_REGULATORIA')),
                    numero_registro_produto=clean_string(row.get('NUMERO_REGISTRO_PRODUTO')),
                    data_vencimento_registro=parse_date(row.get('DATA_VENCIMENTO_REGISTRO')),
                    numero_processo=clean_string(row.get('NUMERO_PROCESSO')),
                    classe_terapeutica=clean_string(row.get('CLASSE_TERAPEUTICA')),
                    empresa_detentora_registro=clean_string(row.get('EMPRESA_DETENTORA_REGISTRO')),
                    situacao_registro=clean_string(row.get('SITUACAO_REGISTRO')),
                    principio_ativo=clean_string(row.get('PRINCIPIO_ATIVO'))
                )
                batch.append(medicamento)
                
                if len(batch) >= batch_size:
                    db.bulk_save_objects(batch)
                    db.commit()
                    imported += len(batch)
                    print(f"Imported {imported} rows...")
                    batch = []
            except Exception as e:
                errors += 1
                if errors <= 10:  # Print first 10 errors
                    print(f"Error importing row {i}: {e}")
                continue
        
        # Import remaining batch
        if batch:
            db.bulk_save_objects(batch)
            db.commit()
            imported += len(batch)
        
        print(f"\nImport completed!")
        print(f"Successfully imported: {imported} rows")
        print(f"Errors: {errors} rows")
        
    except Exception as e:
        print(f"Error during import: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Default CSV path
    csv_path = os.path.join(
        Path(__file__).parent.parent,
        "DADOS_ABERTOS_MEDICAMENTOS.csv"
    )
    
    # Allow custom path as argument
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    
    import_csv(csv_path)
