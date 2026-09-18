import sys
import os
sys.path.append(os.path.join(os.getcwd()))

from nlp_manager.entities import extract_entities
from nlp_manager.postprocess import resolve_columns
import json

prompts = [
    "Give me 100 students with scholarship multiple of 2500 and lower than the fees",
    "Generate 50 students with scholarship greater than 1000 and lower than 50000",
    "fees greater than 50000 and lower than 100000"
]

for text in prompts:
    print(f"\n--- DEBUG: {text} ---")
    e = extract_entities(text)
    print(f"Domain: {e.get('domain')}")
    print(f"Entities: {e.get('columns')}")
    
    resolved = resolve_columns(e.get('columns', []), e.get('domain'))
    print(f"Resolved Cols: {[c['name'] for c in resolved]}")
