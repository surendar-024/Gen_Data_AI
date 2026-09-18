
import time
from faker import Faker
import random

faker = Faker("en_IN")

def test_speed(rows):
    print(f"Testing speed for {rows} records...")
    start = time.time()
    for i in range(rows):
        name = faker.name()
        email = f"{faker.user_name()}.{i}@example.com"
        if i % 100000 == 0:
            print(f"Progress: {i}")
    end = time.time()
    print(f"Total time: {end - start:.2f} seconds")

if __name__ == "__main__":
    test_speed(1000000)
