import os
import joblib

def load_model_and_vectorizer():
    """Charge le modèle ML et le vectorizer depuis les fichiers joblib."""
    try:
        # Les chemins sont relatifs au dossier de travail dans Docker ou local
        model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models', 'model.joblib')
        vectorizer_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models', 'vectorizer.joblib')
        
        if not os.path.exists(model_path) or not os.path.exists(vectorizer_path):
            raise FileNotFoundError("Les fichiers du modèle (model.joblib ou vectorizer.joblib) sont introuvables. Lancez le script de génération d'abord.")

        model = joblib.load(model_path)
        vectorizer = joblib.load(vectorizer_path)
        return model, vectorizer
    except Exception as e:
        print(f"Erreur lors du chargement du modèle : {e}")
        raise

def predict_category(cleaned_text):
    """Prédit la catégorie d'un texte donné."""
    if not cleaned_text:
        return "AUTRE"

    model, vectorizer = load_model_and_vectorizer()
    
    # Vectorisation du texte
    X_new = vectorizer.transform([cleaned_text])
    
    # Prédiction
    prediction = model.predict(X_new)
    
    return prediction[0]
