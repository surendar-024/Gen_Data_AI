# dataset_generator/utils.py

import logging
import random

# Logger for dataset generator
logger = logging.getLogger("dataset_generator")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(message)s",
    "%Y-%m-%d %H:%M:%S"
)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def maybe_null(value, nullable: bool):
    """
    Randomly returns None if column is nullable.
    """
    if nullable and random.random() < 0.1:  # 10% nulls
        return None
    return value


def ensure_unique(values: list):
    """
    Ensures values are unique (best-effort).
    """
    seen = set()
    unique_values = []

    for v in values:
        if v in seen:
            continue
        seen.add(v)
        unique_values.append(v)

    return unique_values


def log_schema(schema: dict):
    logger.info(f"USING SCHEMA: {schema}")


def log_generation_complete(rows: int, columns: int):
    logger.info(f"DATASET GENERATED → Rows: {rows}, Columns: {columns}")
