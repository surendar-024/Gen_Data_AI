
import os
import sys
import json

# Add the current directory to sys.path
sys.path.append(os.getcwd())

from nlp_manager.entities import extract_entities
from nlp_manager.postprocess import build_schema

def run_stress_test():
    prompts = [
        {
            "id": "Multiple Name Constraints",
            "prompt": "Generate 20 students where name starts with 'A', ends with 'Kumar', and has length between 15 and 25"
        },
        {
            "id": "Embedded Story Prompt",
            "prompt": "I am writing a story about 30 brilliant students. Can you generate their data? They should have GPA follow normal distribution above 9.0, their email must start with 'stu_', and enrollment_year = 2024. Also, make sure their city is among Cambridge, Boston, or Somerville."
        },
        {
            "id": "Cross-Field Dependency",
            "prompt": "40 students where fees is between 100k and 200k, and scholarship smaller than fees"
        },
        {
            "id": "Categorical & Patterns Mix",
            "prompt": "30 students: status Graduated or Suspended, roll_number like GRAD-###-2024, and graduation_year is 2024"
        },
        {
            "id": "Contradictory Logic",
            "prompt": "Generate 10 students: age is 20, but age is 30, and age should be 25"
        },
        {
            "id": "Heavy Segmentation",
            "prompt": "10 students | name ends with 'Devi' | GPA 8.5 | marks follow uniform distribution | scholarship 50k | city lists Delhi, Mumbai | phone 10 characters | unique email "
        },
        {
            "id": "Identity Crisis",
            "prompt": "Generate 50 students. Their names must start with 'Prof.' or 'Dr.', end with 'PhD', and be between 15 and 30 characters long. Also, they must have a unique roll_number that follows the pattern 'EMP-####-EDU' and their email should start with 'admin_'."
        },
        {
            "id": "Financial Audit",
            "prompt": "I need a table of 100 students where fees is between 10k and 50k, but their scholarship must be a multiple of 5000 and always be smaller than their fees. Also, roughly some of their addresses should be null."
        },
        {
            "id": "Mixed Signals",
            "prompt": "Create 30 records: age is 20, but age is 30, and actually age should be 25. Marks follow a normal distribution for math_score but marks follow a uniform distribution for science_score. Graduation year is among 2023, 2024, or 2025."
        },
        {
            "id": "Storyteller 2.0",
            "prompt": "I am writing a novel about 40 brilliant students in India. Can you help me generate their data? Make sure their city lists Delhi, Mumbai, Bangalore, or Chennai. They should have a GPA higher than 9.0 and their enrollment_year must be 2024. Also, for their status, it should be either 'Active' or 'On Leave'."
        },
        {
            "id": "Numeric Stressor",
            "prompt": "Generate 10k rows for students. Their attendance is between 60% and 100% and should be a multiple of 5. All of their middle_name must be null, and their phone number must be exactly 10 characters."
        }
    ]

    results = []
    
    intent_result = {"intent": "generate_tabular_data"}

    for p in prompts:
        print(f"Running Test: {p['id']}")
        entities = extract_entities(p['prompt'])
        schema = build_schema(intent_result, entities, p['prompt'])
        
        # Strip aliases from output for readability
        for col in schema.get('columns', []):
            if 'aliases' in col: del col['aliases']
        
        results.append({
            "id": p['id'],
            "prompt": p['prompt'],
            "segments": entities.get('columns', []),
            "result_schema": schema
        })

    with open('stress_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nStress test completed. Results saved to stress_test_results.json")

if __name__ == "__main__":
    run_stress_test()
