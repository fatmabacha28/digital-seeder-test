import os
import re
import string
import numpy as np
import joblib
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

# ── Model cache ────────────────────────────────────────────────────────────────
_cache = {}

def load_models():
    if _cache:
        return _cache['model'], _cache['vectorizer'], _cache['le']

    base = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    paths = {
        'model':      os.path.join(base, 'models', 'model.joblib'),
        'vectorizer': os.path.join(base, 'models', 'vectorizer.joblib'),
        'le':         os.path.join(base, 'models', 'label_encoder.joblib'),
    }
    for key, path in paths.items():
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing: {path}. Run notebook/train_model.py first.")
        _cache[key] = joblib.load(path)

    return _cache['model'], _cache['vectorizer'], _cache['le']


# ── Text preprocessing (mirrors train_model.py) ────────────────────────────────
def preprocess_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'\d+', '', text)
    tokens = text.split()
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(t) for t in tokens if t not in stop_words and len(t) > 2]
    return " ".join(tokens)


# ── Top keywords from TF-IDF ───────────────────────────────────────────────────
def get_top_keywords(vectorizer, processed_text: str, top_n: int = 6) -> list:
    try:
        feature_names = vectorizer.get_feature_names_out()
        vec = vectorizer.transform([processed_text])
        scores = vec.toarray()[0]
        top_indices = scores.argsort()[::-1][:top_n]
        keywords = [feature_names[i] for i in top_indices if scores[i] > 0]
        return keywords
    except Exception:
        return []


# ── Main prediction function ───────────────────────────────────────────────────
CONFIDENCE_THRESHOLD = 0.55

def predict_category(raw_text: str) -> dict:
    """
    Returns a dict with:
        category  : str
        confidence: float (0-100)
        keywords  : list[str]
        all_scores: dict {label: pct}
    """
    if not raw_text or not raw_text.strip():
        return {"category": "OTHER", "confidence": 0.0, "keywords": [], "all_scores": {}}

    model, vectorizer, le = load_models()

    processed = preprocess_text(raw_text)
    if not processed:
        processed = raw_text

    X = vectorizer.transform([processed])

    # Probabilities
    try:
        probas = model.predict_proba(X)[0]
        max_proba = float(np.max(probas))
        pred_idx  = int(np.argmax(probas))

        if max_proba < CONFIDENCE_THRESHOLD:
            category = "OTHER"
            confidence = max_proba * 100
        else:
            category   = le.inverse_transform([pred_idx])[0]
            confidence = max_proba * 100

        all_scores = {
            le.inverse_transform([i])[0]: round(float(p) * 100, 1)
            for i, p in enumerate(probas)
        }
    except AttributeError:
        # Fallback for models without predict_proba
        pred = model.predict(X)
        category   = le.inverse_transform(pred)[0]
        confidence = 0.0
        all_scores = {}

    keywords = get_top_keywords(vectorizer, processed)

    return {
        "category":   category,
        "confidence": round(confidence, 1),
        "keywords":   keywords,
        "all_scores": all_scores,
    }
