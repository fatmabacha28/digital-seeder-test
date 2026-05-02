import os
from flask import Blueprint, render_template, request, current_app, flash, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from app.services.pdf_service import extract_text_from_pdf, clean_text
from app.services.ml_service import predict_category
from app.services.action_service import process_action

bp = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Vérifier si un fichier a été soumis
        if 'file' not in request.files:
            flash("Aucun fichier n'a été envoyé", "error")
            return redirect(request.url)
            
        file = request.files['file']
        
        if file.filename == '':
            flash("Aucun fichier sélectionné", "error")
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                # 1. Extraction
                raw_text = extract_text_from_pdf(filepath)
                if not raw_text.strip():
                    flash("Impossible d'extraire le texte de ce PDF.", "warning")
                    return redirect(request.url)

                # 2. Nettoyage
                cleaned_text = clean_text(raw_text)

                # 3. Prédiction IA
                category = predict_category(cleaned_text)

                # 4. Déclenchement de l'action métier
                result_action = process_action(category, filepath, cleaned_text, current_app)

                # Gestion des retours d'actions (par exemple, téléchargement d'un fichier .ics)
                action_text = result_action
                download_url = None
                if isinstance(result_action, dict) and result_action.get('type') == 'download':
                    action_text = result_action.get('message', 'Fichier généré prêt au téléchargement.')
                    download_url = url_for('main.download_file', filename=result_action.get('filename'))

                flash(f"Document analysé avec succès. Catégorie : {category}.", "success")
                return render_template('index.html', result={
                    'filename': filename,
                    'category': category, 
                    'text_preview': raw_text[:500] + '...', 
                    'action': action_text,
                    'download_url': download_url
                })
                
            except Exception as e:
                flash(f"Une erreur est survenue lors du traitement: {str(e)}", "error")
                return redirect(request.url)
        else:
            flash("Format de fichier non autorisé. Uniquement des PDF.", "error")
            return redirect(request.url)

    return render_template('index.html')

@bp.route('/tech-history')
def tech_history():
    from app.database import get_tech_logs
    logs = get_tech_logs(current_app)
    return render_template('tech_history.html', logs=logs)

@bp.route('/download/<filename>')
def download_file(filename):
    return send_file(
        os.path.join(current_app.config['GENERATED_FOLDER'], filename),
        as_attachment=True
    )
