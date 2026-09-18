
import sys
import os
import json

# Add the current directory to sys.path to import local modules
sys.path.append(os.getcwd())

from nlp_manager.entities import extract_entities
from nlp_manager.postprocess import build_schema

def test_reproduction():
    prompt = "Generate 200 records: gpa follow a normal distribution between 0.0 to 10.0, but use uniform distribution for marks between 0 to 100"
    
    print(f"Testing prompt: {prompt}")
    entities = extract_entities(prompt)
    print("\nRaw Columns from Segmenter:")
    for c in entities.get("columns", []):
        print(f"  - '{c}'")
    
    intent_result = {"intent": "generate_tabular_data", "confidence": 0.99}
    schema = build_schema(intent_result, entities, prompt)
    
    print("\nColumn Suggestions:")
    for sug in schema.get("column_suggestions", []):
        print(f"  - Input: {sug['input']}, Suggested: {sug['suggested']}, Confidence: {sug['confidence']}")
    
    print("\nParsed Schema Columns:")
    for col in schema.get("columns", []):
        name = col["name"]
        # Filter out metadata for clarity
        constraints = {k: v for k, v in col.items() if k not in ["aliases", "name", "type", "output_name", "unique", "nullable"]}
        print(f"  {name}: {json.dumps(constraints)}")

if __name__ == "__main__":
    test_reproduction()
