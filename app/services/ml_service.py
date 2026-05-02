import os
import joblib

import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

def load_models():
    """Charge le modèle ML, le vectorizer et l'encodeur de labels."""
    try:
        model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models', 'model.joblib')
        vectorizer_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models', 'vectorizer.joblib')
        le_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models', 'label_encoder.joblib')
        
        if not all(os.path.exists(p) for p in [model_path, vectorizer_path, le_path]):
            raise FileNotFoundError("Les fichiers du modèle sont introuvables. Lancez notebook/train_model.py d'abord.")

        model = joblib.load(model_path)
        vectorizer = joblib.load(vectorizer_path)
        le = joblib.load(le_path)
        return model, vectorizer, le
    except Exception as e:
        print(f"Erreur lors du chargement des modèles : {e}")
        raise

def preprocess_text_ml(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'\d+', '', text)
    tokens = text.split()
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
    return " ".join(tokens)

def predict_category(cleaned_text):
    """Prédit la catégorie d'un texte donné."""
    if not cleaned_text:
        return "OTHER"

    model, vectorizer, le = load_models()
    
    # Preprocessing avancé comme pour l'entraînement
    processed_text = preprocess_text_ml(cleaned_text)
    if not processed_text:
        processed_text = cleaned_text # Fallback
    
    # Vectorisation du texte
    X_new = vectorizer.transform([processed_text])
    
    # Prédiction avec probabilité
    try:
        import numpy as np
        probas = model.predict_proba(X_new)
        max_proba = np.max(probas, axis=1)[0]
        raw_pred = np.argmax(probas, axis=1)
        
        if max_proba < 0.55:
            prediction_label = "OTHER"
        else:
            prediction_label = le.inverse_transform(raw_pred)[0]
    except AttributeError:
        # Fallback
        prediction_encoded = model.predict(X_new)
        prediction_label = le.inverse_transform(prediction_encoded)[0]
    
    return prediction_label
