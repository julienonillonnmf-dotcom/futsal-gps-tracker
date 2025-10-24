"""
Futsal GPS Tracker - Version Render
Application optimisée pour déploiement sur Render.com
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import json
import tempfile
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
import threading
import time

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration pour Render
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_UPLOAD_SIZE', 100)) * 1024 * 1024  # MB
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', '/tmp/uploads')
app.config['RESULTS_FOLDER'] = os.environ.get('RESULTS_FOLDER', '/tmp/results')

# Extensions autorisées
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

# Créer les dossiers
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

# Import conditionnel pour éviter les erreurs sur Render
try:
    import cv2
    from ultralytics import YOLO
    import numpy as np
    import pandas as pd
    TRACKING_AVAILABLE = True
    logger.info("✅ Modules de tracking chargés")
except ImportError as e:
    TRACKING_AVAILABLE = False
    logger.warning(f"⚠️ Modules de tracking non disponibles: {e}")

# Sessions de tracking (stockage en mémoire)
tracking_sessions = {}

class FutsalTrackerSimplified:
    """Version simplifiée du tracker pour Render"""
    
    def __init__(self, session_id):
        self.session_id = session_id
        self.video_path = None
        self.status = 'idle'
        self.progress = 0
        self.results = None
        
    def load_video(self, video_path):
        """Charge la vidéo et retourne les métadonnées"""
        self.video_path = video_path
        
        if not TRACKING_AVAILABLE:
            # Mode simulation si OpenCV n'est pas disponible
            return {
                'fps': 30,
                'frames': 1000,
                'width': 1920,
                'height': 1080,
                'duration': 33
            }
        
        try:
            cap = cv2.VideoCapture(video_path)
            metadata = {
                'fps': cap.get(cv2.CAP_PROP_FPS),
                'frames': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'duration': int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS))
            }
            cap.release()
            return metadata
        except Exception as e:
            logger.error(f"Erreur chargement vidéo: {e}")
            return None
    
    def process_video(self):
        """Traite la vidéo (version simplifiée pour Render)"""
        self.status = 'processing'
        
        # Simulation du traitement pour la démo
        for i in range(0, 101, 10):
            self.progress = i
            time.sleep(1)  # Simule le traitement
        
        self.status = 'completed'
        self.progress = 100
        
        # Résultats simulés
        self.results = {
            'players': [
                {
                    'id': i,
                    'name': f'Joueur {i+1}',
                    'distance': 3500 + i * 500,
                    'avg_speed': 6.5 + i * 0.3,
                    'max_speed': 20 + i * 0.5,
                    'role': ['Défenseur', 'Milieu', 'Attaquant'][i % 3]
                }
                for i in range(10)
            ],
            'team_stats': {
                'total_distance': 45000,
                'avg_speed': 7.2,
                'duration': 2700
            }
        }

# Routes

@app.route('/')
def index():
    """Page principale"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check pour Render"""
    return jsonify({
        'status': 'healthy',
        'tracking_available': TRACKING_AVAILABLE,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/upload', methods=['POST'])
def upload_video():
    """Upload de vidéo avec gestion des limitations Render"""
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['video']
        
        if file.filename == '':
            return jsonify({'error': 'Nom de fichier vide'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Format non supporté'}), 400
        
        # Générer un ID de session
        session_id = datetime.now().strftime('%Y%m%d_%H%M%S_') + secure_filename(file.filename)
        
        # Sur Render, utiliser /tmp pour stockage temporaire
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Sauvegarder le fichier
        file.save(filepath)
        
        # Créer une session de tracking
        tracker = FutsalTrackerSimplified(session_id)
        tracking_sessions[session_id] = tracker
        
        # Charger les métadonnées
        metadata = tracker.load_video(filepath)
        
        # Nettoyer les vieilles sessions (garder seulement les 10 dernières)
        if len(tracking_sessions) > 10:
            oldest_sessions = sorted(tracking_sessions.keys())[:len(tracking_sessions)-10]
            for old_session in oldest_sessions:
                del tracking_sessions[old_session]
        
        return jsonify({
            'session_id': session_id,
            'metadata': metadata,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Erreur upload: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/calibrate', methods=['POST'])
def calibrate():
    """Calibration (simulée pour Render)"""
    data = request.json
    session_id = data.get('session_id')
    
    if not session_id or session_id not in tracking_sessions:
        return jsonify({'error': 'Session invalide'}), 400
    
    # Sur Render, on simule la calibration
    return jsonify({'status': 'success'})

@app.route('/api/track', methods=['POST'])
def start_tracking():
    """Lance le tracking (simplifié pour Render)"""
    data = request.json
    session_id = data.get('session_id')
    
    if not session_id or session_id not in tracking_sessions:
        return jsonify({'error': 'Session invalide'}), 400
    
    tracker = tracking_sessions[session_id]
    
    # Lancer le tracking dans un thread
    thread = threading.Thread(target=tracker.process_video)
    thread.start()
    
    return jsonify({'status': 'started', 'session_id': session_id})

@app.route('/api/progress/<session_id>')
def get_progress(session_id):
    """Obtient le progrès du tracking"""
    if session_id not in tracking_sessions:
        return jsonify({'error': 'Session invalide'}), 400
    
    tracker = tracking_sessions[session_id]
    
    return jsonify({
        'progress': tracker.progress,
        'status': tracker.status
    })

@app.route('/api/results/<session_id>')
def get_results(session_id):
    """Obtient les résultats"""
    if session_id not in tracking_sessions:
        return jsonify({'error': 'Session invalide'}), 400
    
    tracker = tracking_sessions[session_id]
    
    if tracker.status != 'completed':
        return jsonify({'error': 'Tracking non terminé'}), 400
    
    return jsonify(tracker.results)

@app.route('/api/export/<session_id>/<format>')
def export_data(session_id, format):
    """Export des données"""
    if session_id not in tracking_sessions:
        return jsonify({'error': 'Session invalide'}), 400
    
    tracker = tracking_sessions[session_id]
    
    if not tracker.results:
        return jsonify({'error': 'Aucun résultat disponible'}), 400
    
    if format == 'json':
        return jsonify(tracker.results)
    
    elif format == 'csv':
        # Créer un CSV simple
        import io
        output = io.StringIO()
        output.write("player_id,player_name,distance,avg_speed,max_speed,role\n")
        
        for player in tracker.results['players']:
            output.write(f"{player['id']},{player['name']},{player['distance']},{player['avg_speed']},{player['max_speed']},{player['role']}\n")
        
        output.seek(0)
        
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'futsal_tracking_{session_id}.csv'
        )
    
    return jsonify({'error': 'Format non supporté'}), 400

# Fonction utilitaire
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Nettoyage automatique des fichiers temporaires
def cleanup_old_files():
    """Nettoie les vieux fichiers pour économiser l'espace sur Render"""
    try:
        import shutil
        # Nettoyer les fichiers de plus d'une heure
        cutoff_time = time.time() - 3600  # 1 heure
        
        for folder in [app.config['UPLOAD_FOLDER'], app.config['RESULTS_FOLDER']]:
            if os.path.exists(folder):
                for filename in os.listdir(folder):
                    filepath = os.path.join(folder, filename)
                    if os.path.getmtime(filepath) < cutoff_time:
                        os.remove(filepath)
                        logger.info(f"Fichier supprimé: {filepath}")
    except Exception as e:
        logger.error(f"Erreur nettoyage: {e}")

# Lancer le nettoyage toutes les heures
def start_cleanup_scheduler():
    def run_cleanup():
        while True:
            time.sleep(3600)  # 1 heure
            cleanup_old_files()
    
    cleanup_thread = threading.Thread(target=run_cleanup, daemon=True)
    cleanup_thread.start()

# Configuration pour production
if __name__ == '__main__':
    # Démarrer le scheduler de nettoyage
    start_cleanup_scheduler()
    
    # Port depuis variable d'environnement (requis par Render)
    port = int(os.environ.get('PORT', 5000))
    
    # Mode debug seulement en développement
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    logger.info(f"🚀 Démarrage du serveur sur le port {port}")
    logger.info(f"📍 Mode: {'Development' if debug_mode else 'Production'}")
    logger.info(f"🎯 Tracking disponible: {TRACKING_AVAILABLE}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode
    )
