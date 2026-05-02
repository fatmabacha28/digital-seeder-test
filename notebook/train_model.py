import os
import re
import string
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download necessary NLTK data
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

def preprocess_text(text):
    if not isinstance(text, str):
        return ""
    # Lowercase
    text = text.lower()
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Remove numbers
    text = re.sub(r'\d+', '', text)
    # Tokenize (simple split for speed)
    tokens = text.split()
    # Remove stopwords and lemmatize
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
    return " ".join(tokens)

def train_and_evaluate():
    print("Loading dataset...")
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dataset', 'News_Category_Dataset_v3.json')
    
    # Load JSON lines
    records = []
    with open(data_path, 'r', encoding='utf-8') as f:
        for line in f:
            records.append(json.loads(line))
            
    df = pd.DataFrame(records)
    
    # Mapping categories
    # The News Category dataset has "HEALTHY LIVING" or "WELLNESS". We map them to HEALTH.
    health_aliases = ['HEALTHY LIVING', 'WELLNESS']
    
    def map_category(cat):
        if cat in ['BUSINESS', 'ENTERTAINMENT', 'SPORTS', 'TECH', 'POLITICS']:
            return cat
        elif cat in health_aliases:
            return 'HEALTH'
        else:
            return 'OTHER'
            
    df['category'] = df['category'].apply(map_category)
    
    print(f"Dataset initial distribution:\n{df['category'].value_counts()}\n")
    
    # Combine headline and short_description
    df['text'] = df['headline'] + " " + df['short_description']
    
    # Preprocessing
    print("Preprocessing text... (this may take a moment)")
    df['cleaned_text'] = df['text'].apply(preprocess_text)
    
    # Drop empty texts
    df = df[df['cleaned_text'].str.len() > 0]
    
    # Balance dataset
    # We want a balanced dataset so no class overpowers. We undersample all classes to the size of the smallest.
    # However, 'OTHER' is huge. We don't want OTHER to be too big. Let's sample min_size from all classes.
    min_size = df['category'].value_counts().min()
    # Limit maximum class size to something reasonable (e.g., 2000) so we don't train on too little data if one class is very small.
    # Actually, we will just use stratify and oversample if needed, or simple downsample.
    target_samples_per_class = min(2000, df['category'].value_counts().min())
    
    print(f"Balancing dataset to {target_samples_per_class} samples per class...")
    df_balanced = df.groupby('category').apply(lambda x: x.sample(n=target_samples_per_class, replace=len(x)<target_samples_per_class, random_state=42)).reset_index(drop=True)
    
    print(f"Balanced distribution:\n{df_balanced['category'].value_counts()}\n")
    
    X = df_balanced['cleaned_text']
    y = df_balanced['category']
    
    # Encode labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    # TF-IDF Vectorization
    print("Vectorizing text...")
    vectorizer = TfidfVectorizer(max_features=10000, ngram_range=(1, 2))
    X_vec = vectorizer.fit_transform(X)
    
    # Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X_vec, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)
    
    # Models to evaluate (With Probability calibration support)
    # LinearSVC does not support predict_proba natively, so we wrap it in CalibratedClassifierCV
    base_svc = LinearSVC(random_state=42, dual='auto')
    calibrated_svc = CalibratedClassifierCV(estimator=base_svc, method='sigmoid', cv=3)
    
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced'),
        "LinearSVC (Calibrated)": calibrated_svc,
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    }
    
    best_model = None
    best_f1_macro = 0
    best_model_name = ""
    
    print("\n--- Model Evaluation ---")
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)
        
        # We test the calibration rule: confidence < 0.55 => OTHER
        probas = model.predict_proba(X_test)
        max_probas = np.max(probas, axis=1)
        raw_preds = np.argmax(probas, axis=1)
        
        # Get the index for 'OTHER'
        other_idx = le.transform(['OTHER'])[0]
        
        # Apply threshold
        calibrated_preds = np.where(max_probas < 0.55, other_idx, raw_preds)
        
        acc = accuracy_score(y_test, calibrated_preds)
        report_dict = classification_report(y_test, calibrated_preds, target_names=le.classes_, output_dict=True)
        macro_f1 = report_dict['macro avg']['f1-score']
        
        print(f"{name} Accuracy (with threshold): {acc:.4f} | Macro F1: {macro_f1:.4f}")
        
        if macro_f1 > best_f1_macro:
            best_f1_macro = macro_f1
            best_model = model
            best_model_name = name

    print("\n=========================================")
    print(f"*** Best Model: {best_model_name} (Macro F1: {best_f1_macro:.4f}) ***")
    print("=========================================")
    
    # Detailed report for the best model
    probas = best_model.predict_proba(X_test)
    max_probas = np.max(probas, axis=1)
    raw_preds = np.argmax(probas, axis=1)
    other_idx = le.transform(['OTHER'])[0]
    final_preds = np.where(max_probas < 0.55, other_idx, raw_preds)
    
    print("\nFinal Classification Report (Confidence Threshold = 0.55):")
    print(classification_report(y_test, final_preds, target_names=le.classes_))
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, final_preds)
    
    # Pretty print confusion matrix
    cm_df = pd.DataFrame(cm, index=[f"True {c}" for c in le.classes_], columns=[f"Pred {c}" for c in le.classes_])
    print(cm_df)
    
    # Save the models
    models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    joblib.dump(best_model, os.path.join(models_dir, 'model.joblib'))
    joblib.dump(vectorizer, os.path.join(models_dir, 'vectorizer.joblib'))
    joblib.dump(le, os.path.join(models_dir, 'label_encoder.joblib'))
    
    print(f"\nPipeline complete. Models saved to {models_dir}")

if __name__ == "__main__":
    train_and_evaluate()
