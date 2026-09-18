
import sys
import os
import json

# Add the current directory to sys.path to import local modules
sys.path.append(os.getcwd())

from nlp_manager.entities import extract_entities
from nlp_manager.universal_constraint_parser import parse_universal_constraints
from nlp_manager.postprocess import build_schema

def debug_full_trace():
    prompt = "Generate 50 students: scholarship is 20k, 50k or 0 | GPA follow normal distribution between 0.0 to 10.0 | name ends with 'Kumar' and roll_number like 2024-ST-### | use uniform distribution for marks between 0 to 100 | residence are null"
    
    print(f"--- FULL PROMPT ---\n{prompt}\n")
    
    entities = extract_entities(prompt)
    print("--- EXTRACTED ENTITIES ---")
    print(f"Domain: {entities.get('domain')}")
    print("Segments:")
    for i, seg in enumerate(entities.get('columns', [])):
        print(f"  [{i}] '{seg}'")
    
    intent_result = {"intent": "generate_tabular_data"}
    schema = build_schema(intent_result, entities, prompt)
    
    print("\n--- SCHEMA COLUMNS ---")
    for col in schema.get('columns', []):
        name = col['name']
        # Show all keys except aliases for brevity
        print(f"  {name}: { {k:v for k,v in col.items() if k != 'aliases'} }")

if __name__ == "__main__":
    debug_full_trace()
