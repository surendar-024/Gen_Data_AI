import sys
import os
sys.path.append(os.path.join(os.getcwd()))

from nlp_manager.postprocess import build_schema
from nlp_manager.entities import extract_entities
from Dataset_Generator.generator import generate_dataset
import json

def test_repro():
    print("--- REPRODUCING USER ISSUES ---")
    
    # Issue 1: Academic Year mapping and "is 3 or 4"
    text = "Give me 10 students with scholarship multiple of 2500, fees greater than 50000, and academic year is 3 or 4."
    entities = extract_entities(text)
    print(f"Entities: {entities}")
    
    intent_result = {"intent": "generate_tabular_data", "confidence": 0.5}
    schema = build_schema(intent_result, entities, text)
    
    print("\n--- SCHEMA ---")
    for col in schema["columns"]:
        print(f"Column: {col['name']} (Output: {col.get('output_name')}) Type: {col['type']}")
        if "choices" in col:
            print(f"  Choices: {col['choices']}")
        if "min" in col:
            print(f"  Min/Max: {col.get('min')} / {col.get('max')}")
        if "multiple_of" in col:
            print(f"  Multiple of: {col['multiple_of']}")

    data = generate_dataset(
        rows=5,
        columns=schema["columns"],
        distribution=schema.get("distribution", "uniform"),
        domain=schema.get("domain", "generic")
    )
    print("\n--- PREVIEW ---")
    print(json.dumps(data, indent=2))

    # Issue 2: Scholarship below value (rounding collision?)
    text2 = "Generate 10 students with scholarship below 1000"
    entities2 = extract_entities(text2)
    schema2 = build_schema(intent_result, entities2, text2)
    print("\n--- SCHEMA 2 (Scholarship below 1000) ---")
    for col in schema2["columns"]:
        if col["name"] == "scholarship":
             print(f"  Min/Max: {col.get('min')} / {col.get('max')}")
             print(f"  Multiple of: {col.get('multiple_of')}")

    data2 = generate_dataset(
        rows=5,
        columns=schema2["columns"]
    )
    print("\n--- PREVIEW 2 ---")
    for row in data2:
        print(f"Scholarship: {row.get('scholarship')}")

    # Issue 3: Dynamic Constraint (not implemented yet, but let's see what happens)
    text3 = "Generate 10 students where scholarship is below the fees"
    entities3 = extract_entities(text3)
    schema3 = build_schema(intent_result, entities3, text3)
    print("\n--- SCHEMA 3 (Scholarship below fees) ---")
    print(json.dumps(schema3, indent=2))

if __name__ == "__main__":
    test_repro()
