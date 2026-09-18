# Dataset_Generator/domain_rules.py

"""
Domain-specific validation rules.

These rules define hard boundaries for column values within each domain.
The universal constraint parser can tighten these limits (e.g. user says
"age between 18 and 22"), but it can NEVER widen them beyond the domain
maximums defined here.

Used by:
  - validator.py      → validates that user constraints don't exceed domain limits
  - constraints.py    → enriches columns with domain defaults
  - field_types.py    → falls back to these ranges when no user constraint given
"""

DOMAIN_RULES = {
    "student": {
        # ---------- Numeric ----------
        "age":              {"type": "integer", "min": 5,    "max": 25},
        "marks":            {"type": "integer", "min": 0,    "max": 100},
        "gpa":              {"type": "float",   "min": 0.0,  "max": 10.0},
        "cgpa":             {"type": "float",   "min": 0.0,  "max": 10.0},
        "sgpa":             {"type": "float",   "min": 0.0,  "max": 10.0},
        "percentage":       {"type": "float",   "min": 0.0,  "max": 100.0},
        "attendance":       {"type": "float",   "min": 0.0,  "max": 100.0},
        "semester":         {"type": "integer", "min": 1,    "max": 8},
        "academic_year":    {"type": "integer", "min": 1,    "max": 5},
        "enrollment_year":  {"type": "integer", "min": 2000, "max": 2030},
        "graduation_year":  {"type": "integer", "min": 2004, "max": 2035},
        "fees":             {"type": "float",   "min": 5000, "max": 500000},
        "scholarship":      {"type": "float",   "min": 0,    "max": 500000},
    },

    "employee": {
        "age":    {"type": "integer", "min": 21,    "max": 60},
        "salary": {"type": "integer", "min": 15000, "max": 200000},
    }
}
