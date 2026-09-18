# nlp_manager/config.py

# All intents the system can understand
INTENT_LABELS = [
    "generate_dataset",
    "clarify",
    "explain_code",
    "fetch_real_dataset",
    "preview",
    "export",
    "edit_dataset",
    "cancel"
]

# Example sentences for each intent
# These help the sentence-transformer model match user input
INTENT_PROTOTYPES = {
    "generate_dataset": [
        "I want a dataset",
        "create a dataset",
        "generate 100 rows of data",
        "make synthetic data",
        "build me a dataset"
    ],
    "clarify": [
        "I'm not sure",
        "help me decide",
        "I need clarification",
        "explain the options"
    ],
    "explain_code": [
        "explain this code",
        "what does this code need",
        "what dataset should this code use",
        "analyze my code"
    ],
    "fetch_real_dataset": [
        "get real dataset",
        "fetch data from database",
        "retrieve real world data",
        "find existing dataset"
    ],
    "preview": [
        "show preview",
        "preview the data",
        "display table",
        "show me sample rows"
    ],
    "export": [
        "download as csv",
        "export json",
        "export excel",
        "save this file"
    ],
    "edit_dataset": [
        "edit the dataset",
        "modify columns",
        "change distribution",
        "update the table"
    ],
    "cancel": [
        "stop",
        "cancel this",
        "end the task",
        "nevermind"
    ]
}

# Minimum confidence needed for accepting an intent
CONFIDENCE_THRESHOLD = 0.55
