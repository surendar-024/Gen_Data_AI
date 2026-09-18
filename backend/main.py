from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io
import csv
import json

from nlp_manager.intent import predict_intent
from nlp_manager.entities import extract_entities
from nlp_manager.postprocess import build_schema

from Dataset_Generator.generator import generate_dataset, generate_dataset_iter
from nlp_manager.validator import validate_schema, SchemaValidationError


app = FastAPI(title="GEN DATA AI Backend", description="Conversational Synthetic Dataset Generator",
    version="1.0.0")

class GenerateRequest(BaseModel):
    prompt: str


@app.post("/generate")
def generate(request: GenerateRequest):
    user_text = request.prompt

    intent_result = predict_intent(user_text)
    entities = extract_entities(user_text)
    schema = build_schema(intent_result=intent_result,
                           entities=entities, 
                           user_text=user_text)
    
    if isinstance(schema, dict) and schema.get("status") == "clarification_needed":
        return schema  
    validate_schema(schema) 

    # Limit preview to 1000 rows to prevent response bloat
    preview_rows = min(schema["rows"], 1000)
    data = generate_dataset(
        rows=preview_rows,
        columns=schema["columns"],
        distribution=schema["distribution"],
        domain=schema["domain"]
    )

    return {
        "intent": intent_result,
        "entities": entities,
        "schema": schema,
        "preview": data,
        "full_dataset_available": schema["rows"] > 1000,
        "message": f"Showing first {preview_rows} records. Use /download for the full dataset." if schema["rows"] > 1000 else None
    }


@app.post("/download")
def download(request: GenerateRequest):
    """
    Stream the full dataset as CSV.
    """
    user_text = request.prompt
    intent_result = predict_intent(user_text)
    entities = extract_entities(user_text)
    schema = build_schema(intent_result=intent_result, entities=entities, user_text=user_text)
    
    if isinstance(schema, dict) and schema.get("status") == "clarification_needed":
        return schema
    validate_schema(schema)

    def iter_csv():
        # Get column names for header
        cols = [c.get("output_name", c["name"]) for c in schema["columns"]]
        
        # Create a string buffer
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=cols)
        writer.writeheader()
        
        # Generate and yield rows in chunks to reduce overhead
        chunk_size = 1000
        current_chunk = 0
        
        for record in generate_dataset_iter(
            rows=schema["rows"],
            columns=schema["columns"],
            distribution=schema["distribution"],
            domain=schema["domain"]
        ):
            writer.writerow(record)
            current_chunk += 1
            
            if current_chunk >= chunk_size:
                yield output.getvalue()
                output.truncate(0)
                output.seek(0)
                current_chunk = 0
        
        # Final yield for remaining rows
        if current_chunk > 0:
            yield output.getvalue()

    return StreamingResponse(
        iter_csv(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=synthetic_data_{schema['domain']}.csv"}
    )