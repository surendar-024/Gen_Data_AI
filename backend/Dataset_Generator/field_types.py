# Dataset_Generator/field_types.py

"""
Field-value generators for every column type supported by the system.

Each generator produces a single realistic value. The central
``generate_field()`` function dispatches to the correct generator
based on the column's ``type`` and optional constraints (min, max,
choices, pattern_sample, length, prefix, suffix, nullable, index).
"""

from faker import Faker
import re
import random
import uuid
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger("dataset_generator.field_types")

faker = Faker("en_IN")  # Indian locale for realistic student data


# ======================================================================
#  Atomic generators
# ======================================================================

def generate_string():
    return faker.word()


def generate_text():
    return faker.sentence(nb_words=10)


# --- Name Pool for High Performance ---
_NAME_POOL = {"first": [], "last": []}

def _ensure_name_pool():
    if not _NAME_POOL["first"]:
        # Generate a decent pool once
        for _ in range(5000):
            _NAME_POOL["first"].append(faker.first_name())
            _NAME_POOL["last"].append(faker.last_name())

def generate_name(starts_with=None, ends_with=None, use_pool=False):
    if use_pool:
        _ensure_name_pool()
        res = f"{random.choice(_NAME_POOL['first'])} {random.choice(_NAME_POOL['last'])}"
    else:
        res = faker.name()
    
    if starts_with:
        prefixes = starts_with if isinstance(starts_with, list) else [starts_with]
        char_prefixes = [p.upper() for p in prefixes if len(str(p).strip()) == 1]
        if char_prefixes:
            prefix = random.choice(char_prefixes)
            # Retrying with faker is slow, so for large datasets or pool mode, we just prepend
            if use_pool:
                res = f"{prefix}{res[1:]}" if not res.upper().startswith(prefix) else res
            else:
                for _ in range(50):
                    temp = faker.name()
                    if temp.upper().startswith(prefix):
                        res = temp
                        break
        else:
            p = random.choice(prefixes)
            res = f"{p} {res}"

    if ends_with:
        suffixes = ends_with if isinstance(ends_with, list) else [ends_with]
        s = random.choice(suffixes)
        if not res.lower().endswith(str(s).lower().strip()):
            res = f"{res.rstrip()} {s}"
    
    return res


def generate_first_name(starts_with=None, ends_with=None):
    res = faker.first_name()
    if starts_with:
        prefixes = starts_with if isinstance(starts_with, list) else [starts_with]
        char_prefixes = [p.upper() for p in prefixes if len(str(p).strip()) == 1]
        if char_prefixes:
            prefix = random.choice(char_prefixes)
            for _ in range(50):
                temp = faker.first_name()
                if temp.upper().startswith(prefix):
                    res = temp
                    break
        else:
            p = random.choice(prefixes)
            res = f"{p}{res}"

    if ends_with:
        suffixes = ends_with if isinstance(ends_with, list) else [ends_with]
        s = random.choice(suffixes)
        if not res.lower().endswith(str(s).lower().strip()):
            res = f"{res}{s}"
    return res


def generate_last_name(starts_with=None, ends_with=None):
    res = faker.last_name()
    if starts_with:
        prefixes = starts_with if isinstance(starts_with, list) else [starts_with]
        char_prefixes = [p.upper() for p in prefixes if len(str(p).strip()) == 1]
        if char_prefixes:
            prefix = random.choice(char_prefixes)
            for _ in range(50):
                temp = faker.last_name()
                if temp.upper().startswith(prefix):
                    res = temp
                    break
        else:
            p = random.choice(prefixes)
            res = f"{p}{res}"

    if ends_with:
        suffixes = ends_with if isinstance(ends_with, list) else [ends_with]
        s = random.choice(suffixes)
        if not res.lower().endswith(str(s).lower().strip()):
            res = f"{res}{s}"
    return res


def generate_email(prefix=None, suffix=None, index=0):
    """
    Generate an email. If suffix starts with '@', it's treated as the domain.
    Otherwise, it's appended to a standard faker email.
    For large datasets, we use the index to guarantee uniqueness.
    """
    # For large datasets, we append the index to ensure uniqueness and speed
    # faker.user_name() can be slow and collides easily at scale.
    user_name = faker.user_name()
    
    if suffix and str(suffix).startswith("@"):
        # Use user_name + index + custom domain suffix
        res = f"{user_name}.{index}{suffix}"
    else:
        # Standard faker email usually has limited domains, so we inject index
        res = f"{user_name}.{index}@{faker.free_email_domain()}"
        if suffix:
            res = f"{res}{suffix}"
    
    if prefix:
        p = random.choice(prefix) if isinstance(prefix, list) else prefix
        res = f"{p}{res}"
        
    return res


def generate_phone(length=10):
    """Generate a phone number with the given digit count."""
    # Indian mobile: starts with 6-9
    first = str(random.choice([6, 7, 8, 9]))
    rest = "".join(str(random.randint(0, 9)) for _ in range(length - 1))
    return first + rest


def generate_uuid_value(index=0):
    """
    For performance at huge scale, we can return deterministic UUIDs based on index
    or just stick to uuid4 if collisions are rare.
    """
    return str(uuid.uuid4())


def generate_ip():
    return faker.ipv4()


def generate_mac():
    return faker.mac_address()


def generate_boolean():
    return random.choice([True, False])


def generate_integer(min_v=0, max_v=100, multiple_of=None):
    val = random.randint(int(min_v), int(max_v))
    if multiple_of:
        val = (val // int(multiple_of)) * int(multiple_of)
    return val


def generate_float(min_v=0.0, max_v=100.0, precision=2, multiple_of=None):
    val = random.uniform(float(min_v), float(max_v))
    if multiple_of:
        val = (val // float(multiple_of)) * float(multiple_of)
    return round(val, precision)


def generate_date(min_year=None, max_year=None):
    """Generate a random date, optionally within a year range."""
    if min_year and max_year:
        start = datetime(int(min_year), 1, 1)
        end = datetime(int(max_year), 12, 31)
    else:
        start = datetime.now() - timedelta(days=365 * 5)
        end = datetime.now()
    try:
        return faker.date_between(start_date=start, end_date=end).isoformat()
    except Exception:
        return faker.date_between(
            start_date="-5y", end_date="today"
        ).isoformat()


def generate_json():
    return json.dumps({
        "id": faker.random_int(),
        "name": faker.name(),
        "active": generate_boolean()
    })


def generate_address():
    return faker.address().replace("\n", ", ")


def generate_city():
    return faker.city()


def generate_state():
    return faker.state()


def generate_country():
    return faker.country()


def generate_pincode():
    """Indian 6-digit pincode."""
    first = str(random.choice([1, 2, 3, 4, 5, 6, 7, 8]))
    rest = "".join(str(random.randint(0, 9)) for _ in range(5))
    return first + rest


def generate_blood_pressure():
    """Realistic BP like 120/80."""
    systolic = random.randint(90, 160)
    diastolic = random.randint(60, 100)
    return f"{systolic}/{diastolic}"


def generate_bmi(weight=None, height=None):
    """Calculate BMI or generate a realistic range."""
    if weight and height:
        # height is in cm
        return round(weight / ((height/100)**2), 1)
    return round(random.uniform(18.5, 35.0), 1)


def generate_boolean():
    """Generate a random boolean value."""
    return random.choice([True, False])


def generate_text(max_nb_chars=200):
    """Generate a random sentence or paragraph."""
    return faker.text(max_nb_chars=max_nb_chars)


def generate_ip():
    """Generate a random IPv4 address."""
    return faker.ipv4()


def generate_mac():
    """Generate a random MAC address."""
    return faker.mac_address()


def generate_json():
    """Generate a simple random JSON string."""
    data = {
        "id": random.randint(1, 1000),
        "status": random.choice(["ok", "error", "pending"]),
        "timestamp": datetime.now().isoformat()
    }
    return json.dumps(data)


def generate_choice(choices=None):
    """Pick one from a list of allowed values."""
    if not choices:
        return None
    # Defensive check: random.choice needs a sequence with len()
    if not isinstance(choices, (list, tuple, str)):
        return choices
    return random.choice(choices)


def generate_from_pattern(pattern_sample, index=0):
    """
    Generate a sequential value from a pattern sample like 'CS001' or 'STU-001'.
    Finds the LAST numeric portion, increments it by *index*, and pads to the
    original width.
    """
    # Support both digits (\d+) and hash placeholders (#)
    # We prefer # for custom numeric sequences and \d+ for legacy matches
    matches = list(re.finditer(r'(\d+|#+)', pattern_sample))
    if not matches:
        return f"{pattern_sample}{index}"

    # Target the last match
    match = matches[-1]
    number_part = match.group(1)
    
    # If it's #, treat it as a number based on index
    if "#" in number_part:
        pad_length = len(number_part)
        start_number = 1
        new_val = start_number + index
    else:
        # Legacy: extract number and increment
        pad_length = len(number_part)
        start_number = int(number_part)
        new_val = start_number + index

    prefix = pattern_sample[:match.start()]
    suffix = pattern_sample[match.end():]

    number = str(new_val).zfill(pad_length)
    return f"{prefix}{number}{suffix}"


# ======================================================================
#  Central dispatcher
# ======================================================================

def generate_field(column: dict, distribution_func=None, index=0):
    """
    Generate a single field value based on the column schema.

    Parameters
    ----------
    column : dict
        Column spec with keys: name, type, and optional min, max, choices,
        pattern_sample, length, prefix, suffix, nullable, unique.
    distribution_func : callable or None
        Distribution function (currently unused — kept for API compat).
    index : int
        Row index, used for pattern-based sequential values.

    Returns
    -------
    The generated value (str, int, float, bool, or None).
    """
    field_type = column.get("type", "string").lower()
    nullable = column.get("nullable", False)

    # --- Nullable check ---
    null_chance = column.get("null_chance", 0.1 if nullable else 0.0)
    if random.random() < null_chance:
        return None

    try:
        # ---- PATTERN / SEQUENTIAL (Prioritized for ID/Roll formats) ----
        if column.get("pattern_sample") or (field_type == "pattern"):
            sample = column.get("pattern_sample") or column.get("pattern", "ID001")
            # If we have choices AND a pattern, and choices has only one item that's likely the sample,
            # we prefer the pattern to allow sequential generation.
            choices = column.get("choices")
            if not choices or not isinstance(choices, (list, tuple)) or len(choices) == 1:
                return generate_from_pattern(sample, index=index)

        choices = column.get("choices")
        if choices:
            # If it's a name/email and we have prefix/suffix, skip choices if they match prefix/suffix
            # This allows the name generator to use the prefix rather than returning it as a choice.
            if field_type in ["name", "email"] and (column.get("prefix") or column.get("suffix")):
                pass
            else:
                return generate_choice(choices)
        
        # Helper to pick one if prefix/suffix is a list
        def pick_one(val):
            if isinstance(val, list) and val:
                return random.choice(val)
            return val

        # ---- SPECIALIZED TYPES (Handle their own prefix/suffix natively) ----
        prefix = column.get("prefix")
        suffix = column.get("suffix")

        if field_type == "email":
            return generate_email(prefix=pick_one(prefix), suffix=pick_one(suffix), index=index)

        if field_type == "name":
            return generate_name(starts_with=pick_one(prefix), ends_with=pick_one(suffix), use_pool=(index > 10000))

        if field_type == "first_name":
            return generate_first_name(starts_with=pick_one(prefix), ends_with=pick_one(suffix))

        if field_type == "last_name":
            return generate_last_name(starts_with=pick_one(prefix), ends_with=pick_one(suffix))

        # ---- GENERIC PREFIX / SUFFIX COMBINED ----
        if prefix or suffix:
            # Standard prepend/append logic for simple types (integer, float, text, etc.)
            col_copy = column.copy()
            col_copy.pop("prefix", None)
            col_copy.pop("suffix", None)
            
            base = generate_field(col_copy, distribution_func, index)
            if base is None:
                base = ""
            
            res = str(base)
            if prefix:
                p = random.choice(prefix) if isinstance(prefix, list) else prefix
                res = f"{p}{res}"
            if suffix:
                s = random.choice(suffix) if isinstance(suffix, list) else suffix
                res = f"{res}{s}"
            return res

        # ---- INTEGER ----
        if field_type == "integer":
            min_v = column.get("min", 0)
            max_v = column.get("max", 100)
            multiple_of = column.get("multiple_of")

            # Smart Magnitude Rounding: Only apply if user DID NOT specify a multiplier themselves
            # AND the column name doesn't contain "year"
            if not multiple_of and "year" not in column.get("name", "").lower():
                # Only round if range is significantly large
                range_size = int(max_v) - int(min_v)
                if range_size >= 1000:
                    power = len(str(range_size)) - 2
                    if power >= 1:
                        multiple_of = 10 ** power
            
            min_v, max_v = int(min_v), int(max_v)
            if min_v > max_v:
                min_v, max_v = max_v, min_v
            
            return generate_integer(min_v, max_v, multiple_of=multiple_of)

        # ---- FLOAT / PERCENTAGE ----
        if field_type in ("float", "percentage"):
            min_v = column.get("min", 0.0)
            max_v = column.get("max", 100.0)
            multiple_of = column.get("multiple_of")
            
            min_v, max_v = float(min_v), float(max_v)
            if min_v > max_v:
                min_v, max_v = max_v, min_v
            return generate_float(min_v, max_v, multiple_of=multiple_of)

        # ---- EMAIL ----
        if field_type == "email":
            return generate_email(index=index)

        # ---- UUID ----
        if field_type == "uuid":
            return generate_uuid_value(index=index)

        # ---- NAME ----
        if field_type == "name":
            return generate_name(use_pool=(index > 10000))

        # ---- FIRST NAME ----
        if field_type == "first_name":
            # For simplicity, we use the pool logic inside generate_name or could add to generate_first_name
            return generate_first_name()

        # ---- LAST NAME ----
        if field_type == "last_name":
            return generate_last_name()

        # ---- PHONE ----
        if field_type == "phone":
            length = column.get("length", 10)
            return generate_phone(length=length)

        # ---- ADDRESS ----
        if field_type == "address":
            return generate_address()

        # ---- CITY ----
        if field_type == "city":
            return generate_city()

        # ---- STATE ----
        if field_type == "state":
            return generate_state()

        # ---- COUNTRY ----
        if field_type == "country":
            return generate_country()

        # ---- PINCODE ----
        if field_type == "pincode":
            return generate_pincode()

        # ---- DATE ----
        if field_type == "date":
            min_y = column.get("min")
            max_y = column.get("max")
            return generate_date(min_year=min_y, max_year=max_y)

        # ---- HEALTHCARE SPECIALIZED ----
        if field_type == "blood_pressure":
            return generate_blood_pressure()
        
        if field_type == "bmi":
            return generate_bmi()

        # ---- BOOLEAN ----
        if field_type == "boolean":
            return generate_boolean()

        # ---- TEXT ----
        if field_type == "text":
            return generate_text()

        # ---- IP ----
        if field_type == "ip":
            return generate_ip()

        # ---- MAC ----
        if field_type == "mac":
            return generate_mac()

        # ---- JSON ----
        if field_type == "json":
            return generate_json()

        # ---- STRING (fallback) ----
        return generate_string()

    except Exception as exc:
        logger.warning("Field generation failed for %s: %s", column.get("name"), exc)
        return None
