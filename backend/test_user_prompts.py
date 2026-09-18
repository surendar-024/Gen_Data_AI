
import sys
import os
import logging
import json

# Add current directory to path
sys.path.append(os.getcwd())

from nlp_manager.entities import extract_entities
from nlp_manager.postprocess import build_schema
from Dataset_Generator.generator import generate_dataset

# Setup logging
logging.basicConfig(level=logging.INFO)

prompts = [
    "Generate 100 students with id in the STU-001 format and name.",
    "Create 50 records where roll_number follows the R-2024-### pattern",
    "Generate 20 employees. Their staff_id should be formatted like EMP_1001",
    "10 students: name starts with 'Dr.', email ends with '@edu.in', and age is between 20 to 25",
    "Give me 30 students where department is either 'CS' or 'IT', and marks are above 80",
    "Generate 15 employees with salary between 50k and 150k, and department is set to 'Engineering'",
    "Generate 200 records: attendance is normally distributed with a minimum of 60",
    "I need a dataset of 25 pupils. Make sure their blood group is one of A+, B+, or O+. Also, unique email IDs",
    "30 students: graduation_year is 2025. fees greater than 100k. Scholarship is below fees",
    "Generate 50 students. ID format STU-2024-001. Name starts with 'A' or 'S'. Email suffix is @university.edu. Department is among CS, AI, or Data Science. Age 18-22. Marks follow normal distribution between 40 and 100. Graduation year set to 2026. Unique roll_number and phone"
]

results = []
intent_result = {"intent": "generate_tabular_data"}

for prompt in prompts:
    print(f"\n--- Testing: {prompt} ---")
    entities = extract_entities(prompt)
    schema = build_schema(intent_result, entities, prompt)
    
    if isinstance(schema, dict) and schema.get("status") == "clarification_needed":
        print(f"CLARIFICATION: {schema['message']}")
        results.append({"prompt": prompt, "status": "clarification", "schema": schema})
        continue

    data = generate_dataset(
        rows=min(2, schema["rows"]),
        columns=schema["columns"],
        distribution=schema["distribution"],
        domain=schema["domain"]
    )
    
    print(f"Success. Rows: {schema['rows']}")
    print(f"Constraints: {json.dumps(schema.get('constraints', {}), indent=2)}")
    sample = data[0] if data else {}
    print(f"Sample Row: {sample}")
    
    results.append({
        "prompt": prompt,
        "status": "success",
        "rows": schema["rows"],
        "sample": sample,
        "schema": schema
    })

with open('user_issue_test_results.json', 'w') as f:
    json.dump(results, f, indent=2)
