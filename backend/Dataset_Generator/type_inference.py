def infer_type(column_name: str) -> str:
    col = column_name.lower()

    if "id" in col:
        return "uuid"
    if "email" in col:
        return "email"
    if "phone" in col or "mobile" in col:
        return "phone"
    if "date" in col or "time" in col:
        return "date"
    if "age" in col or "count" in col:
        return "integer"
    if "price" in col or "salary" in col or "amount" in col or "marks" in col or "score" in col:
        return "integer"
    if "name" in col:
        return "name"
    if "description" in col or "text" in col:
        return "text"

    return "string"
