"""
train_intent.py
Trains a TF-IDF + LogisticRegression intent classifier and saves it to disk.
"""

import os
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score
import numpy as np

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
MODEL_PATH = os.path.join(MODEL_DIR, "intent_model.pkl")


def train_intent_model(intents: list[dict]) -> dict:
    """
    Train a TF-IDF + LogisticRegression pipeline on the provided intents.

    Args:
        intents: list of {"name": str, "examples": [str, ...]}

    Returns:
        dict with keys: success (bool), message (str), accuracy (float|None)
    """
    os.makedirs(MODEL_DIR, exist_ok=True)

    texts, labels = [], []
    for intent in intents:
        for example in intent.get("examples", []):
            if example.strip():
                texts.append(example.strip().lower())
                labels.append(intent["name"])

    n_classes = len(set(labels))

    if n_classes < 2:
        return {
            "success": False,
            "message": "Need at least 2 intents with examples to train.",
            "accuracy": None,
        }

    if len(texts) < n_classes * 2:
        return {
            "success": False,
            "message": f"Too few examples ({len(texts)}). Add more training data.",
            "accuracy": None,
        }

    pipeline = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                ngram_range=(1, 2),
                sublinear_tf=True,
                min_df=1,
                analyzer="word",
            ),
        ),
        (
            "clf",
            LogisticRegression(
                max_iter=1000,
                C=5.0,
                solver="lbfgs",
            ),
        ),
    ])

    # Cross-validation for accuracy estimate (only if enough samples)
    accuracy = None
    cv_folds = min(5, min(len([l for l in labels if labels.count(l)]) , 3))
    if len(texts) >= cv_folds * n_classes:
        try:
            scores = cross_val_score(pipeline, texts, labels, cv=cv_folds, scoring="accuracy")
            accuracy = round(float(np.mean(scores)) * 100, 1)
        except Exception:
            accuracy = None

    pipeline.fit(texts, labels)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(pipeline, f)

    acc_str = f" — CV accuracy: {accuracy}%" if accuracy is not None else ""
    return {
        "success": True,
        "message": (
            f"Model trained on {len(texts)} examples across {n_classes} intents{acc_str}."
        ),
        "accuracy": accuracy,
    }
