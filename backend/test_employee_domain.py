
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_employee_complex():
    prompt = "Generate 50 employees with id, employee_code like CORP-001, name starts with Dr., email, personal_email, department among Engineering, Sales, salary between 50k to 150k, bonus 10%, work_mode, performance_rating."
    print(f"Testing prompt: {prompt}")
    
    response = requests.post(f"{BASE_URL}/generate", json={"prompt": prompt})
    if response.status_code == 200:
        res = response.json()
        print(f"Detected Domain: {res['schema']['domain']}")
        print(f"Schema Columns: {[c['name'] for c in res['schema']['columns']]}")
        print(f"Sample Row: {res['preview'][0]}")
    else:
        print(f"FAILED: {response.text}")

if __name__ == "__main__":
    test_employee_complex()
