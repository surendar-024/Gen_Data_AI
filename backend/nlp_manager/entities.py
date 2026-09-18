# nlp_manager/entities.py

import re
import spacy
import logging
from nlp_manager.schema_registry import SCHEMA_REGISTRY

logger = logging.getLogger("nlp_manager.entities")

nlp = spacy.load("en_core_web_sm")

DOMAIN_KEYWORDS = {
    "student": [
        "student", "college", "school", "university", "campus",
        "enrollment", "enrolment", "semester", "academic",
        "marks", "grade", "gpa", "cgpa", "exam", "examination",
        "classroom", "lecture", "professor", "teacher",
        "department", "graduation", "undergraduate", "postgraduate",
        "fresher", "alumni", "batch", "hostel", "dormitory",
        "syllabus", "curriculum", "coursework",
        "roll_number", "rollnumber", "roll_no", "rollno",
        "blood_group", "bloodgroup", "birth_date", "dob",
        "scholarship", "fees", "attendance", "father", "mother",
    ],
    "employee": [
        "employee", "staff", "company", "salary", "workplace", "department", "hire_date", "manager",
        "corporate", "office", "hr", "human_resources", "payroll", "ctc", "salary_pay",
        "designation", "employment", "experience", "notice_period", "work_mode", "job_title"
    ],
    "healthcare": [
        "patient", "hospital", "medical", "doctor", "clinic", "diagnosis", "prescription",
        "physician", "vitals", "blood_pressure", "heart_rate", "bmi", "treatment", "symptoms",
        "admission", "discharge", "mrn", "insurance", "billing", "medication", "dosage", "lab_result",
        "health", "healthcare", "clinical", "surgery", "ward", "room_number"
    ],
    "sales": [
        "sales", "supermarket", "revenue", "product", "invoice", "order", "customer",
        "ecommerce", "e-commerce", "retail", "wholesale", "transaction", "purchase",
        "inventory", "sku", "stock", "billing", "shipping", "delivery", "payment",
        "coupon", "discount", "promo", "tracking", "courier", "logistics", "online_store",
        "cart", "checkout", "refund", "returns"
    ],
}


def extract_entities(text: str):
    text_l = text.lower()

    # ---- Domain Inference ----
    domain = None
    best_score = 0
    
    # 1. Check explicit domain keywords
    for key, keywords in DOMAIN_KEYWORDS.items():
        score = sum(2 for word in keywords if word in text_l) # Higher weight for direct keywords
        if score > best_score:
            best_score = score
            domain = key

    # 2. Check SCHEMA_REGISTRY for unique column aliases if score is still low
    if best_score < 4: 
        for key, schema in SCHEMA_REGISTRY.items():
            if key == "generic": continue
            col_score = 0
            for col_name, meta in schema.get("columns", {}).items():
                aliases = meta.get("aliases", [])
                if any(f" {a} " in f" {text_l} " or text_l.startswith(f"{a} ") or text_l.endswith(f" {a}") for a in aliases + [col_name]):
                    col_score += 1
            if col_score > best_score:
                best_score = col_score
                domain = key

    # If no match at all, leave domain as None (defaults to "generic")
    if best_score == 0:
        domain = None

    # ---- Raw columns extraction ----
    columns = []
    
    # We only trim if it's a known connector pattern immediately following domain/count
    # e.g. "50 students with...", "records where..."
    # We AVOID crossing punctuation or many words to prevent swallowing column names.
    connector_words = [
        r"with", r"where", r"having", r"including", r"containing", 
        r"should\s+have", r"must\s+have", r"will\s+have", r"have"
    ]
    pattern = "|".join([rf"\b{c}\b" for c in connector_words])
    
    # Restrictive trim: Only jump over small words (the, of, a)
    # Restrictive trim: Only jump over small words (the, of, a, me)
    trim_pattern = rf"(?:\b(?:{DOMAIN_KEYWORDS['student'][0]}|students?|employees?|people|pupils?|\d+|rows?|records?|data|million|billion|thousand|lakhs?|crores?)\b\s*(?:the\s+|of\s+|a\s+|me\s+|my\s+)*)(?:{pattern})"
    trim_match = re.search(trim_pattern, text_l, re.IGNORECASE)
    
    if trim_match and trim_match.start() < 60:
        after_connector = text[trim_match.end():].strip()
    else:
        # Fallback: simple split by common connectors if they appear early
        fallback_split = re.split(r'\s+(?:with|where|having|:)\s+', text, maxsplit=1, flags=re.IGNORECASE)
        if len(fallback_split) > 1 and len(fallback_split[0]) < 100:
             after_connector = fallback_split[1].strip()
        else:
             after_connector = text.strip()

    # Split by major separators: | and ;
    abbrev_neg = r'(?<!\bDr)(?<!\bProf)(?<!\bMr)(?<!\bMrs)(?<!\bMs)(?<!\bst)'
    major_sep = r'[|;]'
    period_sep = abbrev_neg + r'\.\s+(?=[A-Z]|Their|They|Also|But|Please|Make|Then|Finally|Moreover)'
    
    segments = re.split(rf'{major_sep}|{period_sep}', after_connector)
    
    # Keywords that indicate a connected phrase for the SAME column
    compound_keywords = [
        " between ", " in ", " as ", " greater ", " less ", 
        " lower ", " higher ", " below ", " above ", " multiple ", " optional",
        " smaller ", " larger ", " bigger ", " in between ",
        " ends with ", " starts with ", " formatted like ", " ending with ", " starting with ",
        " among ", " either ", " is ", " are ", " should be ", " must be ", " one of "
    ]

    all_aliases = []
    for schema in SCHEMA_REGISTRY.values():
        for col_name, meta in schema.get("columns", {}).items():
            all_aliases.append(col_name)
            all_aliases.append(col_name + "s")
            if col_name.endswith('y'):
                all_aliases.append(col_name[:-1] + "ies")
            
            for a in meta.get("aliases", []):
                all_aliases.append(a)
                all_aliases.append(a + "s")
                if a.endswith('s') or a.endswith('ch') or a.endswith('sh') or a.endswith('x'):
                    all_aliases.append(a + "es")
                if a.endswith('y'):
                    all_aliases.append(a[:-1] + "ies")
                
    all_aliases = sorted(list(set(all_aliases)), key=len, reverse=True)

    columns = []
    for seg in segments:
        seg = seg.strip()
        if not seg: continue

        chunks = re.split(r'(,\s*and\s+|\s+and\s+|,[\s,]*|\bbut\b|\bactually\b)', seg, flags=re.IGNORECASE)
        
        current_col_seg = chunks[0]
        for i in range(1, len(chunks), 2):
            sep = chunks[i]
            next_text = chunks[i+1].strip() if i+1 < len(chunks) else ""
            
            is_new_col = False
            next_text_l = next_text.lower()
            
            junk_words = [
                "but", "use", "also", "and", "for", "all", "the", "a", "an",
                "their", "his", "her", "its", "our", "this", "that", "these", "those",
                "distribution", "using", "normal", "uniform", "gaussian",
                "normally", "uniformly", "distributed", "follow", "follows",
                "unique", "distinct", "should", "must", "can", "be", "is", "are",
                "they", "them", "where", "having", "please", "make", "sure",
                "generate", "create", "give", "need", "show", "data", "records",
                "students", "employees", "pupils", "people", "items", "entries", "samples",
                "whose", "which", "with"
            ]
            next_text_cleaned = next_text_l
            while True:
                found_junk = False
                for j in junk_words:
                    if re.match(rf"^{j}\b", next_text_cleaned):
                        next_text_cleaned = next_text_cleaned[len(j):].strip()
                        found_junk = True
                        break
                if not found_junk:
                    break
            
            col_markers = [
                r"follow", r"is", r"are", r"should", r"must", r"between", r"greater", r"less", r"above", r"below"
            ]

            for alias in all_aliases:
                if next_text_cleaned.startswith(alias.lower() + " ") or next_text_cleaned == alias.lower():
                    is_new_col = True
                    break
                if any(re.match(rf"^{re.escape(alias.lower())}\s+(?:{m})\b", next_text_cleaned) for m in col_markers):
                    is_new_col = True
                    break
            
            if is_new_col:
                columns.append(current_col_seg.strip())
                current_col_seg = next_text
            else:
                current_col_seg += sep + next_text
        
        if current_col_seg:
            columns.append(current_col_seg.strip())

    filtered_columns = []
    for c in columns:
        c_strip = c.strip()
        if re.match(r'^(?:generate|create|i\s+need|give|make|show|provide)(?:\s+me)?(?:\s+my)?(?:\s+a)?\s+(?:\d+|million|billion|thousand|lakhs?|crores?|some|a|an)\b', c_strip, re.IGNORECASE):
            continue
        if c_strip:
            filtered_columns.append(c_strip)

    return {
        "domain": domain,
        "columns": filtered_columns
    }
