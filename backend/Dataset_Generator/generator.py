# Dataset_Generator/generator.py

"""
Main dataset generation engine.

Takes a fully-built schema (rows, columns[], distribution, domain) and
produces a list of row-dicts with realistic values obeying all constraints.
"""

import logging
from .distributions import get_distribution
from .field_types import generate_field

logger = logging.getLogger("dataset_generator.generator")

# Retry limit for unique-column generation to prevent infinite loops
# on columns with low cardinality.
_UNIQUE_RETRY_LIMIT = 1000


def generate_dataset(rows, columns, distribution="uniform", domain="generic"):
    """
    Wrapper to return a full list (backward compatibility).
    """
    return list(generate_dataset_iter(rows, columns, distribution, domain))


def generate_dataset_iter(rows, columns, distribution="uniform", domain="generic"):
    """
    Generator that yields records one by one. 
    Memory-efficient for millions of records.
    """
    dist_func = get_distribution(distribution)

    # 1. Dependency-aware sorting (Simple Topo-sort)
    sorted_cols = []
    visited = set()
    visiting = set()
    
    def visit(c_name):
        if c_name in visited: return
        if c_name in visiting: return

        c_dict = next((cd for cd in columns if cd["name"] == c_name), None)
        if not c_dict: return
        
        visiting.add(c_name)
        deps = []
        if c_dict.get("dynamic_min"): deps.append(c_dict["dynamic_min"])
        if c_dict.get("dynamic_max"): deps.append(c_dict["dynamic_max"])
        
        for d in deps:
            if any(cd["name"] == d for cd in columns):
                visit(d)
            
        visiting.remove(c_name)
        visited.add(c_name)
        sorted_cols.append(c_dict)

    for col in columns:
        visit(col["name"])

    # Track unique values per column
    used_values = {
        col["name"]: set()
        for col in sorted_cols
        if col.get("unique")
    }

    for i in range(rows):
        record = {}
        canonical_record = {}

        for col in sorted_cols:
            col_name = col["name"]
            
            col_run = col.copy()
            if col.get("dynamic_min") and col["dynamic_min"] in canonical_record:
                dyn_val = canonical_record[col["dynamic_min"]]
                col_run["min"] = max(col_run.get("min", float('-inf')), dyn_val)
                
            if col.get("dynamic_max") and col["dynamic_max"] in canonical_record:
                dyn_val = canonical_record[col["dynamic_max"]]
                col_run["max"] = min(col_run.get("max", float('inf')), dyn_val)

            try:
                retries = 0
                while True:
                    value = generate_field(col_run, dist_func, index=i)

                    if col.get("unique"):
                        if value in used_values[col_name]:
                            retries += 1
                            if retries >= _UNIQUE_RETRY_LIMIT:
                                break
                            continue
                        used_values[col_name].add(value)
                    break

                canonical_record[col_name] = value
                record[col.get("output_name", col_name)] = value

            except Exception as exc:
                logger.error("Failed for column '%s': %s", col_name, exc)
                record[col_name] = None

        yield record
