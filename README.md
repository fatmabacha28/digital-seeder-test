# Digital Seeder AI — Document Classification

> **Solutions Digitales** · Built for a technical internship challenge

A professional Flask web application that classifies PDF documents using a fine-tuned NLP model and automatically triggers smart business workflows based on the predicted category.

---

## What it does

1. **Upload** a PDF document via drag & drop or file browser.
2. **Extract & clean** the text content from the PDF.
3. **Classify** the document using a scikit-learn NLP model into one of 7 categories.
4. **Display** the prediction with a confidence score, key signal words, and a category badge.
5. **Trigger** an automatic business action depending on the category.

---

## Supported Categories & Business Actions

| Category | Business Action |
|---|---|
| **BUSINESS** | Sends an email via MailHog (SMTP) with the PDF attached |
| **ENTERTAINMENT** | Generates a `.ics` calendar event file (downloadable) |
| **SPORTS** | Generates a `sports_report.txt` summary file (downloadable) |
| **TECH** | Logs the document to a SQLite database (viewable in `/tech-history`) |
| **POLITICS** | Generates a `politics_summary.txt` file (downloadable) |
| **HEALTH** | Generates a `health_report.txt` file (downloadable) |
| **OTHER** | No specific action (low-confidence fallback, threshold < 55%) |

---

## Key Features

- **AI Confidence Score** — Displayed as a percentage with a color-coded progress bar (green ≥ 75%, orange ≥ 55%, red < 55%)
- **Key Signal Words** — Top TF-IDF keywords that influenced the prediction, shown as tag chips
- **Auto-download** — Generated files (.ics, .txt) are directly downloadable from the result page
- **Dark Mode** — Toggle between light and dark theme (persisted in localStorage)
- **Tech History** — Dedicated page at `/tech-history` listing all TECH-classified documents from the SQLite DB
- **Responsive** — Mobile-first design

---

## Architecture

```
digital-seeder-test/
├── app/
│   ├── __init__.py          # App factory, config init
│   ├── routes.py            # HTTP routes & controllers
│   ├── config.py            # Configuration (paths, SMTP, etc.)
│   ├── database.py          # SQLite helpers (TECH logs)
│   ├── services/
│   │   ├── pdf_service.py   # PDF extraction & text cleaning
│   │   ├── ml_service.py    # Model loading, prediction, confidence, keywords
│   │   └── action_service.py# Business actions per category
│   ├── templates/
│   │   ├── index.html       # Main page (upload + result)
│   │   └── tech_history.html# TECH documents history page
│   └── static/
│       ├── css/style.css    # Full design system (brand colors, dark mode)
│       └── img/logo.png     # Digital Seeder logo (place here)
├── notebook/
│   └── train_model.py       # NLP training pipeline (advanced)
├── models/
│   ├── model.joblib         # Trained classifier (MultinomialNB / LogReg / SVC)
│   ├── vectorizer.joblib    # TF-IDF vectorizer (10k features, 1-2 ngrams)
│   └── label_encoder.joblib # sklearn LabelEncoder for category names
├── data/
│   ├── uploads/             # Uploaded PDFs (temporary)
│   ├── generated/           # Generated .ics / .txt files
│   └── app.db               # SQLite database (TECH logs)
├── dataset/
│   └── News_Category_Dataset_v3.json  # Kaggle dataset (not committed)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Prerequisites

- **Docker** & **docker-compose** (recommended)
- **Python 3.11+** for local execution without Docker

---

## Quick Start (Docker — recommended)

```bash
# 1. Clone the repository
git clone https://github.com/fatmabacha28/digital-seeder-test.git
cd digital-seeder-test

# 2. Build and start services
docker-compose up --build

# 3. Open the app
# Web app    → http://localhost:5000
# MailHog UI → http://localhost:8025
```

---

## Local Setup (without Docker)

```bash
# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Download NLTK data (first time only)
python -c "import nltk; nltk.download('stopwords'); nltk.download('wordnet')"

# Run the app
python app/run.py
```

---

## AI Model — Training

The project ships with a **pre-trained model** ready to use.

To re-train the model with the Kaggle News Category Dataset:

### 1. Download the dataset

Download `News_Category_Dataset_v3.json` from [Kaggle](https://www.kaggle.com/datasets/rmisra/news-category-dataset) and place it in:
```
dataset/News_Category_Dataset_v3.json
```

### 2. Run the training script

```bash
python notebook/train_model.py
```

The script will:
- Map and balance 7 classes (BUSINESS, ENTERTAINMENT, SPORTS, TECH, POLITICS, HEALTH, OTHER)
- Apply advanced preprocessing (lowercase, punctuation removal, stopwords, lemmatization)
- Train 3 models: `Logistic Regression`, `LinearSVC (Calibrated)`, `Random Forest`
- Select the best by Macro F1 score
- Apply a **confidence threshold of 55%** — predictions below this are classified as `OTHER`
- Display the full classification report and confusion matrix
- Save `model.joblib`, `vectorizer.joblib`, `label_encoder.joblib` to `models/`

---

## Technology Stack

| Layer | Technology |
|---|---|
| Web Framework | Flask 3.0 |
| NLP / ML | scikit-learn 1.8 (TF-IDF + MultinomialNB/LinearSVC) |
| Text Processing | NLTK (stopwords, lemmatization) |
| PDF Extraction | PyPDF2 |
| Database | SQLite (via Python `sqlite3`) |
| Email (dev) | MailHog (SMTP mock) |
| Calendar | icalendar |
| Frontend | Vanilla HTML/CSS/JS (Space Grotesk, Inter, FontAwesome) |
| Containerization | Docker + docker-compose |
| Python | 3.11 (Docker image: `python:3.11-slim`) |

---

## Environment Variables (docker-compose)

| Variable | Default | Description |
|---|---|---|
| `FLASK_APP` | `app.run` | Flask entry point |
| `FLASK_ENV` | `development` | Environment mode |
| `FLASK_DEBUG` | `1` | Enable auto-reload |
| `MAIL_SERVER` | `mailhog` | SMTP host |
| `MAIL_PORT` | `1025` | SMTP port |

---

## Endpoints

| Method | Route | Description |
|---|---|---|
| `GET` | `/` | Upload page |
| `POST` | `/` | Process uploaded PDF |
| `GET` | `/tech-history` | View TECH document history |
| `GET` | `/download/<filename>` | Download a generated file |

---

## Design System

The UI follows the **Digital Seeder** brand identity:
- **Primary font**: Space Grotesk
- **Background**: `#F5F4F1` (warm off-white)
- **Brand black**: `#0D0D0D`
- **Accent green**: `#16A34A` (growth/seeder metaphor)
- **Dark mode**: Full support, persisted via `localStorage`
