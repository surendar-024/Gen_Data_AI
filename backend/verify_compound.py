import sys
import os
sys.path.append(os.path.join(os.getcwd()))

from nlp_manager.postprocess import build_schema
from nlp_manager.entities import extract_entities
import json

def test_compound():
    prompts = [
        "Give me 100 students with scholarship multiple of 2500 and lower than the fees",
        "Generate 50 students with scholarship greater than 1000 and lower than 50000",
        "fees greater than 50000 and lower than 100000"
    ]
    
    with open("debug_results.txt", "w", encoding="utf-8") as f:
        for text in prompts:
            f.write(f"\n--- TEST: {text} ---\n")
            e = extract_entities(text)
            f.write(f"Domain Extracted: {e.get('domain')}\n")
            f.write(f"Raw Columns Extracted: {e['columns']}\n")
            
            schema = build_schema({'intent': 'generate_tabular_data'}, e, text)
            if "columns" in schema:
                f.write(f"Final Schema Columns: {[c['name'] for c in schema['columns']]}\n")
                for col in schema["columns"]:
                    constraints = {k:v for k,v in col.items() if k not in ('name', 'type', 'aliases', 'output_name', 'choices')}
                    if constraints:
                        f.write(f"  - Col {col['name']} constraints: {constraints}\n")
            else:
                 f.write(f"Schema build returned Clarification Needed!\n")
                 if "invalid_columns" in schema:
                     f.write(f"  Invalid columns: {schema['invalid_columns']}\n")
                 if "message" in schema:
                     f.write(f"  Message: {schema['message']}\n")

if __name__ == "__main__":
    test_compound()
