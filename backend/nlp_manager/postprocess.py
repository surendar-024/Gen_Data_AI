# nlp_manager/postprocess.py

"""
Schema Builder — the ONLY function ``main.py`` should call.

Orchestrates:
    1. Column cleaning & suggestion  (column_suggester)
    2. Column resolution              (column_resolver)
    3. Domain guard                    (domain_guard)
    4. Universal constraint parsing    (universal_constraint_parser)
    5. Row-count extraction            (number_parser)
    6. Constraint merging & safety
"""

import logging
from typing import Dict

from nlp_manager.number_parser import extract_rows
from nlp_manager.column_resolver import resolve_columns
from nlp_manager.column_suggester import clean_and_suggest
from nlp_manager.domain_guard import check_domain_column_conflicts
from nlp_manager.schema_registry import SCHEMA_REGISTRY
from nlp_manager.universal_constraint_parser import parse_universal_constraints

logger = logging.getLogger("nlp_manager.postprocess")


def build_schema(intent_result: Dict, entities: Dict, user_text: str) -> Dict:

    logger.info("build_schema called — user_text=%r", user_text)

    # ---------- Base ----------
    domain = entities.get("domain") or "generic"
    raw_columns = entities.get("columns", [])

    schema = {
        "intent": intent_result.get("intent"),
        "domain": domain,
        "distribution": "uniform",
        "rows": 100,
        "columns": [],
    }

    # ---------- Column Cleaning ----------
    try:
        cleaned_columns, column_suggestions = clean_and_suggest(raw_columns, domain)
    except Exception as exc:
        logger.error("clean_and_suggest failed: %s", exc)
        cleaned_columns, column_suggestions = [], []

    # Pass the actual user-input tokens to resolve_columns so it can preserve aliases/names
    cleaned_input_labels = [s["input"] for s in column_suggestions]
    logger.info("Cleaned labels for resolution: %s", cleaned_input_labels)

    # ---------- Column Resolution ----------
    try:
        schema["columns"] = resolve_columns(cleaned_input_labels, domain)
        
        
        suggest_map = {}
        for s in column_suggestions:
            sug = s["suggested"]
            inp = s["input"]
            if sug not in suggest_map or len(inp) > len(suggest_map[sug]):
                suggest_map[sug] = inp

        for col in schema["columns"]:
            canonical = col["name"]
            input_token = col.pop("input_token", None)
            # If we have a specific input_token (alias) used for this instance, use it
            if input_token:
                col["output_name"] = input_token
            # Fallback to general suggestion mapping if no specific token (should be rare now)
            elif canonical in suggest_map:
                col["output_name"] = suggest_map[canonical]
            else:
                col["output_name"] = canonical
                
    except Exception as exc:
        logger.error("resolve_columns failed: %s", exc)
        schema["columns"] = []

    logger.info("Resolved columns: %s", schema["columns"])

    # ---------- Domain Guard ----------
    try:
        guard = check_domain_column_conflicts(domain, schema["columns"])
        if not guard["valid"]:
            return {
                "status": "clarification_needed",
                "message": (
                    f"The columns {guard['invalid_columns']} "
                    f"do not belong to the '{domain}' domain."
                ),
                "invalid_columns": guard["invalid_columns"],
                "suggested_domains": guard["suggested_domains"],
                "valid_columns_for_domain": list(
                    SCHEMA_REGISTRY.get(domain, SCHEMA_REGISTRY["generic"])["columns"].keys()
                ),
            }
    except Exception as exc:
        logger.error("domain_guard failed: %s", exc)

    # If user typed columns but none resolved → clarification
    if raw_columns and not schema["columns"]:
        return {
            "status": "clarification_needed",
            "message": (
                f"The columns {raw_columns} "
                f"do not belong to the '{domain}' domain."
            ),
            "invalid_columns": raw_columns,
            "suggested_domains": [
                d for d, s in SCHEMA_REGISTRY.items()
                if any(
                    token in s["columns"]
                    for token in " ".join(raw_columns).split()
                )
            ],
            "valid_columns_for_domain": list(
                SCHEMA_REGISTRY.get(domain, SCHEMA_REGISTRY["generic"])["columns"].keys()
            ),
        }

    # Fallback: user gave NO columns at all → use domain defaults
    if not raw_columns and not schema["columns"]:
        schema["columns"] = resolve_columns(["id", "name", "email"], domain)
        if domain not in SCHEMA_REGISTRY:
            schema["domain"] = "generic"

    logger.info("Final columns: %s", schema["columns"])

    # ---------- Constraints ----------
    try:
        # 1. Parse GLOBAL constraints from the full text (rows, distribution)
        full_constraints = parse_universal_constraints(user_text, schema["columns"])
        
        # 2. Parse COLUMN constraints segment-by-segment to prevent greedy swallowing
        # entities["columns"] contains the raw segments ["gender as male or female", "status is...", ...]
        segmented_column_constraints = {}
        for segment in raw_columns:
            # We pass ONLY the segment text but ALL resolved columns
            seg_constraints = parse_universal_constraints(segment, schema["columns"])
            # Merge into our main dictionary
            for col_name, col_data in seg_constraints["columns"].items():
                if col_name not in segmented_column_constraints:
                    segmented_column_constraints[col_name] = {}
                segmented_column_constraints[col_name].update(col_data)

        # Combine: Global from full text, Column from Segments
        constraints = {
            "global": full_constraints["global"],
            "columns": segmented_column_constraints
        }
    except Exception as exc:
        logger.error("parse_universal_constraints failed: %s", exc)
        constraints = {"global": {}, "columns": {}}

    logger.info("Parsed constraints (Segmented): %s", constraints)

    # ---- Rows ----
    # Check constraints["global"] first, then extract from text if missing
    if "rows" in constraints["global"]:
        schema["rows"] = constraints["global"]["rows"]
    else:
        rows = extract_rows(user_text)
        if rows is not None:
            schema["rows"] = rows
        else:
            # Default to 100 rows if columns were resolved
            if schema["columns"]:
                schema["rows"] = 100
            else:
                return {
                    "status": "clarification_needed",
                    "message": (
                        "You did not specify how many rows to generate. "
                        "Please specify the number of rows (e.g., 20, 50), "
                        "or reply 'default' to generate 100 rows."
                    ),
                    "expected_input": "row_count",
                    "default": 100,
                }

    # ---- Distribution ----
    if "distribution" in constraints["global"]:
        schema["distribution"] = constraints["global"]["distribution"]

    # ---- Column constraints ----
    for col in schema["columns"]:
        res_key = col.get("output_name", col["name"])
        if res_key in constraints["columns"]:
            col.update(constraints["columns"][res_key])

    # ---------- Final Safety ----------
    try:
        schema["rows"] = int(schema["rows"])
        if schema["rows"] <= 0:
            raise ValueError
    except (ValueError, TypeError):
        schema["rows"] = 100  # safe default instead of None

    return schema
