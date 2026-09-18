# dataset_generator/schemas.py

from typing import Dict, List, Any


def normalize_column(col: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a single column specification.
    Ensures all required keys exist.
    """
    return {
        "name": col.get("name"),
        "type": col.get("type", "string"),
        "distribution": col.get("distribution"),
        "range": col.get("range"),
        "nullable": col.get("nullable", False),
        "unique": col.get("unique", False)
    }


def normalize_schema(spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize the entire dataset spec before generation.
    """
    rows = spec.get("rows")
    columns = spec.get("columns", [])

    if not rows or not columns:
        raise ValueError("Invalid dataset specification: rows or columns missing")

    normalized_columns: List[Dict[str, Any]] = []
    for col in columns:
        normalized_columns.append(normalize_column(col))

    return {
        "rows": rows,
        "columns": normalized_columns,
        "distribution": spec.get("distribution"),
        "range": spec.get("range")
    }
# -------------------------
# Domain-based schema presets
# -------------------------

DOMAIN_SCHEMAS = {
    "student": {
        "id": "uuid",
        "name": "string",
        "age": "integer",
        "email": "email",
        "marks": "integer"
    },
    "employee": {
        "id": "uuid",
        "name": "string",
        "email": "email",
        "salary": "integer",
        "department": "string"
    },
    "generic": {}
}



def get_schema(domain: str):
    """
    Returns predefined schema for a given domain.
    """
    if not domain:
        return None

    domain = domain.lower()
    return DOMAIN_SCHEMAS.get(domain)
