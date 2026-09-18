# nlp_manager/column_resolver.py

from nlp_manager.schema_registry import SCHEMA_REGISTRY

CONSTRAINT_KEYWORDS = {
    "unique": "unique",
    "distinct": "unique",
    "nunique": "unique"
}

def resolve_columns(raw_columns, domain="generic"):
    resolved = []

    domain_schema = SCHEMA_REGISTRY.get(domain, SCHEMA_REGISTRY["generic"])
    column_defs = domain_schema["columns"]
    seen = set()

    for idx, raw in enumerate(raw_columns):
        raw_l = raw.lower().strip()
        tokens = raw_l.split()
        constraints = {}

        # We also try the whole raw string as a single token (e.g. "math score")
        # Map processed_token -> original_token
        token_map = {raw_l: raw_l}
        for t in tokens:
            t_clean = t.strip(",.;:()\"'")
            if not t_clean: continue
            token_map[t_clean] = t_clean
            if t_clean.endswith('s'):
                token_map[t_clean[:-1]] = t_clean
            if t_clean.endswith('es') and len(t_clean) > 3:
                token_map[t_clean[:-2]] = t_clean
            if t_clean.endswith('ies') and len(t_clean) > 4:
                token_map[t_clean[:-3] + 'y'] = t_clean
        
        clean_tokens = list(token_map.keys())

        # Constraint detection (moved outside the main token loop to apply to the whole raw_column)
        # This part is based on the original code's intent for constraints,
        # but the provided diff removed the constraint detection from the inner loop.
        # To maintain functionality, we re-introduce it here, applying to the original raw string.
        # If the intent was to remove constraint detection entirely, this block should be removed.
        for token_for_constraint in raw_l.split():
            if token_for_constraint in CONSTRAINT_KEYWORDS:
                constraints[CONSTRAINT_KEYWORDS[token_for_constraint]] = True


        tokens_resolved_in_this_segment = set()
        for token in sorted(clean_tokens, key=len, reverse=True):
            for canonical, meta in column_defs.items():
                aliases = meta.get("aliases", [])
                if token == canonical or token in aliases:
                    # Deduplicate within THIS segment (e.g. "marks" matching both "marks" and "mark" alias)
                    if canonical in tokens_resolved_in_this_segment:
                        continue
                    
                    # Allow same (canonical, token) pair if it comes from a different segment instance
                    if (canonical, token, idx) in seen:
                        continue
                    seen.add((canonical, token, idx))
                    tokens_resolved_in_this_segment.add(canonical)

                    col_schema = {
                        "name": canonical,
                        "type": meta["type"],
                        "input_token": token_map.get(token, token)
                    }

                    for k, v in meta.items():
                        if k not in ["type"]:
                            col_schema[k] = v

                    col_schema.update(constraints)
                    resolved.append(col_schema)

    return resolved
    