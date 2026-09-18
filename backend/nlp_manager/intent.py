from sentence_transformers import SentenceTransformer, util
import numpy as np

# --- GLOBAL SINGLETON MODEL ---
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME)

# --- INTENT DEFINITIONS ---
INTENTS = {
    "generate_tabular_data": [
        "create a dataset",
        "generate table data",
        "make synthetic data",
        "generate csv file",
        "create structured dataset",
        "generate students data table",
        "create a table of students",
        "generate records for students",
        "I am writing a story about 30 students, generate their data",
        "making a novel about students, help me with their records",
        "generate a dataset for my book characters",
        "help me create a table of characters for a story"
    ],
    "generate_text_data": [
        "generate text data",
        "create sentences",
        "generate paragraphs",
        "create reviews dataset"
    ],
    "unknown": [
        "hello",
        "how are you",
        "what can you do"
    ]
}

# --- PRECOMPUTE INTENT EMBEDDINGS ---
intent_embeddings = {
    intent: model.encode(samples, convert_to_tensor=True)
    for intent, samples in INTENTS.items()
}

# --- INTENT PREDICTION FUNCTION ---
def predict_intent(user_query: str):
    query_embedding = model.encode(user_query, convert_to_tensor=True)

    best_intent = None
    best_score = -1

    for intent, embeddings in intent_embeddings.items():
        score = util.cos_sim(query_embedding, embeddings).max().item()
        if score > best_score:
            best_score = score
            best_intent = intent

    return {
        "intent": best_intent,
        "confidence": round(best_score, 3)
    }
