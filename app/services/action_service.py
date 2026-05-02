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
    else:
        return "Aucune action métier spécifique n'a été déclenchée pour cette catégorie."

def send_email_via_mailhog(filepath, extracted_text, app):
    """Envoie un email via MailHog pour les documents BUSINESS."""
    msg = EmailMessage()
    msg['Subject'] = 'New Business Document'
    msg['From'] = app.config['MAIL_DEFAULT_SENDER']
    msg['To'] = 'business-team@example.com'
    
    # Corps de l'email
    content = f"Bonjour,\n\nVoici le contenu extrait du document métier reçu :\n\n---\n{extracted_text[:1000]}...\n---\n\nVeuillez trouver le document en pièce jointe."
    msg.set_content(content)
    
    # Pièce jointe
    try:
        with open(filepath, 'rb') as f:
            pdf_data = f.read()
            msg.add_attachment(pdf_data, maintype='application', subtype='pdf', filename=os.path.basename(filepath))
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
    
    ics_filename = f"event_{datetime.datetime.now().strftime('%Y%md%H%M%S')}.ics"
    ics_filepath = os.path.join(app.config['UPLOAD_FOLDER'], ics_filename)
    
    try:
        with open(ics_filepath, 'wb') as f:
            f.write(cal.to_ical())
        # Retourne un dictionnaire pour indiquer à Flask de déclencher un téléchargement
        return {
            'type': 'download',
            'filepath': ics_filepath,
            'filename': ics_filename,
            'message': 'Fichier d\'événement généré avec succès.'
        }
    except Exception as e:
        print(f"Erreur de génération .ics : {e}")
        return f"Erreur lors de la création de l'événement agenda : {e}"
