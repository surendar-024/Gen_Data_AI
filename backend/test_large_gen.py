
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_generate_large():
    prompt = "Generate 1.1 million students data with id and name"
    print(f"Testing prompt: {prompt}")
    
    # 1. Test standard generate (should be capped)
    response = requests.post(f"{BASE_URL}/generate", json={"prompt": prompt})
    if response.status_code == 200:
        res = response.json()
        print(f"Preview rows: {len(res['preview'])}")
        print(f"Full dataset available: {res['full_dataset_available']}")
        print(f"Message: {res['message']}")
    else:
        print(f"Generate failed: {response.text}")

def test_download_stream():
    prompt = "Generate 5000 students data with id and name"
    print(f"\nTesting download for: {prompt}")
    
    # 2. Test download (streaming)
    with requests.post(f"{BASE_URL}/download", json={"prompt": prompt}, stream=True) as r:
        r.raise_for_status()
        count = 0
        for line in r.iter_lines():
            if line:
                count += 1
        print(f"Total lines in CSV (including header): {count}")

if __name__ == "__main__":
    try:
        test_generate_large()
        test_download_stream()
    except Exception as e:
        print(f"Test failed: {e}. Is the server running?")
