# nlp_manager/utils.py

import logging

# Create a logger for NLP Manager
logger = logging.getLogger("nlp_manager")
logger.setLevel(logging.INFO)

# Format of log messages
formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(message)s",
    "%Y-%m-%d %H:%M:%S"
)

# Console handler (prints logs to terminal)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def log_intent(text: str, intent_result: dict):
    """
    Log intent predictions for debugging & future fine-tuning.
    """
    logger.info(f"USER TEXT: {text}")
    logger.info(f"INTENT RESULT: {intent_result}")


def log_entities(text: str, entities: dict):
    """
    Log extracted entities (rows, columns, types, etc.)
    """
    logger.info(f"ENTITY EXTRACTION INPUT: {text}")
    logger.info(f"EXTRACTED ENTITIES: {entities}")


def log_spec(spec: dict):
    """
    Log the final built dataset specification.
    """
    logger.info(f"FINAL SPEC: {spec}")
