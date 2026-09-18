
import sys
import os
import json

# Add the current directory to sys.path to import local modules
sys.path.append(os.getcwd())

from nlp_manager.universal_constraint_parser import parse_universal_constraints

def test_marks_parsing():
    # Simulate a resolved schema structure for a few columns
    schema_cols = [
        {"name": "gpa", "aliases": ["gpa"]},
        {"name": "marks", "aliases": ["marks", "score"]},
        {"name": "scholarship", "aliases": ["scholarship"]},
        {"name": "address", "aliases": ["address", "residence"]},
        {"name": "name", "aliases": ["name"]},
        {"name": "roll_number", "aliases": ["roll_number"]}
    ]
    
    # The problematic segment as split by entities.py
    segment = "but use uniform distribution for marks between 0 to 100"
    
    print(f"Testing segment: '{segment}'")
    
    constraints = parse_universal_constraints(segment, schema_cols)
    
    print("\nParsed Constraints for 'marks':")
    print(json.dumps(constraints["columns"].get("marks", {}), indent=2))
    
    print("\nFull Result:")
    print(json.dumps(constraints, indent=2))

if __name__ == "__main__":
    test_marks_parsing()
