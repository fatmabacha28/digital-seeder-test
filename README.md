# Projet Flask : Classification de Documents par IA

Ce projet a été réalisé dans le cadre d'un test technique pour une alternance. Il permet de :
1. Uploader un fichier PDF.
2. Extraire et nettoyer le texte du PDF.
3. Utiliser un modèle de Machine Learning (NLP) pour classifier le document dans une catégorie (`BUSINESS`, `ENTERTAINMENT`, `AUTRE`).
4. Déclencher une action spécifique selon la catégorie :
   - **BUSINESS** : Envoi d'un e-mail via MailHog avec le texte du document et le PDF en pièce jointe.
   - **ENTERTAINMENT** : Génération et téléchargement d'un fichier agenda `.ics`.
   - **AUTRE** : Action par défaut (affichage du résultat).

## Architecture

L'application est découpée de manière professionnelle (MVC/Service Pattern) :
- `app/` : L'application web Flask
  - `routes.py` : Les contrôleurs et routes de l'API/Web.
  - `services/` : La logique métier séparée par domaine (PDF, Machine Learning, Actions).
  - `templates/` & `static/` : L'interface utilisateur.
  - `config.py` : La configuration.
- `notebook/` : Les scripts de Machine Learning et d'entraînement du modèle.
- `models/` : Le stockage du modèle entraîné (`.joblib`).
- `docker-compose.yml` : La configuration Docker pour l'orchestration de Flask et de MailHog.

## Prérequis
- Docker et docker-compose
- (Optionnel) Python 3.9+ pour exécution locale hors Docker

## Installation et Lancement (avec Docker)

1. Clonez ce dépôt.
2. Placez-vous à la racine du projet.
3. Exécutez :
   ```bash
   docker-compose up --build
   ```
4. Accédez à l'application web : [http://localhost:5000](http://localhost:5000)
5. Accédez à l'interface MailHog pour visualiser les e-mails : [http://localhost:8025](http://localhost:8025)

## Utilisation de l'IA (Modèle)

Le projet intègre un modèle pré-généré pour faciliter les tests. Si vous souhaitez re-générer ou améliorer le modèle :
1. Installer les dépendances : `pip install -r requirements.txt`
2. Aller dans le dossier `notebook` : `cd notebook`
3. Exécuter le script de génération : `python generate_model.py`
Vous pouvez aussi utiliser le fichier `train_model.ipynb` pour une approche exploratoire sous Jupyter.
