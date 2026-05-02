import sys
import os

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

app = create_app()

if __name__ == '__main__':
    # Flask écoute sur toutes les interfaces (0.0.0.0) pour que ça marche dans Docker
    app.run(host='0.0.0.0', port=5000, debug=True)
