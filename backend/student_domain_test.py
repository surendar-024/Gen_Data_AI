
import os
import sys
import json
import logging

# Add the current directory to sys.path
sys.path.append(os.getcwd())

from nlp_manager.entities import extract_entities
from nlp_manager.postprocess import build_schema
from Dataset_Generator.generator import generate_dataset

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("student_test")

def run_student_tests():
    test_cases = [
        {
            "id": "Simple Prompt",
            "prompt": "generate 5 students"
        },
        {
            "id": "Specific Columns",
            "prompt": "10 students with name, email, age and marks"
        },
        {
            "id": "Categorical Constraints",
            "prompt": "20 students: gender is Male or Female. department among CS, IT, ECE. status is Active."
        },
        {
            "id": "Numeric Ranges",
            "prompt": "15 students. age between 18 and 22. marks greater than 75 and less than 95."
        },
        {
            "id": "Prefix/Suffix Constraints",
            "prompt": "10 students. email ends with @edu.in. name starts with Mr. or Ms."
        },
        {
            "id": "Sequential Patterns",
            "prompt": "50 students. id format STU-001. roll_number matches R-2024-###."
        },
        {
            "id": "Uniqueness & Nullability",
            "prompt": "25 students. unique roll_number. email must be unique. middle_name is optional. some addresses are null."
        },
        {
            "id": "Distribution Logic",
            "prompt": "100 students. marks follows normal distribution. GPA follows uniform distribution."
        },
        {
            "id": "Cross-Column Dependencies",
            "prompt": "30 students. scholarship is below fees. graduation_year is higher than enrollment_year."
        },
        {
            "id": "Natural Language Variation",
            "prompt": "I need a dataset of 20 pupils. Their ages should be in between 19 to 21. For their names, please make sure they start with 'A'. Their blood group should be one of A+, B+, or O+."
        },
        {
            "id": "Complex Multi-Constraint",
            "prompt": "Generate 50 students data with id in the STU-2024-001 format, full_name starts with 'S', email ends with @university.ac.in, department among CS, AIDS, CSBS, IT. age between 18 to 25 , gender is M or F. marks follows normal distribution with a minimum of 40 and maximum of 100. graduation_year is 2026. unique phone number. permanent_address can be empty."
        }
    ]

    results = []
    intent_result = {"intent": "generate_tabular_data"}

    print("=== STARTING STUDENT DOMAIN STRESS TEST ===\n")

    for test in test_cases:
        print(f"--- Running Test: {test['id']} ---")
        print(f"Prompt: {test['prompt']}")
        
        try:
            # 1. Extraction
            entities = extract_entities(test['prompt'])
            
            # 2. Schema Building
            schema = build_schema(intent_result, entities, test['prompt'])
            
            # Check for clarification
            if isinstance(schema, dict) and schema.get("status") == "clarification_needed":
                print(f"RESULT: Clarification Needed - {schema['message']}")
                results.append({"id": test['id'], "status": "clarification", "message": schema['message']})
                continue

            # 3. Generation Preview
            # We generate just 3 rows for validation
            data = generate_dataset(
                rows=min(3, schema["rows"]),
                columns=schema["columns"],
                distribution=schema["distribution"],
                domain=schema["domain"]
            )
            
            print(f"RESULT: Success. Generated {schema['rows']} rows.")
            # Basic validation of constraints in the first row
            sample = data[0] if data else {}
            
            results.append({
                "id": test['id'],
                "status": "success",
                "rows_requested": schema["rows"],
                "columns_resolved": [c['name'] for c in schema['columns']],
                "sample_row": sample
            })
            
        except Exception as e:
            print(f"RESULT: FAILED - {str(e)}")
            import traceback
            traceback.print_exc()
            results.append({"id": test['id'], "status": "error", "error": str(e)})

    # Save summary
    with open('student_domain_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n=== TEST COMPLETED ===")
    print(f"Summary saved to student_domain_test_results.json")

if __name__ == "__main__":
    run_student_tests()
