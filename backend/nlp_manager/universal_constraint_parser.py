# nlp_manager/universal_constraint_parser.py

"""
Universal Constraint Parser — Production-Ready
===============================================
Extracts constraints from natural-language user prompts and maps them to
resolved column specs.  Handles 12 constraint types and is fully
domain-agnostic (works for student, employee, or any future domain).

Design principles
-----------------
* Each constraint type is a **separate function** → easy to test, maintain,
  and extend.
* All regex patterns are **pre-compiled** at module level for performance.
* Column-name matching is **fuzzy** — handles multi-word names such as
  "roll number" → ``roll_number`` and singular/plural variants.
* Every parser is wrapped in try/except — malformed text is logged and
  skipped, never crashes.
"""

import re
import logging
from collections import defaultdict

logger = logging.getLogger("nlp_manager.constraint_parser")

_STOP_PERIOD = r'\.\s+(?=[A-Z]|Their|They|Also|But|Please|Make|Then|Finally|Moreover)'
_STOP_BASE = r'(?=\s+(?:and|but|with|is|are|should|must|like|follow|follows|normally|uniformly|unique|unique)\b|[,;|]|' + _STOP_PERIOD + r'|$)'

# Specific stops: don't stop at keywords that are part of the current regex
_STOP_VAL = r'(?=\s+(?:and|but|with|starts?\s+with|ends?\s+with|pattern|format|length|between|is|are|should|must|like|follow|follows|normally|uniformly|unique|unique)\b|[,;|]|' + _STOP_PERIOD + r'|$)'

# Cat stop: allows commas (for choice lists) but stops at keywords or major punctuation
_STOP_CAT = r'(?=\s+(?:and|but|with|starts?\s+with|ends?\s+with|pattern|format|length|between|is|are|should|must|like|follow|follows|normally|uniformly|unique|unique)\b|[;|]|' + _STOP_PERIOD + r'|$)'

# --- Numeric range ---
_RE_BETWEEN = re.compile(
    r'(?:\b([\w\s]{2,})\s+)?(?:is\s+|are\s+)?(?:in\s+between\s+(?:of\s+)?|between\s+)?(\d+(?:\.\d+)?\s*(?:k|m|b|t|thousand|million|billion|trillion|lakhs?|crores?)?)\s*%?\s*(?:and|to|through|[-])\s*(\d+(?:\.\d+)?\s*(?:k|m|b|t|thousand|million|billion|trillion|lakhs?|crores?)?)\s*%?' + _STOP_BASE,
    re.IGNORECASE,
)

# --- Comparison operators (natural language) ---
_RE_GREATER_NL = re.compile(
    r'(?:\b([\w\s]{2,})\s+)?(?:is\s+|are\s+|has\s+)?(?:greater\s+than|more\s+than|above|over|at\s+least|minimum|min|higher\s+than|larger\s+than|bigger\s+than)\s*(?:of\s+)?(\d+(?:\.\d+)?\s*(?:k|m|b|t|thousand|million|billion|trillion|lakhs?|crores?)?)\s*%?' + _STOP_BASE,
    re.IGNORECASE,
)
_RE_LESS_NL = re.compile(
    r'(?:\b([\w\s]{2,})\s+)?(?:is\s+|are\s+|has\s+)?(?:less\s+than|under|below|at\s+most|maximum|max|lower\s+than|smaller\s+than|lesser\s+than)\s*(?:of\s+)?(\d+(?:\.\d+)?\s*(?:k|m|b|t|thousand|million|billion|trillion|lakhs?|crores?)?)\s*%?' + _STOP_BASE,
    re.IGNORECASE,
)

_RE_COMP_SYM = re.compile(
    r'(\w+)\s*(>=|<=|>|<|=)\s*(\d+(?:\.\d+)?)\s*%?',
    re.IGNORECASE,
)

# --- Simple Equality (is/are/set to) ---
# We exclude values that look like other constraints (starts/ends with, above/below, distributions)
_RE_EQUALITY = re.compile(
    r'(?:\b([\w\s]{2,})\s+)?(?:is|are|set\s+to|equals?)\s+(?!(?:norm|gauss|unif|distrib|starts|ends|above|below|greater|less|max|min))([A-Za-z0-9@._\s% -]+?)' + _STOP_VAL,
    re.IGNORECASE,
)

# --- Implied Percentage (e.g. "bonus 10%") ---
_RE_PERCENT_FIXED = re.compile(
    r'(?:\b([\w\s]{2,})\s+)?(\d+(?:\.\d+)?)\s*%' + _STOP_BASE,
    re.IGNORECASE,
)

# --- Categorical / Enum ---
# Added boundaries and non-greedy matching to avoid swallowing subsequent constraints
_RE_ENUM_IN = re.compile(
    r'(?:\b([\w\s]{2,})\s+)?\b(?:in|from|among|one\s+of|lists?)\s+(?!(?:starts|ends)\s+with)\[?\s*([A-Za-z0-9@._\s,/|\'"-]+?)\s*\]?' + _STOP_CAT,
    re.IGNORECASE,
)
_RE_ENUM_OR = re.compile(
    r'(?:\b([\w\s]{2,})\s+)?\b(?:is|are|either|as)\s+(?!(?:starts|ends)\s+with)([A-Za-z0-9@._\s,/|\'"-]+?\s+\bor\b\s+[A-Za-z0-9@._\s,/|\'"-]+?)' + _STOP_CAT,
    re.IGNORECASE,
)
_RE_ENUM_LIST = re.compile(
    r'(?:\b([\w\s]{2,})\s+)?\b(?:is|are)\s+(?!(?:starts|ends)\s+with)([A-Za-z0-9@._\s,/|\'"-]+?,\s*[A-Za-z0-9@._\s,/|\'"-]+?\s+(?:or|and)\s+[A-Za-z0-9@._\s,/|\'"-]+?)' + _STOP_CAT,
    re.IGNORECASE,
)
_RE_ENUM_SIMPLE_OR = re.compile(
    r'(?:\b([\w\s]{2,})\s+)?(?!(?:starts|ends)\s+with)([A-Za-z0-9@._\s,/|\'"-]+?\s+\bor\b\s+[A-Za-z0-9@._\s,/|\'"-]+?)' + _STOP_CAT,
    re.IGNORECASE,
)
# --- Length ---
_RE_LENGTH = re.compile(
    r'(?:\b([\w\s]{2,})\s+)?(?:has\s+)?(\d+)\s+(?:digits?|characters?|chars?|length)' + _STOP_BASE,
    re.IGNORECASE,
)
_RE_LENGTH_RANGE = re.compile(
    r'(?:\b([\w\s]{2,})\s+)?(?:has\s+)?length\s+(?:is\s+)?(?:in\s+)?between\s+(\d+)\s+(?:and|to)\s+(\d+)' + _STOP_BASE,
    re.IGNORECASE,
)

# --- Prefix / Suffix ---
_RE_PREFIX = re.compile(
    r'(?:\b([\w\s]{2,})\s+)?(?:starts?\s+(?:with|like)|prefix|beginning\s+with)\s+([A-Za-z0-9@._\s,/|\'"-]+?)' + _STOP_VAL,
    re.IGNORECASE,
)
_RE_SUFFIX = re.compile(
    r'(?:\b([\w\s]{2,})\s+)?(?:ends?\s+(?:with|like)|suffix|ending\s+with)\s+([A-Za-z0-9@._\s,/|\'"-]+?)' + _STOP_VAL,
    re.IGNORECASE,
)
_RE_PATTERN = re.compile(
    r'(?:\b([\w\s]{2,})\s+)?(?:pattern|format|formatted\s+like|matches|\blike\b)\s+([A-Za-z0-9@._\s,#|\'"-]+?)' + _STOP_VAL,
    re.IGNORECASE,
)
_RE_PATTERN_REVERSE = re.compile(
    r'(?:\b([\w\s]{2,})\s+)?([A-Za-z0-9@._\s,#|\'"-]+?)\s+(?:pattern|format|formatted\s+like|matches)' + _STOP_VAL,
    re.IGNORECASE,
)

# --- Uniqueness ---
_RE_UNIQUE_PRE = re.compile(r'\bunique\s+([\w_]+)', re.IGNORECASE)
_RE_UNIQUE_POST = re.compile(r'([\w_]+)\s+(?:unique|distinct)', re.IGNORECASE)

# --- Nullable ---
_RE_NULLABLE = re.compile(
    r'(?:\b([\w\s]+?)\s+)?(?:can\s+be\s+null|optional|nullable|can\s+be\s+empty|allow\s+null|is\s+null|are\s+null|should\s+be\s+null)',
    re.IGNORECASE,
)
_RE_NULL_PARTIAL = re.compile(
    r'(?:some|partial|mostly|randomly|roughly)\s+([\w\s]+?)\s+(?:are|should\s+be|is|must\s+be|will\s+be|can\s+be)?\s*null',
    re.IGNORECASE,
)
_RE_NULL_ALL = re.compile(
    r'(?:all|every|each|always)\s+([\w\s]+?)\s+(?:are|should\s+be|is|must\s+be|will\s+be)?\s*null',
    re.IGNORECASE,
)

# --- Distribution per column ---
_RE_COL_DIST = re.compile(
    r'\b([\w\s]+?)\s+(?:follow|follows|following|use|using|with)\s+(?:a|an|the|as)?\s*(normal|gaussian|uniform|skewed)\s*(?:distribution)?(?!.*for\b)' + _STOP_BASE,
    re.IGNORECASE,
)
_RE_COL_DIST_FOR = re.compile(
    r'(?:follow|follows|following|use|using|with)\s+(?:a|an|the|as)?\s*(normal|gaussian|uniform|skewed)\s*(?:distribution)?\s+for\s+([\w\s]+)' + _STOP_BASE,
    re.IGNORECASE,
)
_RE_COL_DIST_ALT = re.compile(
    r'(\b[\w\s]+?)\s+(?:normally|uniformly)\s+distributed' + _STOP_BASE,
    re.IGNORECASE,
)

# --- Rounding / Step ---
_RE_STEP = re.compile(
    r'(?:\b([\w\s]+?)\s+)?(?:multiple\s+of|increments?\s+of|round\s+to|step)\s+(\d+(?:\.\d+)?\s*(?:k|m|b|t|thousand|million|billion|trillion|lakhs?|crores?)?)' + _STOP_BASE,
    re.IGNORECASE,
)

# --- Global distribution ---
_RE_GLOBAL_DIST = re.compile(
    r'(?:use|with|using)?\s*(normal|gaussian|uniform)\s+distribution',
    re.IGNORECASE,
)

# --- Rows ---
_RE_ROWS = re.compile(r'(\d+(?:\.\d+)?\s*(?:k|m|b|t|thousand|million|billion|trillion|lakhs?|crores?)?)\s*(?:[\w\s]+\s+)?(?:rows|records|entries|samples|students?|employees?|patients?|pupils?|people|users?|items?|persons?|data)', re.IGNORECASE)

# --- Dynamic (Cross-column) ---
_RE_DYNAMIC_LESS = re.compile(
    r'(?:\b([\w\s]+?)\s+)?(?:is\s+)?(?:below|less\s+than|under|at\s+most|maximum|max|should\s+be\s+lower\s+than|must\s+be\s+lower\s+than|lower\s+than|smaller\s+than)\s+(?:the\s+)?([\w\s]+?)(?=\s+and\b|$)',
    re.IGNORECASE,
)
_RE_DYNAMIC_GREATER = re.compile(
    r'(?:\b([\w\s]+?)\s+)?(?:is\s+)?(?:above|greater\s+than|more\s+than|over|at\s+least|minimum|min|higher\s+than|must\s+be\s+higher\s+than|higher\s+than|larger\s+than|bigger\s+than)\s+(?:the\s+)?([\w\s]+?)(?=\s+and\b|$)',
    re.IGNORECASE,
)

# Words that must never be treated as column names
_STOP_WORDS = frozenset({
    "generate", "create", "make", "build", "produce", "give", "get",
    "me", "the", "of", "for", "to", "want", "need",
    "with", "and", "or", "data", "dataset", "table", "records", "rows",
    "entries", "samples", "some", "having", "where", "that", "which",
    "should", "must", "can", "be", "is", "are", "has", "have",
    "please", "also", "each", "every", "all", "student", "students",
    "but", "use", "using", "distribution", "normal", "uniform", "gaussian",
    "normally", "uniformly", "distributed", "follow", "follows", "between",
    "in", "among", "one", "of", "either", "lists", "list", "has", "have"
})


# ======================================================================
#  Column-name fuzzy matching
# ======================================================================

def _build_column_lookup(resolved_columns):
    """
    Build a fast lookup: lowered_name → canonical_name.
    Handles underscored and space-separated variants automatically.
    Now also handles basic plural forms (suffix 's').
    """
    lookup = {}
    for col in resolved_columns:
        # Use output_name if available to distinguish between instances (e.g. math_score vs science_score)
        res_key = col.get("output_name", col["name"])
        name = col["name"]
        aliases = col.get("aliases", [])
        
        # Register canonical name, output_name and its variants
        variants = [name, res_key] + aliases
        for v in variants:
            if not v: continue
            lower = v.lower()
            lookup[lower] = res_key
            
            # Basic pluralization
            if not lower.endswith('s'):
                lookup[lower + 's'] = res_key
            if lower.endswith('y'):
                lookup[lower[:-1] + 'ies'] = res_key
            if lower.endswith('s') or lower.endswith('ch') or lower.endswith('sh') or lower.endswith('x'):
                lookup[lower + 'es'] = res_key
            # also register no-separator version
            if "_" in lower or " " in lower:
                flat = lower.replace("_", "").replace(" ", "")
                lookup[flat] = res_key
                lookup[flat + "s"] = res_key
    return lookup


def _resolve_col_name(raw_name: str, col_lookup: dict, parser_state: dict) -> str:
    """
    Map a raw string to the canonical internal name.
    Tracks state to provide context for subsequent segments.
    """
    if not raw_name or not raw_name.strip():
        # Fallback to context ONLY if we have one
        return parser_state.get("last_seen_column")

    norm = raw_name.lower().strip()
    
    # Strip common leading noise that might hide the column name
    # e.g. "their middle name" -> "middle name"
    noise = ["their ", "his ", "her ", "the ", "its ", "of ", "for ", "student ", "students "]
    for n in noise:
        if norm.startswith(n):
            norm = norm[len(n):].strip()

    norm_no_stop = " ".join([w for w in norm.split() if w not in _STOP_WORDS]).strip()
    
    # 1. Direct / cleaned lookup
    if norm in col_lookup:
        res = col_lookup[norm]
        parser_state["last_seen_column"] = res
        return res
    if norm_no_stop and norm_no_stop in col_lookup:
        res = col_lookup[norm_no_stop]
        parser_state["last_seen_column"] = res
        return res

    # 2. Split and try to find any word that matches a column
    # This prevents "roll_number follows..." from being missed if it's part of a longer segment
    for word in norm.split():
        if word in col_lookup:
            res = col_lookup[word]
            parser_state["last_seen_column"] = res
            return res

    # 3. Contextual fallback if this part of the sentence omitted the column name
    return parser_state.get("last_seen_column")


# ======================================================================
#  Parser Helpers
# ======================================================================

def _add_constraint(constraints, col, key, val):
    """
    Adds a constraint value to a column.
    Collection keys (choices, prefix, suffix) merge into lists.
    Scalar keys (min, max, length, etc.) overwrite (last one wins).
    """
    # Keys that should always be a single scalar value
    scalar_keys = {
        "min", "max", "length", "min_length", "max_length", 
        "multiple_of", "null_chance", "nullable", "unique", 
        "distribution", "pattern_sample", "dynamic_min", "dynamic_max"
    }

    if key in scalar_keys:
        # Strict overwrite
        constraints["columns"][col][key] = val
        return

    # Collection keys merge
    current = constraints["columns"][col].get(key)
    if current is None:
        constraints["columns"][col][key] = val
    elif key in ("choices", "prefix", "suffix"):
        if not isinstance(current, list):
            current = [current]
        
        new_vals = val if isinstance(val, list) else [val]
        for v in new_vals:
            if v not in current:
                current.append(v)
        constraints["columns"][col][key] = current
    else:
        # Fallback for unexpected keys
        constraints["columns"][col][key] = val

# ======================================================================
#  Parser Functions
# ======================================================================

def _parse_numeric_range(text: str, col_lookup: dict, constraints: dict, parser_state: dict):
    for match in _RE_BETWEEN.finditer(text):
        col_raw, min_val, max_val = match.groups()
        c_name = _resolve_col_name(col_raw, col_lookup, parser_state)
        if c_name:
            _add_constraint(constraints, c_name, "min", _smart_number(min_val))
            _add_constraint(constraints, c_name, "max", _smart_number(max_val))

def _parse_greater_than(text: str, col_lookup: dict, constraints: dict, parser_state: dict):
    for match in _RE_GREATER_NL.finditer(text):
        col_raw, min_val = match.groups()
        c_name = _resolve_col_name(col_raw, col_lookup, parser_state)
        if c_name:
            _add_constraint(constraints, c_name, "min", _smart_number(min_val))

def _parse_less_than(text: str, col_lookup: dict, constraints: dict, parser_state: dict):
    for match in _RE_LESS_NL.finditer(text):
        col_raw, max_val = match.groups()
        c_name = _resolve_col_name(col_raw, col_lookup, parser_state)
        if c_name:
            _add_constraint(constraints, c_name, "max", _smart_number(max_val))

def _parse_symbolic_comparison(text: str, col_lookup: dict, constraints: dict, parser_state: dict):
    for match in _RE_COMP_SYM.finditer(text):
        col_raw, oper, val = match.groups()
        c_name = _resolve_col_name(col_raw, col_lookup, parser_state)
        if not c_name:
            continue
        v = _smart_number(val)
        if oper in (">=", ">"):
            _add_constraint(constraints, c_name, "min", v)
        elif oper in ("<=", "<"):
            _add_constraint(constraints, c_name, "max", v)
        elif oper == "=":
            _add_constraint(constraints, c_name, "min", v)
            _add_constraint(constraints, c_name, "max", v)
        
        # Infer type if numeric
        if isinstance(v, float):
            constraints["columns"][c_name]["type"] = "float"
        elif isinstance(v, int):
            constraints["columns"][c_name]["type"] = "integer"


def _parse_categorical(text, col_lookup, constraints, resolved_columns=None, parser_state=None):
    """'grade in A, B, C, D, F' or 'gender male or female'"""
    # Helper to map lowercased extracted choices back to correct casing
    def _map_casing(col_name, extracted_choices, parser_state):
        if not resolved_columns:
            return extracted_choices
        
        # Find the original column spec from resolved_columns
        spec = next((c for c in resolved_columns if c["name"] == col_name), {})
        
        valid_choices = spec.get("choices", [])
        valid_choices_lower = {c.lower(): c for c in valid_choices}
        col_type = spec.get("type", "string")

        # Abbreviation mapping specifically for common fields
        abbrev_map = {}
        if col_name == "gender":
            abbrev_map = {"m": "Male", "f": "Female", "o": "Other"}
        elif col_name == "status":
            abbrev_map = {"active": "Active", "inactive": "Inactive", "suspended": "Suspended", "on leave": "On Leave", "dismissed": "Dismissed"}
            
        mapped = []
        for c in extracted_choices:
            if isinstance(c, (int, float)):
                mapped.append(c)
                continue
            c_clean = str(c).strip(",. \"'").lower()
            if not c_clean:
                continue
            
            # Numeric conversion if column is numeric
            if col_type in ("integer", "float", "number"):
                val = _smart_number(c_clean)
                if isinstance(val, (int, float)):
                    mapped.append(val)
                else:
                    if c_clean in valid_choices_lower:
                        mapped.append(valid_choices_lower[c_clean])
                continue
            
            if c_clean in abbrev_map:
                mapped.append(abbrev_map[c_clean])
            elif c_clean in valid_choices_lower:
                mapped.append(valid_choices_lower[c_clean])
            else:
                # If user typed short code (CS, IT), keep it uppercase
                if len(c_clean) <= 3:
                    mapped.append(c_clean.upper())
                else:
                    mapped.append(c_clean.capitalize()) # fallback
        return mapped
        return mapped

    # "in/from/among" style
    for match in _RE_ENUM_IN.finditer(text):
        raw_col, raw_values = match.group(1), match.group(2)
        col = _resolve_col_name(raw_col, col_lookup, parser_state)
        if col:
            choices = _split_choices(raw_values)
            choices = _map_casing(col, choices, parser_state)
            if len(choices) >= 1:
                # Equality for numeric/date fields should set min/max
                spec = next((c for c in (resolved_columns or []) if c["name"] == col), {})
                if len(choices) == 1 and spec.get("type") in ("integer", "float", "date"):
                    _add_constraint(constraints, col, "min", choices[0])
                    _add_constraint(constraints, col, "max", choices[0])
                else:
                    # Always store choices as a list to avoid random.choice errors or string iteration
                    _add_constraint(constraints, col, "choices", choices)

    # "either X or Y" style
    for match in _RE_ENUM_OR.finditer(text):
        raw_col, raw_values = match.group(1), match.group(2)
        col = _resolve_col_name(raw_col, col_lookup, parser_state)
        if col:
            choices = _split_choices(raw_values)
            choices = _map_casing(col, choices, parser_state)
            if len(choices) >= 2:
                _add_constraint(constraints, col, "choices", choices)

    # "X, Y and Z" style
    for match in _RE_ENUM_LIST.finditer(text):
        raw_col, raw_values = match.group(1), match.group(2)
        col = _resolve_col_name(raw_col, col_lookup, parser_state)
        if col:
            choices = _split_choices(raw_values)
            choices = _map_casing(col, choices, parser_state)
            if len(choices) >= 2:
                _add_constraint(constraints, col, "choices", choices)

    # Simple "X or Y" without keyword
    for match in _RE_ENUM_SIMPLE_OR.finditer(text):
        raw_col, raw_values = match.group(1), match.group(2)
        col = _resolve_col_name(raw_col, col_lookup, parser_state)
        if col:
            choices = _split_choices(raw_values)
            choices = _map_casing(col, choices, parser_state)
            if len(choices) >= 2:
                _add_constraint(constraints, col, "choices", choices)


def _parse_equality(text, col_lookup, constraints, parser_state):
    """'graduation year is 2026', 'status set to active'"""
    for match in _RE_EQUALITY.finditer(text):
        raw_col, val = match.groups()
        col = _resolve_col_name(raw_col, col_lookup, parser_state)
        if col:
            val_clean = val.strip(",. \"'")
            # If it's a number, convert it
            num = _smart_number(val_clean)
            if isinstance(num, (int, float)):
                # For numeric equality, set min=max
                _add_constraint(constraints, col, "min", num)
                _add_constraint(constraints, col, "max", num)
            else:
                # Always store choices as a list to avoid random.choice errors or string iteration
                # Ensure we don't treat prefixes/suffixes as simple choices
                val_lower = val_clean.lower()
                if not any(val_lower.startswith(m) for m in ["starts with", "ends with", "pattern", "format", "like"]):
                    _add_constraint(constraints, col, "choices", [val_clean])


def _parse_fixed_percentage(text, col_lookup, constraints, parser_state):
    """'bonus 10%', 'tax 5%'"""
    for match in _RE_PERCENT_FIXED.finditer(text):
        raw_col, val = match.groups()
        col = _resolve_col_name(raw_col, col_lookup, parser_state)
        if col:
            v = _smart_number(val)
            # For numeric equality, set min=max
            _add_constraint(constraints, col, "min", v)
            _add_constraint(constraints, col, "max", v)
            constraints["columns"][col]["type"] = "percentage"


def _parse_length(text, col_lookup, constraints, parser_state):
    """'phone 10 digits', 'name length between 10 and 20'"""
    for match in _RE_LENGTH.finditer(text):
        raw_col, length = match.groups()
        col = _resolve_col_name(raw_col, col_lookup, parser_state)
        if col:
            _add_constraint(constraints, col, "length", int(length))
            
    for match in _RE_LENGTH_RANGE.finditer(text):
        raw_col, min_len, max_len = match.groups()
        col = _resolve_col_name(raw_col, col_lookup, parser_state)
        if col:
            _add_constraint(constraints, col, "min_length", int(min_len))
            _add_constraint(constraints, col, "max_length", int(max_len))


def _parse_prefix_suffix(text, col_lookup, constraints, parser_state):
    """'id starts with STU', 'email ends with @edu.in'"""
    for match in _RE_PREFIX.finditer(text):
        raw_col, prefix_val = match.group(1), match.group(2)
        col = _resolve_col_name(raw_col, col_lookup, parser_state)
        if col:
            # Handle multiple prefixes like "A or B"
            if " or " in prefix_val.lower() or " and " in prefix_val.lower() or "," in prefix_val:
                vals = _split_choices(prefix_val)
                for v in vals:
                    _add_constraint(constraints, col, "prefix", v.strip(",. \"'"))
            else:
                _add_constraint(constraints, col, "prefix", prefix_val.strip(",. \"'"))

    for match in _RE_SUFFIX.finditer(text):
        raw_col, suffix_val = match.group(1), match.group(2)
        col = _resolve_col_name(raw_col, col_lookup, parser_state)
        if col:
            if " or " in suffix_val.lower() or " and " in suffix_val.lower() or "," in suffix_val:
                vals = _split_choices(suffix_val)
                for v in vals:
                    _add_constraint(constraints, col, "suffix", v.strip(",. \"'"))
            else:
                _add_constraint(constraints, col, "suffix", suffix_val.strip(",. \"'"))


def _parse_pattern(text, col_lookup, constraints, parser_state):
    """'roll number like CS2024001', 'id format STU-001', 'STU-001 format'"""
    # Standard: [Keyword] [Sample]
    for match in _RE_PATTERN.finditer(text):
        raw_col, sample = match.group(1), match.group(2)
        col = _resolve_col_name(raw_col, col_lookup, parser_state)
        if col:
            sample = sample.strip(",. \"'")
            _add_constraint(constraints, col, "pattern_sample", sample)
            
    # Reverse: [Sample] [Keyword]
    for match in _RE_PATTERN_REVERSE.finditer(text):
        raw_col, sample = match.group(1), match.group(2)
        col = _resolve_col_name(raw_col, col_lookup, parser_state)
        if col:
            sample = sample.strip(",. \"'")
            _add_constraint(constraints, col, "pattern_sample", sample)


def _parse_uniqueness(text, col_lookup, constraints, parser_state):
    """'unique email', 'roll_number unique'"""
    for regex in (_RE_UNIQUE_PRE, _RE_UNIQUE_POST):
        for match in regex.finditer(text):
            col = _resolve_col_name(match.group(1), col_lookup, parser_state)
            if col:
                _add_constraint(constraints, col, "unique", True)


def _parse_nullable(text, col_lookup, constraints, parser_state):
    """'scholarship can be null', 'address optional'"""
    for match in _RE_NULLABLE.finditer(text):
        raw_col = match.group(1)
        col = _resolve_col_name(raw_col, col_lookup, parser_state)
        if col:
            _add_constraint(constraints, col, "nullable", True)
            _add_constraint(constraints, col, "null_chance", 1.0)
    
    # Partial Nulls ("some address are null", "randomly absent")
    for match in _RE_NULL_PARTIAL.finditer(text):
        raw_col = match.group(1)
        col = _resolve_col_name(raw_col, col_lookup, parser_state)
        if col:
            _add_constraint(constraints, col, "nullable", True)
            _add_constraint(constraints, col, "null_chance", 0.2)

    # All Nulls ("all address should be null")
    for match in _RE_NULL_ALL.finditer(text):
        raw_col = match.group(1)
        col = _resolve_col_name(raw_col, col_lookup, parser_state)
        if col:
            _add_constraint(constraints, col, "nullable", True)
            _add_constraint(constraints, col, "null_chance", 1.0)


def _parse_rounding(text, col_lookup, constraints, parser_state):
    for match in _RE_STEP.finditer(text):
        raw_col, val = match.groups()
        col = _resolve_col_name(raw_col, col_lookup, parser_state)
        if col:
            constraints["columns"][col]["multiple_of"] = _smart_number(val)


def _parse_column_distribution(text, col_lookup, constraints, parser_state):
    """
    'marks follow normal distribution', 'marks normally distributed',
    'use normal distribution for GPA'
    """
    # Pattern 1: [Column] follow [Dist]
    for match in _RE_COL_DIST.finditer(text):
        raw_col, dist = match.group(1), match.group(2).lower()
        col = _resolve_col_name(raw_col, col_lookup, parser_state)
        if col:
            if dist in ("normal", "gaussian"):
                constraints["columns"][col]["distribution"] = "normal"
            elif dist == "uniform":
                constraints["columns"][col]["distribution"] = "uniform"

    # Pattern 2: use [Dist] for [Column]
    for match in _RE_COL_DIST_FOR.finditer(text):
        dist, raw_col = match.group(1).lower(), match.group(2)
        col = _resolve_col_name(raw_col, col_lookup, parser_state)
        if col:
            if dist in ("normal", "gaussian"):
                constraints["columns"][col]["distribution"] = "normal"
            elif dist == "uniform":
                constraints["columns"][col]["distribution"] = "uniform"

    for match in _RE_COL_DIST_ALT.finditer(text):
        raw_col = match.group(1)
        col = _resolve_col_name(raw_col, col_lookup, parser_state)
        if col:
            if "normally" in match.group(0).lower():
                constraints["columns"][col]["distribution"] = "normal"
            else:
                constraints["columns"][col]["distribution"] = "uniform"


def _parse_dynamic_constraints(text, col_lookup, constraints, parser_state):
    """'scholarship below fees', 'discount less than price'"""
    # Pattern: [Col A] below [Col B]
    for match in _RE_DYNAMIC_LESS.finditer(text):
        raw_col_a, raw_col_b = match.groups()
        
        # Don't match if Col B is a number (it would be caught by standard less_than)
        if re.match(r'^\d', raw_col_b.strip()):
            continue
            
        src_canonical = _resolve_col_name(raw_col_a, col_lookup, parser_state)
        target_canonical = _resolve_col_name(raw_col_b, col_lookup, parser_state)
        
        if src_canonical and target_canonical and src_canonical != target_canonical:
            _add_constraint(constraints, src_canonical, "dynamic_max", target_canonical)

    # Pattern: [Col A] above [Col B]
    for match in _RE_DYNAMIC_GREATER.finditer(text):
        raw_col_a, raw_col_b = match.groups()
        
        # Don't match if Col B is a number
        if re.match(r'^\d', raw_col_b.strip()):
            continue

        src_canonical = _resolve_col_name(raw_col_a, col_lookup, parser_state)
        target_canonical = _resolve_col_name(raw_col_b, col_lookup, parser_state)
        
        if src_canonical and target_canonical and src_canonical != target_canonical:
            _add_constraint(constraints, src_canonical, "dynamic_min", target_canonical)


def _parse_global_constraints(text, constraints):
    """Global distribution and row count."""
    # Distribution
    dist_match = _RE_GLOBAL_DIST.search(text)
    if dist_match:
        dist = dist_match.group(1).lower()
        if dist in ("normal", "gaussian"):
            constraints["global"]["distribution"] = "normal"
        else:
            constraints["global"]["distribution"] = "uniform"

    # Rows
    rows_match = _RE_ROWS.search(text)
    if rows_match:
        constraints["global"]["rows"] = _smart_number(rows_match.group(1))


# ======================================================================
#  Helpers
# ======================================================================

def _smart_number(s: str):
    """
    Convert string like '500', '50.5', '50k', '2 lakh', 'a million' to int or float.
    Returns the numeric value or the original string if parsing fails.
    """
    if not s or not isinstance(s, str):
        return s
    
    raw = s.strip().lower().replace(",", "")

    # 1. Check for verbal multipliers
    multipliers = {
        "k": 1_000,
        "m": 1_000_000,
        "b": 1_000_000_000,
        "t": 1_000_000_000_000,
        "thousand": 1_000,
        "million": 1_000_000,
        "billion": 1_000_000_000,
        "trillion": 1_000_000_000_000,
        "lakh": 100_000,
        "lakhs": 100_000,
        "crore": 10_000_000,
        "crores": 10_000_000,
    }

    # Handle standalone words like "million", "a million"
    if raw in multipliers:
        return multipliers[raw]
    if (raw.startswith("a ") or raw.startswith("an ")) and raw.split()[-1] in multipliers:
        return multipliers[raw.split()[-1]]

    # Extract number and unit
    # Matches e.g. "50", "50.5", "50 k", "2 lakh"
    match = re.fullmatch(r'(\d+(?:\.\d+)?)\s*(k|m|b|t|thousand|million|billion|trillion|lakhs?|crores?)?', raw)
    if match:
        num_str, unit = match.groups()
        try:
            val = float(num_str)
            if unit in multipliers:
                val *= multipliers[unit]
            
            # Convert to int if it's a whole number
            if val.is_integer():
                return int(val)
            return val
        except ValueError:
            pass

    # 2. Basic fallback
    try:
        if "." in raw:
            return float(raw)
        return int(raw)
    except (ValueError, TypeError):
        return s
    except (ValueError, TypeError):
        return 0


def _split_choices(raw: str):
    """
    Split choice lists like 'A, B, or C' or 'A and B' or 'A/B/C'.
    Handles commas, slashes, pipes, and natural language conjunctions.
    """
    # 1. Normalize separators: replace ' and ', ' or ', ' & ' with commas
    s = re.sub(r'\s+(?:and|or|&)\s+', ',', raw, flags=re.IGNORECASE)
    
    # 2. Handle symbol delimiters even without spaces: |, /, \
    s = re.sub(r'[|/\\\\]', ',', s)
    
    # 3. Split by comma
    parts = [p.strip() for p in s.split(",") if p.strip()]

    # 4. Fallback: if STILL only 1 part and it has spaces, maybe it's space-separated?
    # (But only if doesn't look like a single multi-word entity)
    # For now, we'll keep it simple and trust the delimiters above.
    # If the user typed "Male Female", we can split by space.
    if len(parts) == 1 and " " in parts[0]:
        # Only split by space if the words are short or common
        # Actually, let's just split and filter.
        parts = [p.strip() for p in parts[0].split() if p.strip()]

    # 5. Cleanup each part
    cleaned = []
    for p in parts:
        # Remove leading/trailing junk words like 'or ', 'and ', 'either ', 'as '
        p_clean = re.sub(r'^(?:and|or|either|as|is|among|of|both)\s+', '', p, flags=re.IGNORECASE)
        p_clean = p_clean.strip(",. ")
        
        if p_clean and p_clean.lower() not in _STOP_WORDS:
            # Try to convert to number if it looks like one
            num = _smart_number(p_clean)
            if isinstance(num, (int, float)):
                cleaned.append(num)
            else:
                cleaned.append(p_clean)

    return cleaned


# ======================================================================
#  Public API
# ======================================================================

def parse_universal_constraints(user_text: str, resolved_columns: list) -> dict:
    """
    Extract all constraints from *user_text* that apply to
    *resolved_columns*.

    Parameters
    ----------
    user_text : str
        The raw user prompt.
    resolved_columns : list[dict]
        List of resolved column dicts, each having at least ``{"name": ...}``.

    Returns
    -------
    dict  with keys ``"global"`` and ``"columns"``.
        ``"global"`` → dict of global constraints (rows, distribution).
        ``"columns"`` → dict mapping column name → dict of constraints.
    """
    text = user_text.lower()

    constraints = {
        "global": {},
        "columns": defaultdict(dict),
    }

    col_lookup = _build_column_lookup(resolved_columns)

    parser_state = {"last_seen_column": None}

    # Run every constraint parser — each one mutates *constraints* in place.
    # Wrapped in try/except so a single bad regex never kills the pipeline.
    parsers = [
        ("numeric_range",       lambda: _parse_numeric_range(text, col_lookup, constraints, parser_state)),
        ("greater_than",        lambda: _parse_greater_than(text, col_lookup, constraints, parser_state)),
        ("less_than",           lambda: _parse_less_than(text, col_lookup, constraints, parser_state)),
        ("symbolic_comparison", lambda: _parse_symbolic_comparison(text, col_lookup, constraints, parser_state)),
        ("categorical",         lambda: _parse_categorical(text, col_lookup, constraints, resolved_columns, parser_state)),
        ("equality",            lambda: _parse_equality(text, col_lookup, constraints, parser_state)),
        ("length",              lambda: _parse_length(text, col_lookup, constraints, parser_state)),
        ("prefix_suffix",       lambda: _parse_prefix_suffix(user_text, col_lookup, constraints, parser_state)),
        ("percent_fixed",       lambda: _parse_fixed_percentage(text, col_lookup, constraints, parser_state)),
        ("pattern",             lambda: _parse_pattern(user_text, col_lookup, constraints, parser_state)),
        ("rounding",            lambda: _parse_rounding(text, col_lookup, constraints, parser_state)),
        ("uniqueness",          lambda: _parse_uniqueness(text, col_lookup, constraints, parser_state)),
        ("nullable",            lambda: _parse_nullable(text, col_lookup, constraints, parser_state)),
        ("dynamic",             lambda: _parse_dynamic_constraints(text, col_lookup, constraints, parser_state)),
        ("column_distribution", lambda: _parse_column_distribution(text, col_lookup, constraints, parser_state)),
        ("global",              lambda: _parse_global_constraints(text, constraints)),
    ]

    for name, parser_fn in parsers:
        try:
            parser_fn()
        except Exception as exc:
            logger.warning("Constraint parser '%s' failed: %s", name, exc)

    # Convert defaultdict to plain dict for serialisation safety
    constraints["columns"] = dict(constraints["columns"])

    return constraints