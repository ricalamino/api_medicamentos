#!/usr/bin/env python3
"""Test script to check CSV encoding"""
import csv
import sys
from pathlib import Path

csv_path = Path(__file__).parent.parent / "DADOS_ABERTOS_MEDICAMENTOS.csv"

encodings = ['cp1252', 'iso-8859-1', 'latin-1', 'utf-8']

for encoding in encodings:
    try:
        with open(csv_path, 'r', encoding=encoding, newline='') as f:
            reader = csv.DictReader(f, delimiter=';')
            first_row = next(reader)
            
            nome = first_row.get('NOME_PRODUTO', '')
            empresa = first_row.get('EMPRESA_DETENTORA_REGISTRO', '')
            categoria = first_row.get('CATEGORIA_REGULATORIA', '')
            
            # Check for Portuguese characters
            sample_text = nome + empresa + categoria
            has_portuguese = any(char in sample_text for char in ['ã', 'ç', 'é', 'ê', 'ô', 'õ', 'á', 'í', 'ó', 'ú', 'Ã', 'Ç', 'É', 'Ê', 'Ô', 'Õ', 'Á', 'Í', 'Ó', 'Ú'])
            
            print(f"\n{'='*60}")
            print(f"Encoding: {encoding}")
            print(f"NOME_PRODUTO: {repr(nome[:80])}")
            print(f"EMPRESA: {repr(empresa[:80])}")
            print(f"CATEGORIA: {repr(categoria[:80])}")
            print(f"Has Portuguese chars: {has_portuguese}")
            
            if has_portuguese:
                print(f"✓ {encoding} appears to be correct!")
                break
    except Exception as e:
        print(f"\nEncoding {encoding} failed: {e}")
