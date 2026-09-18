# nlp_manager/column_suggester.py

import re
import difflib
from nlp_manager.schema_registry import SCHEMA_REGISTRY

# words and common values that are NEVER columns
STOP_WORDS = {
    "unique", "distinct", "nunique", "only",
    "rows", "row", "records", "data", "dataset",
    "with", "and", "between", "from", "to",
    "starts", "ends", "like", "format", "pattern",
    "as", "either", "among", "one", "of",
    # Common categorical values (keep lowercase)
    "male", "female", "other", "m", "f", "o",
    "active", "suspended", "graduated", "inactive", "on", "leave", "dismissed",
    "undergraduate", "graduate", "postgraduate",
    "full-time", "part-time", "probation"
}    


def suggest_column(token: str, domain: str):
    """
    Suggest closest valid column name using schema registry.
    """
    domain_schema = SCHEMA_REGISTRY.get(domain, SCHEMA_REGISTRY["generic"])
    column_defs = domain_schema["columns"]

    all_names = []
    alias_to_canonical = {}

    for canonical, meta in column_defs.items():
        variants = [canonical, canonical + "s"]
        if canonical.endswith('y'):
            variants.append(canonical[:-1] + "ies")
        if canonical.endswith('s') or canonical.endswith('ch') or canonical.endswith('sh') or canonical.endswith('x'):
             variants.append(canonical + "es")
             
        for alias in meta.get("aliases", []):
            variants.append(alias)
            variants.append(alias + "s")
            if alias.endswith('y'):
                variants.append(alias[:-1] + "ies")
            if alias.endswith('s') or alias.endswith('ch') or alias.endswith('sh') or alias.endswith('x'):
                variants.append(alias + "es")
        
        for v in variants:
            all_names.append(v)
            alias_to_canonical[v] = canonical

    token = token.lower().strip()
    # direct alias hit
    if token in alias_to_canonical:
        return alias_to_canonical[token]

    # fuzzy match
    match = difflib.get_close_matches(token, all_names, n=1, cutoff=0.8)
    if match:
        return alias_to_canonical.get(match[0], match[0])

    return None


def clean_and_suggest(raw_columns, domain):
    """
    Cleans tokens and suggests valid columns.
    """
    final_columns = []
    suggestions = []

    for raw in raw_columns:
        raw_l = raw.lower().strip()
        
        # 1. Advanced Matcher: Find ALL aliases that appear as substrings
        # We want to find the longest alias possible (e.g. "phone number" > "phone")
        matches_in_segment = []
        
        # 0. Find if there's a constraint keyword in this segment
        # If so, we should probably only look for columns BEFORE it
        constraint_keywords = [
            " starts with ", " ends with ", " like ", " format ", " pattern ",
            " formatted like ", " greater than ", " less than ", " higher than ",
            " lower than ", " between ", " in ", " matches ", " multiple of ",
            " increments of ", " step ", " is ", " as ", " prefix ", " suffix ",
            " are ", " should be ", " is null ", " are null ", " are empty "
        ]
        cutoff = len(raw_l)
        for kw in constraint_keywords:
            idx = raw_l.find(kw)
            if idx != -1 and idx < cutoff:
                cutoff = idx

        domain_schema = SCHEMA_REGISTRY.get(domain, SCHEMA_REGISTRY["generic"])
        column_defs = domain_schema["columns"]

        for canonical, meta in column_defs.items():
            variants = [canonical, canonical + "s"]
            if canonical.endswith('y'):
                variants.append(canonical[:-1] + "ies")
            if canonical.endswith('s') or canonical.endswith('ch') or canonical.endswith('sh') or canonical.endswith('x'):
                 variants.append(canonical + "es")

            for alias in meta.get("aliases", []):
                variants.append(alias)
                variants.append(alias + "s")
                if alias.endswith('y'):
                    variants.append(alias[:-1] + "ies")
                if alias.endswith('s') or alias.endswith('ch') or alias.endswith('sh') or alias.endswith('x'):
                    variants.append(alias + "es")
            
            for alias in sorted(list(set(variants)), key=len, reverse=True):
                alias_l = alias.lower()
                # Check if alias is a whole word or phrase in segment
                pattern = rf"\b{re.escape(alias_l)}\b"
                for match_found in re.finditer(pattern, raw_l):
                    # IGNORE if match starts after the constraint keyword cutoff
                    if match_found.start() >= cutoff and cutoff > 0:
                        continue

                    matches_in_segment.append({
                        "alias": alias_l,
                        "canonical": canonical,
                        "start": match_found.start(),
                        "end": match_found.end(),
                        "length": len(alias_l)
                    })

        if matches_in_segment:
            # Sort by length descending to prioritize longer matches in case of overlaps
            matches_in_segment.sort(key=lambda x: x["length"], reverse=True)
            
            used_indices = set()
            for m in matches_in_segment:
                # Check for overlap with already accepted (longer) matches
                if any(m["start"] >= s and m["end"] <= e for s, e in used_indices):
                    continue
                if any(m["start"] < e and m.get("end") > s for s, e in used_indices):
                     # Partial overlap - still better to skip if a longer one is already there
                     continue

                final_columns.append(m["canonical"])
                used_indices.add((m["start"], m["end"]))
                suggestions.append({
                    "input": m["alias"],
                    "suggested": m["canonical"],
                    "confidence": "high"
                })
                # Register the indices used
                for idx in range(m["start"], m["end"]):
                    used_indices.add((m["start"], m["end"])) # Optimization: just store the range
                    break # We only need to add it once
            continue

        # 2. Fallback to basic suggestion if no clear alias found in substring
        suggested = suggest_column(raw_l, domain)
        if suggested:
            final_columns.append(suggested)
            suggestions.append({
                "input": raw_l,
                "suggested": suggested,
                "confidence": "high"
            })

    # remove duplicates only if they are the exact same canonical AND input alias
    seen = set()
    result = []
    filtered_suggestions = []
    for col, sug in zip(final_columns, suggestions):
        key = (col, sug["input"])
        if key not in seen:
            seen.add(key)
            result.append(col)
            filtered_suggestions.append(sug)

    return result, filtered_suggestions
