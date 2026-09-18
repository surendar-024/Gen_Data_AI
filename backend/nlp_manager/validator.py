# nlp_manager/validator.py

import logging
from Dataset_Generator.domain_rules import DOMAIN_RULES
from nlp_manager.schema_registry import SCHEMA_REGISTRY

logger = logging.getLogger("nlp_manager.validator")


class SchemaValidationError(Exception):
    """Raised when the final schema is invalid."""
    pass


def validate_schema(schema: dict):
    # ---- Rows ----
    rows = schema.get("rows")

    # Allow temporary None when waiting for user clarification
    if rows is None:
        return

    if not isinstance(rows, int) or rows <= 0:
        raise SchemaValidationError(f"Invalid row count: {rows!r}")

    # ---- Columns ----
    domain = schema.get("domain", "generic")
    columns = schema.get("columns", [])

    if not columns:
        raise SchemaValidationError("No columns provided")

    domain_rules = DOMAIN_RULES.get(domain, {})

    for col in columns:
        if not isinstance(col, dict):
            raise SchemaValidationError(
                f"Column must be a dictionary, got {type(col).__name__}"
            )

        col_name = col.get("name")
        col_type = col.get("type")

        if not col_name:
            raise SchemaValidationError("Column without name detected")
        if not col_type:
            raise SchemaValidationError(f"Column '{col_name}' has no type")

        # ---- Dynamic range validation from DOMAIN_RULES ----
        rule = domain_rules.get(col_name)
        if rule:
            _validate_range(col, rule, col_name)

        # ---- Choice column sanity ----
        if col_type == "choice":
            choices = col.get("choices")
            if not choices:
                logger.warning(
                    "Choice column '%s' has no choices list — "
                    "generation will return None.",
                    col_name,
                )


def _validate_range(col: dict, rule: dict, col_name: str):
    """
    Ensure user-supplied min/max don't exceed domain hard limits.
    If they do, clamp them and log a warning.
    """
    domain_min = rule.get("min")
    domain_max = rule.get("max")

    if domain_min is not None and "min" in col:
        if col["min"] < domain_min:
            logger.warning(
                "Column '%s' min=%s below domain minimum %s — clamping.",
                col_name, col["min"], domain_min,
            )
            col["min"] = domain_min

    if domain_max is not None and "max" in col:
        if col["max"] > domain_max:
            logger.warning(
                "Column '%s' max=%s above domain maximum %s — clamping.",
                col_name, col["max"], domain_max,
            )
            col["max"] = domain_max

    # Ensure min <= max after any clamping
    if "min" in col and "max" in col:
        if col["min"] > col["max"]:
            logger.warning(
                "Column '%s' has min > max (%s > %s) — swapping.",
                col_name, col["min"], col["max"],
            )
            col["min"], col["max"] = col["max"], col["min"]
