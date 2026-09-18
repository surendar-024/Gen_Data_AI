
import time
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from Dataset_Generator.generator import generate_dataset

columns = [
    {"name": "id", "type": "uuid"},
    {"name": "name", "type": "name"},
    {"name": "email", "type": "email"},
    {"name": "age", "type": "integer", "min": 18, "max": 25},
    {"name": "marks", "type": "integer", "min": 0, "max": 100}
]

def benchmark(rows):
    print(f"Generating {rows} records...")
    start_time = time.time()
    try:
        data = generate_dataset(rows=rows, columns=columns)
        end_time = time.time()
        duration = end_time - start_time
        print(f"Success! Time taken: {duration:.2f} seconds.")
        # print first record
        if data:
            print(f"Sample: {data[0]}")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    benchmark(1000000)
