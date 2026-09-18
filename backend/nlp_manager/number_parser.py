# nlp_manager/number_parser.py
import re

WORD_NUMBERS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "ten": 10, "twenty": 20, "thirty": 30,
    "fifty": 50, "hundred": 100
}

from .universal_constraint_parser import _smart_number

def extract_rows(text: str):
    text = text.lower()

    # digit-based with optional units
    # Allows for "55 student records", "1 million rows", "100k entries"
    units = r'(?:k|m|b|t|thousand|million|billion|trillion|lakhs?|crores?)'
    m = re.search(rf'(\d+(?:\.\d+)?\s*{units}?)\s*(?:[\w\s]+\s+)?(?:rows|records|entries|samples|students?|employees?|patients?|pupils?|people|users?|items?|persons?|data)', text)
    if m:
        return _smart_number(m.group(1))

    # word-based
    for word, num in WORD_NUMBERS.items():
        if word in text:
            return num

    return None
