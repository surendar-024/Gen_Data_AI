# nlp_manager/constraints.py
from typing import Dict, Any
from Dataset_Generator.domain_rules import DOMAIN_RULES
from Dataset_Generator.type_inference import infer_type


def apply_constraints(domain: str, columns: list) -> list:
    enriched_columns = []
    domain_rules = DOMAIN_RULES.get(domain, {})

    for col in columns:
        if isinstance(col, dict):
            enriched_columns.append(col)
            continue

        col_name = col.lower()
        rule = domain_rules.get(col_name, {})

        column_spec: Dict[str, Any] = {
            "name": col,
            "type": rule.get("type", infer_type(col_name))
        }

        if "min" in rule:
            column_spec["min"] = rule["min"]
        if "max" in rule:
            column_spec["max"] = rule["max"]

        enriched_columns.append(column_spec)

    return enriched_columns

