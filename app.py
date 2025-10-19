from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import cv2
import numpy as np
from ultralytics import YOLO
import pandas as pd
import json
import os
from datetime import datetime
import base64
import tempfile
import threading
from werkzeug.utils import secure_filename
import io
from collections import defaultdict
import math

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

# Créer les dossiers nécessaires
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)
os.makedirs('static', exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('models', exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Variable globale pour stocker l'état du tracking
tracking_sessions = {}

class FutsalTrackerAPI:
    def __init__(self, session_id):
        self.session_id = session_id
        self.video_path = None
        self.calibration_points = None
        self.transform_matrix = None
        self.tracking_data = defaultdict(list)
        self.progress = 0
        self.status = 'idle'
        self.model = None
        
        # Dimensions du terrain
        self.TERRAIN_LONGUEUR = 40.0
        self.TERRAIN_LARGEUR = 20.0
        
    def load_video(self, video_path):
        """Charge la vidéo et extrait les métadonnées"""
        self.video_path = video_path
        cap = cv2.VideoCapture(video_path)
        
        metadata = {
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'frames': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'duration': int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS))
        }
        
        # Extraire une frame pour la calibration
        cap.set(cv2.CAP_PROP_POS_FRAMES, 30)  # Frame 30 pour avoir une bonne image
        ret, frame = cap.read()
        
        if ret:
            # Encoder la frame en base64 pour l'envoyer au frontend
            _, buffer = cv2.imencode('.jpg', frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            metadata['calibration_frame'] = frame_base64
        
        cap.release()
        return metadata
    
    def set_calibration(self, points):
        """Configure la calibration avec les points reçus du frontend"""
        self.calibration_points = np.array(points, dtype=np.float32)
        
        # Points du terrain en mètres
        terrain_corners = np.array([
            [0, 0],
            [self.TERRAIN_LONGUEUR, 0],
            [self.TERRAIN_LONGUEUR, self.TERRAIN_LARGEUR],
            [0, self.TERRAIN_LARGEUR]
        ], dtype=np.float32)
        
        # Calculer la matrice de transformation
        self.transform_matrix = cv2.getPerspectiveTransform(
            self.calibration_points, 
            terrain_corners * 10  # Multiplier pour avoir des pixels de travail
        )
        
        return True
    
    def pixel_to_meters(self, point):
        """Convertit un point en pixels vers des coordonnées en mètres"""
        if self.transform_matrix is None:
            return None
        
        point_array = np.array([[point]], dtype=np.float32)
        point_m = cv2.perspectiveTransform(point_array, self.transform_matrix)
        return point_m[0][0] / 10  # Diviser pour revenir en mètres
    
    def process_video(self):
        """Traite la vidéo et effectue le tracking"""
        self.status = 'processing'
        self.progress = 0
        
        # Charger le modèle YOLO
        if self.model is None:
            self.model = YOLO('yolov8n.pt')
        
        cap = cv2.VideoCapture(self.video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Tracking simple basé sur la proximité
        last_positions = {}
        next_id = 0
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Détection des joueurs avec YOLO
            results = self.model(frame, classes=[0])  # Classe 0 = personne
            
            current_positions = {}
            used_ids = set()
            
            for r in results:
                boxes = r.boxes
                if boxes is not None:
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        conf = box.conf[0].cpu().numpy()
                        
                        if conf > 0.5:
                            # Point au sol (milieu bas de la boîte)
                            pied_x = (x1 + x2) / 2
                            pied_y = y2
                            
                            # Convertir en coordonnées terrain
                            pied_m = self.pixel_to_meters([pied_x, pied_y])
                            
                            if pied_m is None:
                                continue
                            
                            # Association simple des IDs
                            min_dist = float('inf')
                            matched_id = None
                            
                            for id_joueur, last_pos in last_positions.items():
                                if id_joueur not in used_ids:
                                    dist = np.linalg.norm(np.array(pied_m) - np.array(last_pos))
                                    if dist < min_dist and dist < 2.0:
                                        min_dist = dist
                                        matched_id = id_joueur
                            
                            # Assigner ID
                            if matched_id is not None:
                                id_joueur = matched_id
                                used_ids.add(id_joueur)
                            else:
                                id_joueur = next_id
                                next_id += 1
                            
                            current_positions[id_joueur] = pied_m
                            
                            # Enregistrer la position
                            self.tracking_data[id_joueur].append({
                                'frame': frame_count,
                                'time': frame_count / fps,
                                'x': float(pied_m[0]),
                                'y': float(pied_m[1])
                            })
            
            last_positions = current_positions
            frame_count += 1
            
            # Mise à jour du progrès
            self.progress = (frame_count / total_frames) * 100
            
            # Limiter le traitement pour la démo (traiter 1 frame sur 10)
            if frame_count % 10 != 0:
                cap.set(cv2.CAP_PROP_POS_FRAMES, cap.get(cv2.CAP_PROP_POS_FRAMES) + 9)
        
        cap.release()
        self.status = 'completed'
        self.progress = 100
        
        # Calculer les statistiques
        return self.calculate_statistics(fps)
    
    def calculate_statistics(self, fps):
        """Calcule les statistiques pour chaque joueur"""
        stats = {
            'players': [],
            'team_stats': {
                'total_distance': 0,
                'avg_speed': 0,
                'duration': 0
            }
        }
        
        for player_id, positions in self.tracking_data.items():
            if len(positions) < 2:
                continue
            
            player_stats = {
                'id': player_id,
                'name': f'Joueur {player_id + 1}',
                'positions': positions,
                'distance': 0,
                'avg_speed': 0,
                'max_speed': 0,
                'zone_coverage': {'x_min': 40, 'x_max': 0, 'y_min': 20, 'y_max': 0}
            }
            
            # Calcul de la distance et des vitesses
            speeds = []
            for i in range(1, len(positions)):
                p1 = positions[i-1]
                p2 = positions[i]
                
                # Distance
                dist = math.sqrt((p2['x']-p1['x'])**2 + (p2['y']-p1['y'])**2)
                player_stats['distance'] += dist
                
                # Vitesse
                dt = p2['time'] - p1['time']
                if dt > 0:
                    speed = (dist / dt) * 3.6  # Conversion en km/h
                    speeds.append(speed)
                
                # Zone couverte
                player_stats['zone_coverage']['x_min'] = min(player_stats['zone_coverage']['x_min'], p2['x'])
                player_stats['zone_coverage']['x_max'] = max(player_stats['zone_coverage']['x_max'], p2['x'])
                player_stats['zone_coverage']['y_min'] = min(player_stats['zone_coverage']['y_min'], p2['y'])
                player_stats['zone_coverage']['y_max'] = max(player_stats['zone_coverage']['y_max'], p2['y'])
            
            if speeds:
                player_stats['avg_speed'] = sum(speeds) / len(speeds)
                player_stats['max_speed'] = max(speeds)
            
            # Déterminer le rôle probable
            avg_x = sum(p['x'] for p in positions) / len(positions)
            if avg_x < self.TERRAIN_LONGUEUR * 0.35:
                player_stats['role'] = 'Défenseur'
            elif avg_x > self.TERRAIN_LONGUEUR * 0.65:
                player_stats['role'] = 'Attaquant'
            else:
                player_stats['role'] = 'Milieu'
            
            stats['players'].append(player_stats)
            stats['team_stats']['total_distance'] += player_stats['distance']
        
        # Statistiques d'équipe
        if stats['players']:
            stats['team_stats']['avg_speed'] = sum(p['avg_speed'] for p in stats['players']) / len(stats['players'])
            stats['team_stats']['duration'] = max(
                max(p['time'] for p in positions) 
                for positions in self.tracking_data.values()
            )
        
        return stats

# Routes Flask

@app.route('/')
def index():
    """Page principale - sert l'interface HTML"""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_video():
    """Upload d'une vidéo"""
    if 'video' not in request.files:
        return jsonify({'error': 'Aucun fichier fourni'}), 400
    
    file = request.files['video']
    
    if file.filename == '':
        return jsonify({'error': 'Nom de fichier vide'}), 400
    
    if file and allowed_file(file.filename):
        # Générer un ID de session unique
        session_id = datetime.now().strftime('%Y%m%d_%H%M%S_') + secure_filename(file.filename)
        
        # Sauvegarder le fichier
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], session_id + '_' + filename)
        file.save(filepath)
        
        # Créer une session de tracking
        tracker = FutsalTrackerAPI(session_id)
        tracking_sessions[session_id] = tracker
        
        # Charger la vidéo et obtenir les métadonnées
        metadata = tracker.load_video(filepath)
        
        return jsonify({
            'session_id': session_id,
            'metadata': metadata,
            'status': 'success'
        })
    
    return jsonify({'error': 'Type de fichier non supporté'}), 400

@app.route('/api/calibrate', methods=['POST'])
def calibrate():
    """Configure la calibration du terrain"""
    data = request.json
    session_id = data.get('session_id')
    points = data.get('points')
    
    if not session_id or session_id not in tracking_sessions:
        return jsonify({'error': 'Session invalide'}), 400
    
    if not points or len(points) != 4:
        return jsonify({'error': '4 points de calibration requis'}), 400
    
    tracker = tracking_sessions[session_id]
    success = tracker.set_calibration(points)
    
    return jsonify({'status': 'success' if success else 'error'})

@app.route('/api/track', methods=['POST'])
def start_tracking():
    """Lance le tracking sur la vidéo"""
    data = request.json
    session_id = data.get('session_id')
    
    if not session_id or session_id not in tracking_sessions:
        return jsonify({'error': 'Session invalide'}), 400
    
    tracker = tracking_sessions[session_id]
    
    if tracker.transform_matrix is None:
        return jsonify({'error': 'Calibration requise'}), 400
    
    # Lancer le tracking dans un thread séparé
    thread = threading.Thread(target=tracker.process_video)
    thread.start()
    
    return jsonify({'status': 'started', 'session_id': session_id})

@app.route('/api/progress/<session_id>', methods=['GET'])
def get_progress(session_id):
    """Obtient le progrès du tracking"""
    if session_id not in tracking_sessions:
        return jsonify({'error': 'Session invalide'}), 400
    
    tracker = tracking_sessions[session_id]
    
    return jsonify({
        'progress': tracker.progress,
        'status': tracker.status
    })

@app.route('/api/results/<session_id>', methods=['GET'])
def get_results(session_id):
    """Obtient les résultats du tracking"""
    if session_id not in tracking_sessions:
        return jsonify({'error': 'Session invalide'}), 400
    
    tracker = tracking_sessions[session_id]
    
    if tracker.status != 'completed':
        return jsonify({'error': 'Tracking non terminé'}), 400
    
    # Calculer les statistiques
    stats = tracker.calculate_statistics(30)  # Assumant 30 FPS
    
    return jsonify(stats)

@app.route('/api/export/<session_id>/<format>', methods=['GET'])
def export_data(session_id, format):
    """Exporte les données dans différents formats"""
    if session_id not in tracking_sessions:
        return jsonify({'error': 'Session invalide'}), 400
    
    tracker = tracking_sessions[session_id]
    
    if tracker.status != 'completed':
        return jsonify({'error': 'Tracking non terminé'}), 400
    
    stats = tracker.calculate_statistics(30)
    
    if format == 'csv':
        # Créer un CSV
        df_data = []
        for player in stats['players']:
            for pos in player['positions']:
                df_data.append({
                    'player_id': player['id'],
                    'player_name': player['name'],
                    'time': pos['time'],
                    'x': pos['x'],
                    'y': pos['y']
                })
        
        df = pd.DataFrame(df_data)
        
        # Créer un buffer
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        
        return send_file(
            io.BytesIO(buffer.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'tracking_futsal_{session_id}.csv'
        )
    
    elif format == 'json':
        return jsonify(stats)
    
    else:
        return jsonify({'error': 'Format non supporté'}), 400

@app.route('/health')
def health():
    """Endpoint de santé pour vérifier que le serveur fonctionne"""
    return 'OK', 200

# Fonctions utilitaires

def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Lancement du serveur

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║         ⚽ FUTSAL GPS TRACKER - SERVEUR DÉMARRÉ          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    print("🚀 Serveur Futsal Tracker démarré!")
    print("📍 Accédez à l'application sur: http://localhost:5000")
    print("📹 Formats vidéo supportés: MP4, AVI, MOV, MKV")
    print("⚡ Appuyez sur Ctrl+C pour arrêter le serveur")
    
    app.run(debug=True, port=5000, threaded=True)
