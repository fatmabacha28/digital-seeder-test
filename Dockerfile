FROM python:3.9-slim

WORKDIR /app

# Installation des dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers de configuration
COPY requirements.txt .

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Téléchargement des ressources NLTK
RUN python -m nltk.downloader punkt stopwords

# Copie du reste de l'application
COPY . .

# Exposition du port Flask
EXPOSE 5000

# Commande de lancement
CMD ["python", "app/run.py"]
