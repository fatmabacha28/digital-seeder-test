import smtplib
from email.message import EmailMessage
from icalendar import Calendar, Event
import datetime
import os

def process_action(category, filepath, extracted_text, app):
    """
    Déclenche l'action métier en fonction de la catégorie.
    - BUSINESS: envoi d'email
    - ENTERTAINMENT: génération .ics
    - AUTRE: aucune action spécifique
    """
    if category == "BUSINESS":
        return send_email_via_mailhog(filepath, extracted_text, app)
    elif category == "ENTERTAINMENT":
        return generate_ics(filepath, app)
    elif category == "SPORTS":
        return generate_sports_report(filepath, extracted_text, app)
    elif category == "TECH":
        return log_tech_document(filepath, extracted_text, app)
    elif category == "POLITICS":
        return generate_politics_summary(filepath, extracted_text, app)
    elif category == "HEALTH":
        return generate_health_report(filepath, extracted_text, app)
    elif category == "OTHER":
        return "Catégorie non spécifique (OTHER). Aucune action déclenchée."
    else:
        return "Aucune action métier spécifique n'a été déclenchée pour cette catégorie."

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def send_email_via_mailhog(filepath, extracted_text, app):
    """Envoie un email via MailHog pour les documents BUSINESS."""
    msg = MIMEMultipart()
    msg['Subject'] = 'New Business Document'
    msg['From'] = app.config['MAIL_DEFAULT_SENDER']
    msg['To'] = 'business-team@example.com'
    
    # Corps de l'email
    content = f"Bonjour,\n\nVoici le contenu extrait du document métier reçu :\n\n---\n{extracted_text[:1000]}...\n---\n\nVeuillez trouver le document en pièce jointe."
    msg.attach(MIMEText(content, 'plain'))
    
    # Pièce jointe
    try:
        with open(filepath, 'rb') as f:
            pdf_attachment = MIMEApplication(f.read(), _subtype="pdf")
            pdf_attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(filepath))
            msg.attach(pdf_attachment)
    except Exception as e:
        print(f"Erreur lors de l'attachement du PDF : {e}")

    # Envoi via SMTP
    try:
        with smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT']) as server:
            server.send_message(msg)
        return "Email envoyé avec succès à l'équipe Business (vérifiez MailHog)."
    except Exception as e:
        print(f"Erreur d'envoi d'email : {e}")
        return f"Erreur lors de l'envoi de l'email : {e}"

def generate_ics(filepath, app):
    """Génère un fichier .ics pour les documents ENTERTAINMENT."""
    cal = Calendar()
    cal.add('prodid', '-//Digital Seeder//Event Calendar//EN')
    cal.add('version', '2.0')
    
    event = Event()
    event.add('summary', 'Nouvel Événement / Divertissement')
    event.add('dtstart', datetime.datetime.now())
    event.add('dtend', datetime.datetime.now() + datetime.timedelta(hours=2))
    event.add('description', f"Événement extrait du document : {os.path.basename(filepath)}")
    
    cal.add_component(event)
    
    ics_filename = f"event_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.ics"
    ics_filepath = os.path.join(app.config['GENERATED_FOLDER'], ics_filename)
    
    try:
        with open(ics_filepath, 'wb') as f:
            f.write(cal.to_ical())
        # Retourne un dictionnaire avec l'info du fichier
        return {
            'type': 'download',
            'filename': ics_filename,
            'message': 'Fichier d\'événement généré avec succès.'
        }
    except Exception as e:
        print(f"Erreur de génération .ics : {e}")
        return f"Erreur lors de la création de l'événement agenda : {e}"

def generate_sports_report(filepath, extracted_text, app):
    """Génère un rapport texte pour les documents SPORTS."""
    report_filename = f"sports_report_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
    report_filepath = os.path.join(app.config['GENERATED_FOLDER'], report_filename)
    
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = f"Sports document detected\n"
    content += f"Prediction category: SPORTS\n"
    content += f"Processing date: {current_date}\n"
    content += f"Summary:\n{extracted_text[:500]}\n"
    
    try:
        with open(report_filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Rapport sportif généré avec succès : {report_filename}"
    except Exception as e:
        print(f"Erreur de génération du rapport sportif : {e}")
        return f"Erreur lors de la création du rapport sportif : {e}"

def log_tech_document(filepath, extracted_text, app):
    """Sauvegarde un log dans SQLite pour les documents TECH."""
    from app.database import insert_tech_log
    filename = os.path.basename(filepath)
    text_length = len(extracted_text)
    
    try:
        insert_tech_log(filename, "TECH", text_length, app)
        return "Document Tech loggé avec succès dans la base de données."
    except Exception as e:
        print(f"Erreur de logging TECH : {e}")
        return f"Erreur lors de l'enregistrement dans la base de données : {e}"

def generate_politics_summary(filepath, extracted_text, app):
    """Génère un résumé texte pour les documents POLITICS."""
    report_filename = f"politics_summary_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
    report_filepath = os.path.join(app.config['GENERATED_FOLDER'], report_filename)
    
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = f"--- POLITICS DOCUMENT SUMMARY ---\n"
    content += f"Processed on: {current_date}\n"
    content += f"Original File: {os.path.basename(filepath)}\n\n"
    content += f"Excerpt:\n{extracted_text[:800]}\n"
    
    try:
        with open(report_filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Résumé politique généré avec succès : {report_filename}"
    except Exception as e:
        print(f"Erreur de génération du résumé politique : {e}")
        return f"Erreur lors de la création du résumé : {e}"

def generate_health_report(filepath, extracted_text, app):
    """Génère un dossier santé factice pour les documents HEALTH."""
    report_filename = f"health_report_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
    report_filepath = os.path.join(app.config['GENERATED_FOLDER'], report_filename)
    
    content = f"=== HEALTH DOCUMENT LOG ===\nDate: {datetime.datetime.now()}\nFile: {os.path.basename(filepath)}\nExtract:\n{extracted_text[:600]}\n"
    try:
        with open(report_filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Dossier santé généré : {report_filename}"
    except Exception as e:
        print(f"Erreur de génération dossier santé : {e}")
        return f"Erreur lors de la création du dossier santé : {e}"
