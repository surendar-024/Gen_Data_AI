import re
_RE_DYNAMIC_LESS = re.compile(
    r'(?:\b([\w\s]+?)\s+)?(?:is\s+)?(?:below|less\s+than|under|at\s+most|maximum|max|should\s+be\s+lower\s+than|must\s+be\s+lower\s+than|lower\s+than)\s+(?:the\s+)?([\w\s]+?)(?=\s+and\b|$)',
    re.IGNORECASE,
)

text = "scholarship multiple of 2500 and lower than the fees"

print(f"Testing text: {text}")
for match in _RE_DYNAMIC_LESS.finditer(text):
    print(f"Match found: {match.group(0)}")
    print(f"Group 1 (col): {match.group(1)}")
    print(f"Group 2 (target): {match.group(2)}")
