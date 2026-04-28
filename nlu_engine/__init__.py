"""
nlu_engine package
Public API for intent classification and entity extraction.
"""

import json
import os

from .train_intent import train_intent_model
from .infer_intent import load_intent_model, reload_intent_model, predict_intent
from .entity_extractor import extract_entities

_INTENTS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "intents.json")


def load_intents() -> list[dict]:
    """Load intents from data/intents.json."""
    if os.path.exists(_INTENTS_PATH):
        with open(_INTENTS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_intents(intents: list[dict]) -> None:
    """Persist intents back to data/intents.json."""
    os.makedirs(os.path.dirname(_INTENTS_PATH), exist_ok=True)
    with open(_INTENTS_PATH, "w", encoding="utf-8") as f:
        json.dump(intents, f, indent=2, ensure_ascii=False)


__all__ = [
    "load_intents",
    "save_intents",
    "train_intent_model",
    "load_intent_model",
    "reload_intent_model",
    "predict_intent",
    "extract_entities",
]
