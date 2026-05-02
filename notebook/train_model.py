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
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report
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
    
    # Target categories
    target_categories = ['BUSINESS', 'ENTERTAINMENT', 'SPORTS', 'TECH', 'POLITICS']
    df = df[df['category'].isin(target_categories)].copy()
    
    print(f"Dataset size after filtering: {len(df)}")
    
    # Combine headline and short_description
    df['text'] = df['headline'] + " " + df['short_description']
    
    print("Preprocessing text... (this may take a moment)")
    df['cleaned_text'] = df['text'].apply(preprocess_text)
    
    # Drop empty texts
    df = df[df['cleaned_text'].str.len() > 0]
    
    # Balance dataset by under-sampling to the minimum class size
    min_size = df['category'].value_counts().min()
    print(f"Balancing dataset to {min_size} samples per class...")
    df_balanced = df.groupby('category').apply(lambda x: x.sample(n=min_size, random_state=42)).reset_index(drop=True)
    
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
    X_train, X_test, y_train, y_test = train_test_split(X_vec, y_encoded, test_size=0.2, random_state=42)
    
    # Models to evaluate
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "LinearSVC": LinearSVC(random_state=42),
        "MultinomialNB": MultinomialNB()
    }
    
    best_model = None
    best_accuracy = 0
    best_model_name = ""
    
    print("\n--- Model Evaluation ---")
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        print(f"{name} Accuracy: {acc:.4f}")
        
        if acc > best_accuracy:
            best_accuracy = acc
            best_model = model
            best_model_name = name

    print("\n=========================================")
    print(f"*** Best Model: {best_model_name} (Accuracy: {best_accuracy:.4f}) ***")
    print("=========================================")
    
    # Print full classification report for the best model
    y_pred_best = best_model.predict(X_test)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred_best, target_names=le.classes_))
    
    # Save the models
    models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    joblib.dump(best_model, os.path.join(models_dir, 'model.joblib'))
    joblib.dump(vectorizer, os.path.join(models_dir, 'vectorizer.joblib'))
    joblib.dump(le, os.path.join(models_dir, 'label_encoder.joblib'))
    
    print(f"\nModels successfully saved to {models_dir}")

if __name__ == "__main__":
    train_and_evaluate()
