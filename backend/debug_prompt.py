
import sys
import os
import json

# Add current directory to path
sys.path.append(os.getcwd())

from nlp_manager.intent import predict_intent
from nlp_manager.entities import extract_entities
from nlp_manager.postprocess import build_schema

def debug_prompt():
    prompt = "generate me 1 million student data with name, email, age and phone number"
    print(f"DEBUGGING PROMPT: {prompt}")
    
    intent = predict_intent(prompt)
    print(f"Intent: {intent}")
    
    entities = extract_entities(prompt)
    print(f"Entities: {json.dumps(entities, indent=2)}")
    
    schema = build_schema(intent, entities, prompt)
    print(f"Schema: {json.dumps(schema, indent=2)}")

if __name__ == "__main__":
    debug_prompt()
