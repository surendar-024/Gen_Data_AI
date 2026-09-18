import sys
import os
sys.path.append(os.path.join(os.getcwd()))

from nlp_manager.column_suggester import clean_and_suggest
import json

def test():
    raw_columns = ["scholarship is below the fees and fees are between 10000 and 20000"]
    domain = "student"
    
    cols, suggestions = clean_and_suggest(raw_columns, domain)
    
    print(f"Segment: {raw_columns[0]}")
    print(f"Resolved Columns: {cols}")
    print(f"Suggestions: {json.dumps(suggestions, indent=2)}")

if __name__ == "__main__":
    test()
