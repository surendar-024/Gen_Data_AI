# nlp_manager/domain_guard.py

from nlp_manager.schema_registry import SCHEMA_REGISTRY


def check_domain_column_conflicts(domain: str, columns: list):
    """
    Checks whether resolved columns belong to the selected domain.

    Returns:
    {
        "valid": bool,
        "invalid_columns": list,
        "suggested_domains": list
    }
    """

    registry = SCHEMA_REGISTRY
    domain_schema = registry.get(domain, registry["generic"])
    valid_columns = set(domain_schema["columns"].keys())

    invalid = []
    for col in columns:
        name = col["name"]
        if name not in valid_columns:
            invalid.append(name)

    if not invalid:
        return {
            "valid": True,
            "invalid_columns": [],
            "suggested_domains": []
        }

    # suggest domains where these columns DO exist
    suggested_domains = []
    for d, schema in registry.items():
        schema_cols = set(schema["columns"].keys())
        if any(col in schema_cols for col in invalid):
            suggested_domains.append(d)

    return {
        "valid": False,
        "invalid_columns": invalid,
        "suggested_domains": suggested_domains
    }
