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
    """Clean string values"""
    if not value:
        return None
    value = str(value).strip()
    if value == "" or value == 'None':
        return None
    return value


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
        
        # Read CSV with different encodings (ISO-8859-1 detected by chardet, try it first)
        encodings = ['iso-8859-1', 'cp1252', 'latin-1', 'utf-8']
        csv_data = None
        used_encoding = None
        
        for encoding in encodings:
            try:
                # Use 'strict' or 'ignore' instead of 'replace' to avoid replacement characters
                with open(csv_path, 'r', encoding=encoding, newline='', errors='strict') as f:
                    # Try to detect if it's semicolon or comma separated
                    sample = f.read(1024)
                    f.seek(0)
                    delimiter = ';' if ';' in sample else ','
                    f.seek(0)
                    reader = csv.DictReader(f, delimiter=delimiter)
                    csv_data = list(reader)
                    used_encoding = encoding
                    print(f"Successfully read CSV with encoding: {encoding}")
                    # Test if encoding is correct by checking for common Portuguese characters (both lower and UPPER case)
                    if csv_data:
                        test_sample = str(csv_data[0])
                        portuguese_chars = ['ã', 'ç', 'é', 'ê', 'ô', 'õ', 'á', 'í', 'ó', 'ú', 
                                           'Ã', 'Ç', 'É', 'Ê', 'Ô', 'Õ', 'Á', 'Í', 'Ó', 'Ú']
                        if any(char in test_sample for char in portuguese_chars):
                            print(f"✓ Encoding {encoding} appears correct (found Portuguese characters)")
                            break
            except UnicodeDecodeError:
                # Try with 'ignore' if strict fails
                try:
                    with open(csv_path, 'r', encoding=encoding, newline='', errors='ignore') as f:
                        sample = f.read(1024)
                        f.seek(0)
                        delimiter = ';' if ';' in sample else ','
                        f.seek(0)
                        reader = csv.DictReader(f, delimiter=delimiter)
                        csv_data = list(reader)
                        used_encoding = encoding
                        print(f"Successfully read CSV with encoding: {encoding} (using errors='ignore')")
                        if csv_data:
                            test_sample = str(csv_data[0])
                            portuguese_chars = ['ã', 'ç', 'é', 'ê', 'ô', 'õ', 'á', 'í', 'ó', 'ú', 
                                               'Ã', 'Ç', 'É', 'Ê', 'Ô', 'Õ', 'Á', 'Í', 'Ó', 'Ú']
                            if any(char in test_sample for char in portuguese_chars):
                                print(f"✓ Encoding {encoding} appears correct")
                                break
                except Exception as e:
                    print(f"Failed to read with encoding {encoding}: {e}")
                    continue
            except Exception as e:
                print(f"Failed to read with encoding {encoding}: {e}")
                continue
        
        if csv_data is None:
            print("Error: Could not read CSV with any encoding")
            return
        
        print(f"Found {len(csv_data)} rows to import")
        
        # Check for existing data
        existing_count = db.query(Medicamento).count()
        if existing_count > 0:
            print(f"\nWarning: Found {existing_count} existing records in database.")
            print("Clearing existing data to reimport with correct encoding...")
            db.query(Medicamento).delete()
            db.commit()
            print("Existing data cleared.")
        
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
