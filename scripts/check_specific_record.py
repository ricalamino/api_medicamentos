#!/usr/bin/env python3
"""Check specific record in CSV"""
import csv
from pathlib import Path

csv_path = Path(__file__).parent.parent / "DADOS_ABERTOS_MEDICAMENTOS.csv"

print("Searching for LEGRAND in CSV...\n")

# Try with ISO-8859-1
with open(csv_path, 'r', encoding='iso-8859-1', newline='') as f:
    reader = csv.DictReader(f, delimiter=';')
    
    found = []
    for i, row in enumerate(reader):
        empresa = row.get('EMPRESA_DETENTORA_REGISTRO', '')
        situacao = row.get('SITUACAO_REGISTRO', '')
        
        if 'LEGRAND' in empresa.upper():
            found.append({
                'row': i + 2,
                'empresa': empresa,
                'situacao': situacao,
                'nome': row.get('NOME_PRODUTO', '')
            })
            if len(found) >= 3:
                break

if found:
    print("Found records with LEGRAND:\n")
    for record in found:
        print(f"Row {record['row']}:")
        print(f"  EMPRESA: {repr(record['empresa'])}")
        print(f"  SITUACAO: {repr(record['situacao'])}")
        print(f"  NOME: {repr(record['nome'][:50])}")
        print()
        
    # Check for Portuguese characters
    empresa_text = found[0]['empresa']
    situacao_text = found[0]['situacao']
    
    print("Character analysis:")
    print(f"  'Ú' in empresa: {'Ú' in empresa_text or 'ú' in empresa_text}")
    print(f"  'Á' in situacao: {'Á' in situacao_text or 'á' in situacao_text}")
    print(f"  Raw bytes (first 100): {empresa_text.encode('iso-8859-1')[:100]}")
else:
    print("No records with LEGRAND found")
