#!/usr/bin/env python3
"""Detect CSV file encoding and check for issues"""
import sys
from pathlib import Path

csv_path = Path(__file__).parent.parent / "DADOS_ABERTOS_MEDICAMENTOS.csv"

print("="*60)
print("Detecting CSV file encoding...")
print("="*60)

# Try chardet if available
try:
    import chardet
    with open(csv_path, 'rb') as f:
        raw_data = f.read(50000)  # Read first 50KB
        result = chardet.detect(raw_data)
        print(f"\nChardet detection:")
        print(f"  Encoding: {result['encoding']}")
        print(f"  Confidence: {result['confidence']:.2%}")
        print(f"  Language: {result.get('language', 'N/A')}")
except ImportError:
    print("\nChardet not available. Install with: pip install chardet")
except Exception as e:
    print(f"\nError using chardet: {e}")

# Test different encodings manually
print("\n" + "="*60)
print("Testing different encodings:")
print("="*60)

encodings = ['cp1252', 'iso-8859-1', 'latin-1', 'utf-8', 'utf-8-sig']

for encoding in encodings:
    try:
        with open(csv_path, 'r', encoding=encoding, newline='') as f:
            # Read first line
            first_line = f.readline()
            second_line = f.readline()
            
            # Check for Portuguese characters
            sample = first_line + second_line
            portuguese_chars = ['ã', 'ç', 'é', 'ê', 'ô', 'õ', 'á', 'í', 'ó', 'ú', 
                              'Ã', 'Ç', 'É', 'Ê', 'Ô', 'Õ', 'Á', 'Í', 'Ó', 'Ú']
            has_portuguese = any(char in sample for char in portuguese_chars)
            
            # Check for replacement characters (encoding errors)
            has_replacements = '\ufffd' in sample or '' in sample
            
            status = "✓" if has_portuguese and not has_replacements else "✗"
            print(f"\n{status} {encoding}:")
            print(f"  Has Portuguese chars: {has_portuguese}")
            print(f"  Has replacement chars: {has_replacements}")
            
            if has_portuguese and not has_replacements:
                # Show sample
                sample_clean = sample[:100].replace('\n', ' ')
                print(f"  Sample: {sample_clean}")
                print(f"  → This encoding works correctly!")
                
    except UnicodeDecodeError as e:
        print(f"\n✗ {encoding}: Failed - {e}")
    except Exception as e:
        print(f"\n✗ {encoding}: Error - {e}")

print("\n" + "="*60)
print("Recommendation:")
print("="*60)
print("Use the encoding that shows ✓ and has Portuguese characters.")
print("The import script should use: cp1252 or iso-8859-1")
