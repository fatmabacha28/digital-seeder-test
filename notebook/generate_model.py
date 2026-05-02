import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

def create_dummy_model():
    """
    Crée et sauvegarde un modèle scikit-learn très basique avec des données factices
    pour que l'application puisse fonctionner immédiatement.
    """
    print("Génération du modèle IA factice...")
    
    # Données factices
    X_train = [
        "contrat facture entreprise bilan financier chiffre affaire business plan",
        "réunion client stratégie commerciale marketing vente",
        "film cinéma acteur réalisateur festival projection ticket",
        "concert musique festival billet artiste scène",
        "recette cuisine ingrédient plat restaurant",
        "voiture réparation garage mécanique"
    ]
    
    y_train = [
        "BUSINESS",
        "BUSINESS",
        "ENTERTAINMENT",
        "ENTERTAINMENT",
        "AUTRE",
        "AUTRE"
    ]
    
    # Création du vectorizer et du modèle
    vectorizer = TfidfVectorizer()
    model = MultinomialNB()
    
    # Entraînement
    X_train_vec = vectorizer.fit_transform(X_train)
    model.fit(X_train_vec, y_train)
    
    # Chemins de sauvegarde
    models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    model_path = os.path.join(models_dir, 'model.joblib')
    vectorizer_path = os.path.join(models_dir, 'vectorizer.joblib')
    
    # Sauvegarde avec joblib
    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vectorizer_path)
    
    print(f"Modèle sauvegardé dans : {model_path}")
    print(f"Vectorizer sauvegardé dans : {vectorizer_path}")
    print("Succès !")

if __name__ == "__main__":
    create_dummy_model()
