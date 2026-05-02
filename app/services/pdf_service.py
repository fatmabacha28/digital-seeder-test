import PyPDF2
import re
import nltk
from nltk.corpus import stopwords

# Téléchargement initial sécurisé (géré aussi dans le Dockerfile)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

def extract_text_from_pdf(filepath):
    """Extrait le texte brut d'un document PDF."""
    text = ""
    try:
        with open(filepath, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Erreur extraction PDF: {e}")
        raise e
    return text

def clean_text(text):
    """Nettoie le texte : minuscules, suppression ponctuation, stopwords."""
    # 1. Minuscules
    text = text.lower()
    
    # 2. Suppression de la ponctuation et caractères spéciaux (ne garde que lettres et chiffres)
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # 3. Suppression des chiffres (optionnel, selon le besoin)
    text = re.sub(r'\d+', ' ', text)
    
    # 4. Suppression des espaces multiples
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 5. Suppression des mots vides (stopwords)
    french_stopwords = set(stopwords.words('french'))
    english_stopwords = set(stopwords.words('english'))
    all_stopwords = french_stopwords.union(english_stopwords)
    
    words = text.split()
    cleaned_words = [word for word in words if word not in all_stopwords]
    
    return ' '.join(cleaned_words)
