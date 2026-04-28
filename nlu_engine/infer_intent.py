"""
infer_intent.py
Loads the trained model and exposes predict_intent().
"""

import os
import pickle

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "intent_model.pkl")

_cached_model = None


def load_intent_model():
    """Load and cache the trained pipeline. Returns None if not trained yet."""
    global _cached_model
    if _cached_model is not None:
        return _cached_model
    if not os.path.exists(MODEL_PATH):
        return None
    with open(MODEL_PATH, "rb") as f:
        _cached_model = pickle.load(f)
    return _cached_model


def reload_intent_model():
    """Force reload from disk (call after retraining)."""
    global _cached_model
    _cached_model = None
    return load_intent_model()


def predict_intent(text: str) -> dict:
    """
    Predict the intent of a user query.

    Returns:
        dict with keys:
            intent   (str)   — top predicted class
            confidence (float) — probability of top class (0–1)
            all_scores (dict)  — {intent: probability} for all classes
    """
    model = load_intent_model()
    if model is None:
        return {"intent": "unknown", "confidence": 0.0, "all_scores": {}}

    text_clean = text.strip().lower()
    proba = model.predict_proba([text_clean])[0]
    classes = model.classes_

    idx = int(proba.argmax())
    all_scores = {
        str(cls): round(float(p), 4)
        for cls, p in sorted(zip(classes, proba), key=lambda x: -x[1])
    }

    return {
        "intent": str(classes[idx]),
        "confidence": round(float(proba[idx]), 4),
        "all_scores": all_scores,
    }
