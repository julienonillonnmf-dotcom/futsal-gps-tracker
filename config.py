# Configuration Futsal GPS Tracker
import os

# Server settings
DEBUG = True
PORT = 5000
HOST = '0.0.0.0'

# Upload settings
MAX_UPLOAD_SIZE = 500 * 1024 * 1024  # 500MB
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

# Model settings
YOLO_MODEL = 'yolov8n.pt'  # Can be 'yolov8s.pt', 'yolov8m.pt', 'yolov8x.pt'
CONFIDENCE_THRESHOLD = 0.5

# Field dimensions (meters)
FIELD_LENGTH = 40.0  # Longueur terrain handball/futsal
FIELD_WIDTH = 20.0   # Largeur terrain handball/futsal

# Processing settings
PROCESS_EVERY_N_FRAMES = 1  # Process every frame (set higher for faster processing)
MAX_TRACKING_DISTANCE = 2.0  # Maximum distance (meters) between frames for same player

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)
os.makedirs('models', exist_ok=True)
os.makedirs('static', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)
os.makedirs('templates', exist_ok=True)
