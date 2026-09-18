from nlp_manager.postprocess import build_schema
from nlp_manager.entities import extract_entities
import json

def test_prompt(prompt):
    print(f"\n--- TEST: {prompt} ---")
    
    # 1. Extract entities (simulating real pipeline)
    entities = extract_entities(prompt)
    print(f"Entities Extracted: {entities}")
    
    # 2. Build schema
    # Use dummy intent results
    intent_result = {"intent": "generate_tabular_data", "confidence": 0.99}
    schema = build_schema(intent_result, entities, prompt)
    
    if schema.get("status") == "clarification_needed":
        print(f"Schema build returned Clarification Needed!")
        print(f"  Message: {schema['message']}")
        return

    # Print only relevant column data
    output = {
        "domain": schema.get("domain"),
        "rows": schema.get("rows"),
        "columns": []
    }
    for col in schema.get("columns", []):
        c_data = {k: v for k, v in col.items() if k not in ["type", "aliases", "output_name"]}
        output["columns"].append(c_data)
    
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    prompts = [
        "50 records with roll_number formatted like 2024-ST-###, enrollment_year is 2023, study year is 2, and email ends with @university.edu"
    ]
    results = []
    for p in prompts:
        entities = extract_entities(p)
        intent_result = {"intent": "generate_tabular_data", "confidence": 0.99}
        schema = build_schema(intent_result, entities, p)
        results.append({"prompt": p, "schema": schema})
    
    with open("schema_test_output.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print("Results saved to schema_test_output.json")
