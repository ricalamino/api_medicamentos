#!/usr/bin/env python3
"""Analyze CSV for encoding issues"""
import csv
from pathlib import Path

csv_path = Path(__file__).parent.parent / "DADOS_ABERTOS_MEDICAMENTOS.csv"

print("Analyzing CSV file for encoding issues...\n")

# Try with ISO-8859-1 (detected by chardet)
with open(csv_path, 'r', encoding='iso-8859-1', newline='', errors='replace') as f:
    reader = csv.DictReader(f, delimiter=';')
    
    issues_found = []
    good_records = []
    
    for i, row in enumerate(reader):
        if i >= 100:  # Check first 100 records
            break
            
        nome = row.get('NOME_PRODUTO', '')
        empresa = row.get('EMPRESA_DETENTORA_REGISTRO', '')
        
        # Check for replacement character
        has_replacement = '\ufffd' in nome or '\ufffd' in empresa
        
        # Check for Portuguese characters
        portuguese_chars = ['ã', 'ç', 'é', 'ê', 'ô', 'õ', 'á', 'í', 'ó', 'ú']
        has_portuguese = any(char in (nome + empresa).lower() for char in portuguese_chars)
        
        if has_replacement:
            issues_found.append({
                'row': i + 2,  # +2 because header is row 1, and enumerate starts at 0
                'nome': nome[:60],
                'empresa': empresa[:60]
            })
        elif has_portuguese:
            good_records.append({
                'row': i + 2,
                'nome': nome[:60],
                'empresa': empresa[:60]
            })

print(f"Records analyzed: 100")
print(f"Records with replacement chars (issues): {len(issues_found)}")
print(f"Records with Portuguese chars (good): {len(good_records)}")

if issues_found:
    print("\n⚠️  Records with encoding issues:")
    for issue in issues_found[:5]:  # Show first 5
        print(f"  Row {issue['row']}: {issue['nome']}")
        print(f"           {issue['empresa']}")
    
if good_records:
    print("\n✓ Records with correct encoding:")
    for record in good_records[:5]:  # Show first 5
        print(f"  Row {record['row']}: {record['nome']}")
        print(f"           {record['empresa']}")

print("\n" + "="*60)
if len(issues_found) > len(good_records):
    print("⚠️  WARNING: Many records have encoding issues!")
    print("The CSV file may have been corrupted or saved with wrong encoding.")
    print("You may need to download it again from the source.")
else:
    print("✓ Most records look good. The encoding should work with iso-8859-1 or cp1252.")
