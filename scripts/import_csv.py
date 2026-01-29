import csv
import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# #region agent log
# Use relative path from script location for cross-platform compatibility
LOG_PATH = Path(__file__).parent.parent / ".cursor" / "debug.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
def debug_log(hyp, loc, msg, data=None):
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps({"hypothesisId": hyp, "location": loc, "message": msg, "data": data, "timestamp": datetime.now().isoformat()}, ensure_ascii=False) + "\n")
# #endregion

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

# #region agent log
def clean_string_debug(value, field_name):
    """Debug version of clean_string"""
    original = value
    result = clean_string(value)
    if 'AIRELA' in str(original) or 'LEGRAND' in str(original) or 'VLIDO' in str(result or '') or 'INDSTRIA' in str(result or ''):
        debug_log("H5", "clean_string", f"Checking {field_name}", {"original": repr(original), "result": repr(result), "original_type": type(original).__name__})
    return result
# #endregion


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
                    # #region agent log
                    debug_log("H1", "encoding_detection", f"Encoding used: {encoding}", {"encoding": encoding, "errors_mode": "strict"})
                    # Find a sample with AIRELA or LEGRAND to check encoding
                    for sample_row in csv_data[:500]:
                        emp = sample_row.get('EMPRESA_DETENTORA_REGISTRO', '')
                        sit = sample_row.get('SITUACAO_REGISTRO', '')
                        if 'AIRELA' in emp or 'LEGRAND' in emp:
                            debug_log("H1", "csv_sample_data", "Sample record from CSV", {"empresa": repr(emp), "situacao": repr(sit), "has_U_accent": 'Ú' in emp, "has_A_accent": 'Á' in sit})
                            break
                    # #endregion
                    # Test if encoding is correct by checking for common Portuguese characters (both lower and UPPER case)
                    if csv_data:
                        test_sample = str(csv_data[0])
                        portuguese_chars = ['ã', 'ç', 'é', 'ê', 'ô', 'õ', 'á', 'í', 'ó', 'ú', 
                                           'Ã', 'Ç', 'É', 'Ê', 'Ô', 'Õ', 'Á', 'Í', 'Ó', 'Ú']
                        if any(char in test_sample for char in portuguese_chars):
                            print(f"✓ Encoding {encoding} appears correct (found Portuguese characters)")
                            # #region agent log
                            debug_log("H1_FIX", "encoding_final", f"FINAL encoding selected: {encoding}", {"encoding": encoding, "found_chars": [c for c in portuguese_chars if c in test_sample][:5]})
                            # #endregion
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
                # #region agent log
                empresa_raw = row.get('EMPRESA_DETENTORA_REGISTRO', '')
                situacao_raw = row.get('SITUACAO_REGISTRO', '')
                if 'AIRELA' in empresa_raw or 'LEGRAND' in empresa_raw:
                    debug_log("H2", "before_insert", f"Row {i} before processing", {"empresa_raw": repr(empresa_raw), "situacao_raw": repr(situacao_raw), "empresa_bytes": empresa_raw.encode('utf-8').hex() if empresa_raw else None})
                # #endregion
                
                empresa_clean = clean_string(row.get('EMPRESA_DETENTORA_REGISTRO'))
                situacao_clean = clean_string(row.get('SITUACAO_REGISTRO'))
                
                # #region agent log
                if 'AIRELA' in str(empresa_clean) or 'LEGRAND' in str(empresa_clean):
                    debug_log("H2", "after_clean", f"Row {i} after clean_string", {"empresa_clean": repr(empresa_clean), "situacao_clean": repr(situacao_clean)})
                # #endregion
                
                medicamento = Medicamento(
                    tipo_produto=clean_string(row.get('TIPO_PRODUTO')),
                    nome_produto=clean_string(row.get('NOME_PRODUTO')),
                    data_finalizacao_processo=parse_date(row.get('DATA_FINALIZACAO_PROCESSO')),
                    categoria_regulatoria=clean_string(row.get('CATEGORIA_REGULATORIA')),
                    numero_registro_produto=clean_string(row.get('NUMERO_REGISTRO_PRODUTO')),
                    data_vencimento_registro=parse_date(row.get('DATA_VENCIMENTO_REGISTRO')),
                    numero_processo=clean_string(row.get('NUMERO_PROCESSO')),
                    classe_terapeutica=clean_string(row.get('CLASSE_TERAPEUTICA')),
                    empresa_detentora_registro=empresa_clean,
                    situacao_registro=situacao_clean,
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
        
        # #region agent log
        # Verify data in database after import
        sample = db.query(Medicamento).filter(Medicamento.empresa_detentora_registro.like('%AIRELA%')).first()
        if sample:
            debug_log("H2", "db_verify", "Data in DB after import", {"empresa_in_db": repr(sample.empresa_detentora_registro), "situacao_in_db": repr(sample.situacao_registro)})
        debug_log("H4", "import_completed", "Import finished", {"imported": imported, "errors": errors, "timestamp": datetime.now().isoformat()})
        # #endregion
        
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
