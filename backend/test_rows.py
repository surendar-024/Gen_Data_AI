
import sys
import os
import re
import logging

logging.basicConfig(level=logging.INFO)

# Add current directory to path
sys.path.append(os.getcwd())

from nlp_manager.entities import extract_entities
from nlp_manager.number_parser import extract_rows
from nlp_manager.universal_constraint_parser import parse_universal_constraints

def test_prompt():
    prompt = "generate me 1 million student data with name, email, age and phone number"
    print(f"PROMPT: {prompt}")
    
    segments = re.split(r'\s+(?:with|:)\s+', prompt, maxsplit=1)
    print(f"Split segments: {segments}")
    
    entities = extract_entities(prompt)
    print(f"Entities: {entities}")
    
    rows = extract_rows(prompt)
    print(f"Rows from number_parser: {rows}")
    
    # Simulate schema build for rows
    resolved_cols = [{"name": "name"}, {"name": "email"}, {"name": "age"}, {"name": "phone"}]
    constraints = parse_universal_constraints(prompt, resolved_cols)
    print(f"Rows from constraints parser: {constraints['global'].get('rows')}")

if __name__ == "__main__":
    test_prompt()
