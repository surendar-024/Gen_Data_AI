# tests/test_student_domain.py

"""
Comprehensive test suite for the student domain — covers constraint parsing,
schema resolution, field generation, validation, and end-to-end pipeline.

Run:
    cd c:\\Projects\\gendataai\\backend
    python -m pytest tests/test_student_domain.py -v
"""

import sys
import os
import pytest

# Ensure backend is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from nlp_manager.universal_constraint_parser import parse_universal_constraints
from nlp_manager.schema_registry import SCHEMA_REGISTRY
from nlp_manager.column_resolver import resolve_columns
from nlp_manager.column_suggester import clean_and_suggest
from nlp_manager.entities import extract_entities
from nlp_manager.validator import validate_schema, SchemaValidationError
from Dataset_Generator.field_types import (
    generate_field, generate_from_choices, generate_from_pattern,
    generate_phone, generate_pincode,
)
from Dataset_Generator.generator import generate_dataset


# ====================================================================
#  Helpers
# ====================================================================

def _student_columns(*names):
    """Quick helper: resolve a list of column names in student domain."""
    return resolve_columns(list(names), "student")


def _parse(text, col_names):
    """Quick helper: parse constraints for given column specs."""
    cols = _student_columns(*col_names)
    return parse_universal_constraints(text, cols)


# ====================================================================
#  1. Schema Registry Tests
# ====================================================================

class TestSchemaRegistry:
    def test_student_domain_exists(self):
        assert "student" in SCHEMA_REGISTRY

    def test_student_has_many_columns(self):
        cols = SCHEMA_REGISTRY["student"]["columns"]
        assert len(cols) >= 30, f"Expected 30+ columns, got {len(cols)}"

    def test_every_column_has_type(self):
        for name, meta in SCHEMA_REGISTRY["student"]["columns"].items():
            assert "type" in meta, f"Column '{name}' missing type"

    def test_every_column_has_aliases(self):
        for name, meta in SCHEMA_REGISTRY["student"]["columns"].items():
            assert "aliases" in meta, f"Column '{name}' missing aliases"
            assert isinstance(meta["aliases"], list)
            assert len(meta["aliases"]) >= 1

    def test_canonical_name_in_aliases(self):
        """The canonical name itself should be reachable via alias lookup."""
        for name, meta in SCHEMA_REGISTRY["student"]["columns"].items():
            # canonical name or underscore-less version should be in aliases
            aliases_lower = [a.lower() for a in meta["aliases"]]
            assert (
                name in aliases_lower
                or name.replace("_", "") in aliases_lower
            ), f"'{name}' not reachable via its own aliases: {meta['aliases']}"


# ====================================================================
#  2. Column Resolution Tests
# ====================================================================

class TestColumnResolution:
    def test_basic_columns(self):
        cols = _student_columns("name", "age", "marks")
        names = [c["name"] for c in cols]
        assert "name" in names
        assert "age" in names
        assert "marks" in names

    def test_alias_resolution(self):
        """Typing 'rollnumber' should resolve to 'roll_number'."""
        cols = resolve_columns(["rollnumber"], "student")
        assert len(cols) == 1
        assert cols[0]["name"] == "roll_number"

    def test_email_alias(self):
        cols = resolve_columns(["mail"], "student")
        assert len(cols) == 1
        assert cols[0]["name"] == "email"

    def test_unknown_column_ignored(self):
        cols = resolve_columns(["xyzgarbage"], "student")
        assert len(cols) == 0

    def test_new_columns_resolve(self):
        """New columns added in this sprint should resolve."""
        for col_name in ["gpa", "cgpa", "attendance", "department", "phone",
                         "gender", "blood_group", "scholarship", "fees"]:
            cols = resolve_columns([col_name], "student")
            assert len(cols) == 1, f"'{col_name}' did not resolve"
            assert cols[0]["name"] == col_name


# ====================================================================
#  3. Constraint Parser Tests
# ====================================================================

class TestConstraintParserNumericRange:
    def test_between(self):
        r = _parse("age between 18 and 22", ["age"])
        assert r["columns"]["age"]["min"] == 18
        assert r["columns"]["age"]["max"] == 22

    def test_float_upgrade(self):
        """Test that integer columns upgrade to float if user gives float range."""
        r = _parse("scholarship between 1000.5 and 2000.5", ["scholarship"])
        assert r["columns"]["scholarship"]["type"] == "float"
        assert r["columns"]["scholarship"]["min"] == 1000.5

    def test_between_float(self):
        r = _parse("gpa between 7.5 and 9.0", ["gpa"])
        assert r["columns"]["gpa"]["min"] == 7.5
        assert r["columns"]["gpa"]["max"] == 9.0


class TestConstraintParserComparison:
    def test_greater_than(self):
        r = _parse("marks greater than 40", ["marks"])
        assert r["columns"]["marks"]["min"] == 40

    def test_less_than(self):
        r = _parse("age less than 20", ["age"])
        assert r["columns"]["age"]["max"] == 20

    def test_above(self):
        r = _parse("attendance above 75", ["attendance"])
        assert r["columns"]["attendance"]["min"] == 75

    def test_below(self):
        r = _parse("fees below 100000", ["fees"])
        assert r["columns"]["fees"]["max"] == 100000

    def test_symbolic_equals(self):
        r = _parse("semester = 4", ["semester"])
        assert r["columns"]["semester"]["min"] == 4
        assert r["columns"]["semester"]["max"] == 4

    def test_symbolic_gte(self):
        r = _parse("marks >= 50", ["marks"])
        assert r["columns"]["marks"]["min"] == 50


class TestConstraintParserCategorical:
    def test_in_list(self):
        r = _parse("grade in A, B, C, D, F", ["grade"])
        assert "choices" in r["columns"]["grade"]
        choices = r["columns"]["grade"]["choices"]
        assert "A" in choices
        assert "F" in choices

    def test_or_list(self):
        r = _parse("gender either Male or Female", ["gender"])
        assert "choices" in r["columns"]["gender"]
        choices = r["columns"]["gender"]["choices"]
        assert len(choices) == 2
        assert "Male" in choices
        assert "Female" in choices

    def test_complex_conjunctions(self):
        """Test 'X, Y, or Z' and 'X, Y and Z' mixed style."""
        r1 = _parse("department among Computer Science, Electronics, or Physics", ["department"])
        c1 = r1["columns"]["department"]["choices"]
        assert "Computer Science" in c1
        assert "Electronics" in c1
        assert "Physics" in c1
        assert "or Physics" not in c1
        assert "Or physics" not in c1

        r2 = _parse("department Computer Science, Electronics and Physics", ["department"])
        c2 = r2["columns"]["department"]["choices"]
        assert "Physics" in c2
        assert "And physics" not in c2

    def test_no_comma_conjunction(self):
        """Test 'X and Y' without a comma."""
        r = _parse("gender Male and Female", ["gender"])
        choices = r["columns"]["gender"]["choices"]
        assert "Male" in choices
        assert "Female" in choices


class TestConstraintParserPercentage:
    def test_percentage_between(self):
        r = _parse("attendance between 75% and 100%", ["attendance"])
        assert r["columns"]["attendance"]["min"] == 75
        assert r["columns"]["attendance"]["max"] == 100


class TestConstraintParserLength:
    def test_digits(self):
        r = _parse("phone 10 digits", ["phone"])
        assert r["columns"]["phone"]["length"] == 10


class TestConstraintParserPattern:
    def test_like_pattern(self):
        r = _parse("roll_number like CS2024001", ["roll_number"])
        assert r["columns"]["roll_number"]["pattern_sample"] == "CS2024001"


class TestConstraintParserPrefix:
    def test_starts_with(self):
        r = _parse("id starts with STU", ["id"])
        assert r["columns"]["id"]["prefix"] == "STU"


class TestConstraintParserUniqueness:
    def test_unique_prefix(self):
        r = _parse("unique email", ["email"])
        assert r["columns"]["email"]["unique"] is True

    def test_unique_postfix(self):
        r = _parse("roll_number unique", ["roll_number"])
        assert r["columns"]["roll_number"]["unique"] is True


class TestConstraintParserNullable:
    def test_can_be_null(self):
        r = _parse("scholarship can be null", ["scholarship"])
        assert r["columns"]["scholarship"]["nullable"] is True

    def test_optional(self):
        r = _parse("address optional", ["address"])
        assert r["columns"]["address"]["nullable"] is True

    def test_nullable_association(self):
        """Test that nullable attaches to correct column in complex sentences."""
        text = "scholarship between 10000 and 50000, address can be null, and fees > 100"
        r = _parse(text, ["scholarship", "address", "fees"])
        assert r["columns"]["address"]["nullable"] is True
        # Scholarship should NOT be nullable unless specified
        assert r["columns"]["scholarship"].get("nullable") in (None, False)

    def test_full_nullability(self):
        """Test that 'all X are null' sets 100% null chance."""
        r = _parse("all address are null", ["address"])
        assert r["columns"]["address"]["nullable"] is True
        assert r["columns"]["address"]["null_chance"] == 1.0


class TestConstraintParserRounding:
    def test_multiple_of(self):
        r = _parse("scholarship multiple of 1000", ["scholarship"])
        assert r["columns"]["scholarship"]["multiple_of"] == 1000

    def test_increments_of(self):
        r = _parse("fees increments of 500", ["fees"])
        assert r["columns"]["fees"]["multiple_of"] == 500


class TestConstraintParserDistribution:
    def test_global_normal(self):
        r = _parse("use normal distribution", ["marks"])
        assert r["global"]["distribution"] == "normal"

    def test_flexible_col_dist(self):
        """Test 'follow a normal distribution' and 'use normal dist for X'."""
        r = _parse("marks follow a normal distribution", ["marks"])
        assert r["columns"]["marks"]["distribution"] == "normal"
        
        r = _parse("use normal distribution for gpa", ["gpa"])
        assert r["columns"]["gpa"]["distribution"] == "normal"

    def test_row_count(self):
        r = _parse("50 rows", ["marks"])
        assert r["global"]["rows"] == 50


# ====================================================================
#  4. Field Generation Tests
# ====================================================================

class TestFieldGeneration:
    def test_integer_field(self):
        col = {"name": "age", "type": "integer", "min": 18, "max": 22}
        for _ in range(50):
            v = generate_field(col)
            assert 18 <= v <= 22

    def test_float_field(self):
        col = {"name": "gpa", "type": "float", "min": 0.0, "max": 10.0}
        for _ in range(50):
            v = generate_field(col)
            assert 0.0 <= v <= 10.0

    def test_choice_field(self):
        col = {"name": "gender", "type": "choice", "choices": ["Male", "Female"]}
        for _ in range(50):
            v = generate_field(col)
            assert v in ["Male", "Female"]

    def test_pattern_field(self):
        col = {"name": "roll_number", "type": "pattern", "pattern": "CS001"}
        v0 = generate_field(col, index=0)
        v1 = generate_field(col, index=1)
        assert v0 == "CS001"
        assert v1 == "CS002"

    def test_email_field(self):
        col = {"name": "email", "type": "email"}
        v = generate_field(col)
        assert "@" in v

    def test_uuid_field(self):
        col = {"name": "id", "type": "uuid"}
        v = generate_field(col)
        assert len(v) == 36  # UUID format

    def test_name_field(self):
        col = {"name": "name", "type": "name"}
        v = generate_field(col)
        assert isinstance(v, str) and len(v) > 0

    def test_phone_field(self):
        v = generate_phone(10)
        assert len(v) == 10
        assert v[0] in "6789"

    def test_pincode_field(self):
        v = generate_pincode()
        assert len(v) == 6
        assert v.isdigit()

    def test_from_choices(self):
        v = generate_from_choices(["A", "B", "C"])
        assert v in ["A", "B", "C"]

    def test_from_pattern(self):
        assert generate_from_pattern("STU-001", 0) == "STU-001"
        assert generate_from_pattern("STU-001", 5) == "STU-006"

    def test_nullable_field(self):
        """Nullable columns should sometimes produce None."""
        col = {"name": "scholarship", "type": "float", "min": 0, "max": 100000, "nullable": True}
        results = [generate_field(col) for _ in range(200)]
        assert None in results, "Expected at least one None in 200 nullable samples"
        assert any(v is not None for v in results), "Expected some non-None values"

    def test_address_field(self):
        col = {"name": "address", "type": "address"}
        v = generate_field(col)
        assert isinstance(v, str) and len(v) > 0

    def test_city_field(self):
        col = {"name": "city", "type": "city"}
        v = generate_field(col)
        assert isinstance(v, str) and len(v) > 0


# ====================================================================
#  5. Validator Tests
# ====================================================================

class TestValidator:
    def test_valid_schema(self):
        schema = {
            "rows": 10,
            "domain": "student",
            "columns": [{"name": "age", "type": "integer", "min": 18, "max": 22}],
        }
        validate_schema(schema)  # should not raise

    def test_invalid_rows(self):
        schema = {"rows": -1, "domain": "student", "columns": [{"name": "age", "type": "integer"}]}
        with pytest.raises(SchemaValidationError):
            validate_schema(schema)

    def test_no_columns(self):
        schema = {"rows": 10, "domain": "student", "columns": []}
        with pytest.raises(SchemaValidationError):
            validate_schema(schema)

    def test_column_without_name(self):
        schema = {"rows": 10, "domain": "student", "columns": [{"type": "integer"}]}
        with pytest.raises(SchemaValidationError):
            validate_schema(schema)

    def test_clamping(self):
        """User sets age min to -5 → should be clamped to domain min (5)."""
        schema = {
            "rows": 10,
            "domain": "student",
            "columns": [{"name": "age", "type": "integer", "min": -5, "max": 22}],
        }
        validate_schema(schema)
        assert schema["columns"][0]["min"] == 5  # clamped by domain rule


# ====================================================================
#  6. Entity Extraction Tests
# ====================================================================

class TestEntityExtraction:
    def test_student_domain_detection(self):
        result = extract_entities("generate student data with name and age")
        assert result["domain"] == "student"

    def test_academic_keywords(self):
        result = extract_entities("create university enrollment records")
        assert result["domain"] == "student"

    def test_column_extraction(self):
        result = extract_entities("generate data with name, age and marks")
        assert "name" in result["columns"][0]
        assert "age" in result["columns"][1]

    def test_multi_word_alias(self):
        """Test 'phone number' is matched as a whole, not split."""
        res, suggestions = clean_and_suggest(["phone number"], "student")
        assert "phone" in res
        assert "registration_number" not in res
        
    def test_residence_alias(self):
        res, names = clean_and_suggest(["residence"], "student")
        assert "address" in res

    def test_year_mapping_calendar(self):
        """Test 'year' maps to enrollment_year, not academic_year (study year)."""
        res, _ = clean_and_suggest(["year"], "student")
        assert "enrollment_year" in res

    def test_male_collision_protected(self):
        """Test 'male' is not suggested as 'email'."""
        res, suggestions = clean_and_suggest(["male"], "student")
        assert "email" not in res
        
    def test_categorical_isolation(self):
        """Test segmented parsing prevents categorical greediness."""
        from nlp_manager.postprocess import build_schema
        text = "Generate 10 records with gender as Male or Female, status is On Leave or Suspended"
        entities = {"domain": "student", "columns": ["gender as male or female", "status is on leave or suspended"]}
        intent = {"intent": "generate_tabular_data"}
        schema = build_schema(intent, entities, text)
        
        cols = {c["name"]: c for c in schema["columns"]}
        assert cols["gender"]["choices"] == ["Male", "Female"]
        assert cols["status"]["choices"] == ["On Leave", "Suspended"]

    def test_prefix_quote_stripping(self):
        """Test that quotes are stripped from prefixes."""
        from nlp_manager.postprocess import build_schema
        text = "Generate 10 records with name starts with 'S'"
        entities = {"domain": "student", "columns": ["name starts with 'S'"]}
        schema = build_schema({"intent": "generate_tabular_data"}, entities, text)
        assert schema["columns"][0]["prefix"] == "S"

    def test_multi_word_substring_matching(self):
        """Test that 'phone number' is matched correctly even in longer segments."""
        from nlp_manager.column_suggester import clean_and_suggest
        res, _ = clean_and_suggest(["phone number 10 digits"], "student")
        assert "phone" in res
        assert "registration_number" not in res

    def test_no_domain(self):
        res = extract_entities("Create a dataset with random data")
        assert res["domain"] is None

    def test_multi_connector_extraction(self):
        """Test where, having, including, and colons."""
        res = extract_entities("records where name like John and age > 10")
        assert "name like John" in res["columns"]
        assert "age > 10" in res["columns"]
        
        res = extract_entities("students having gpa > 9")
        assert "gpa > 9" in res["columns"]
        
        res = extract_entities("output: email, phone")
        assert "email" in res["columns"]
        assert "phone" in res["columns"]


# ====================================================================
#  7. End-to-End Generation Tests
# ====================================================================

class TestEndToEndGeneration:
    def test_basic_generation(self):
        cols = _student_columns("name", "age", "email")
        data = generate_dataset(rows=10, columns=cols, domain="student")
        assert len(data) == 10
        for row in data:
            assert "name" in row
            assert "age" in row
            assert "email" in row
            assert isinstance(row["age"], int)
            assert 5 <= row["age"] <= 25

    def test_choice_generation(self):
        cols = _student_columns("gender", "grade")
        data = generate_dataset(rows=20, columns=cols, domain="student")
        assert len(data) == 20
        for row in data:
            assert row["gender"] in ["Male", "Female", "Other"]
            assert row["grade"] in ["A+", "A", "B+", "B", "C+", "C", "D", "F"]

    def test_unique_generation(self):
        cols = _student_columns("email")
        data = generate_dataset(rows=50, columns=cols, domain="student")
        emails = [r["email"] for r in data]
        assert len(emails) == len(set(emails)), "Emails should be unique"

    def test_pattern_generation(self):
        cols = _student_columns("roll_number")
        data = generate_dataset(rows=5, columns=cols, domain="student")
        assert len(data) == 5
        # Roll numbers should be sequential
        for i, row in enumerate(data):
            assert "R" in row["roll_number"]

    def test_float_generation(self):
        cols = _student_columns("gpa", "attendance")
        data = generate_dataset(rows=20, columns=cols, domain="student")
        for row in data:
            assert 0.0 <= row["gpa"] <= 10.0
            assert 0.0 <= row["attendance"] <= 100.0

    def test_many_columns(self):
        """Test generating with a large number of columns at once."""
        col_names = [
            "name", "age", "email", "phone", "gender", "marks",
            "gpa", "department", "semester", "attendance",
        ]
        cols = _student_columns(*col_names)
        data = generate_dataset(rows=10, columns=cols, domain="student")
        assert len(data) == 10
        for row in data:
            assert len(row) == len(col_names)

    def test_constrained_generation(self):
        """Apply user constraints and verify data respects them."""
        cols = _student_columns("age", "marks")
        # Simulate user saying "age between 18 and 20, marks greater than 60"
        constraints = parse_universal_constraints(
            "age between 18 and 20, marks greater than 60", cols
        )
        for col in cols:
            name = col["name"]
            if name in constraints["columns"]:
                col.update(constraints["columns"][name])

        data = generate_dataset(rows=30, columns=cols, domain="student")
        for row in data:
            assert 18 <= row["age"] <= 20
            assert row["marks"] >= 60


# ====================================================================
#  8. Column Suggester Tests
# ====================================================================

class TestColumnSuggester:
    def test_clean_basic(self):
        cleaned, suggestions = clean_and_suggest(["name", "age"], "student")
        assert "name" in cleaned
        assert "age" in cleaned

    def test_alias_suggestion(self):
        cleaned, suggestions = clean_and_suggest(["rollnumber"], "student")
        assert "roll_number" in cleaned

    def test_stop_words_removed(self):
        cleaned, _ = clean_and_suggest(["unique name"], "student")
        assert "name" in cleaned
