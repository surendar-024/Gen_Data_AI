
import json

def verify_stress():
    try:
        with open('stress_test_results.json', 'r') as f:
            results = json.load(f)
        
        for t in results:
            print(f"\n{'='*60}")
            print(f"TEST: {t['id']}")
            print(f"PROMPT: {t['prompt']}")
            print(f"SEGMENTS: {t['segments']}")
            print(f"{'-'*60}")
            for col in t['result_schema']['columns']:
                # Show name and important constraints
                constraints = {k: v for k, v in col.items() if k not in ['name', 'output_name', 'type']}
                if constraints:
                    print(f"  {col['name']}: {constraints}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_stress()
