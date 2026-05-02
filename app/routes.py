import os
from flask import Blueprint, render_template, request, current_app, flash, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from app.services.pdf_service import extract_text_from_pdf, clean_text
from app.services.ml_service import predict_category
from app.services.action_service import process_action

bp = Blueprint('main', __name__)
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("Aucun fichier envoyé.", "error")
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash("Aucun fichier sélectionné.", "error")
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash("Format non autorisé. PDF uniquement.", "error")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            raw_text = extract_text_from_pdf(filepath)
            if not raw_text.strip():
                flash("Impossible d'extraire le texte de ce PDF.", "warning")
                return redirect(request.url)

            cleaned_text = clean_text(raw_text)

            # predict_category now returns a rich dict
            prediction = predict_category(cleaned_text)
            category   = prediction['category']
            confidence = prediction['confidence']
            keywords   = prediction['keywords']
            all_scores = prediction['all_scores']

            # Business action
            result_action = process_action(category, filepath, cleaned_text, current_app)

            # Handle file download actions
            action_text  = result_action
            download_url = None
            if isinstance(result_action, dict) and result_action.get('type') == 'download':
                action_text  = result_action.get('message', 'Fichier généré.')
                download_url = url_for('main.download_file', filename=result_action.get('filename'))

            return render_template('index.html', result={
                'filename':     filename,
                'category':     category,
                'confidence':   confidence,
                'keywords':     keywords,
                'all_scores':   all_scores,
                'text_preview': raw_text[:500] + ('...' if len(raw_text) > 500 else ''),
                'action':       action_text,
                'download_url': download_url,
            })

        except Exception as e:
            flash(f"Erreur lors du traitement : {str(e)}", "error")
            return redirect(request.url)

    return render_template('index.html')


@bp.route('/tech-history')
def tech_history():
    from app.database import get_tech_logs
    logs = get_tech_logs(current_app)
    return render_template('tech_history.html', logs=logs)


@bp.route('/download/<filename>')
def download_file(filename):
    safe = secure_filename(filename)
    path = os.path.join(current_app.config['GENERATED_FOLDER'], safe)
    if not os.path.exists(path):
        flash("Fichier introuvable.", "error")
        return redirect(url_for('main.index'))
    return send_file(path, as_attachment=True)
