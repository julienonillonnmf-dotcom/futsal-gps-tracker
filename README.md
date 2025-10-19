⚽ Futsal GPS Tracker
Afficher l'image
Afficher l'image
Afficher l'image
Transformez vos vidéos de futsal en données GPS exploitables avec l'Intelligence Artificielle
<p align="center">
  <img src="https://via.placeholder.com/600x300/667eea/ffffff?text=Futsal+GPS+Tracker" alt="Futsal GPS Tracker">
</p>
🎯 Vue d'Ensemble
Futsal GPS Tracker est une application web qui utilise la vision par ordinateur et l'IA pour extraire automatiquement les positions GPS de vos joueurs à partir d'une simple vidéo de match. Plus besoin de trackers GPS coûteux !
✨ Fonctionnalités Principales

🤖 Détection automatique des joueurs avec YOLO v8
📍 Tracking en temps réel des positions sur le terrain
📊 Statistiques complètes : distance, vitesse, zones de jeu
🎨 Interface web moderne et intuitive
📈 Export flexible en CSV, JSON
🚀 Performance optimisée pour vidéos HD

🚀 Installation Rapide
Méthode 1 : Installation Automatique (Recommandée)
bash# 1. Cloner le repository
git clone https://github.com/votre-username/futsal-gps-tracker.git
cd futsal-gps-tracker

# 2. Lancer l'installateur
python installer.py

# 3. Démarrer l'application
python app.py
Méthode 2 : Installation Manuelle
bash# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python app.py
Méthode 3 : Docker
bash# Construire l'image
docker build -t futsal-tracker .

# Lancer le container
docker run -p 5000:5000 futsal-tracker
💻 Utilisation

Ouvrez votre navigateur : http://localhost:5000
Chargez votre vidéo : Drag & drop ou cliquez pour sélectionner
Calibrez le terrain : Cliquez sur les 4 coins dans l'ordre
Lancez l'analyse : Le tracking démarre automatiquement
Exportez les résultats : CSV ou JSON selon vos besoins

📊 Données Exportées
Format CSV
csvplayer_id,player_name,time,x,y
0,Joueur 1,0.0,20.5,10.2
0,Joueur 1,0.033,20.6,10.1
Format JSON
json{
  "players": [
    {
      "id": 0,
      "name": "Joueur 1",
      "distance": 4523.2,
      "avg_speed": 7.8,
      "positions": [...]
    }
  ]
}
📋 Prérequis
ComposantMinimumRecommandéPython3.83.10+RAM4 GB8 GB+Espace disque2 GB5 GB+GPUNon requisNVIDIA avec CUDA
🎥 Configuration Vidéo Optimale

Résolution : 1080p minimum
FPS : 30+ recommandé
Position : Vue depuis les tribunes/hauteur
Angle : Terrain complet visible
Éclairage : Uniforme et suffisant

🔧 Configuration Avancée
Changer le modèle YOLO
Dans config.py :
pythonYOLO_MODEL = 'yolov8x.pt'  # Pour plus de précision
Ajuster la sensibilité
pythonCONFIDENCE_THRESHOLD = 0.7  # Augmenter pour moins de faux positifs
📁 Structure du Projet
futsal-gps-tracker/
├── app.py              # Serveur Flask principal
├── config.py           # Configuration
├── installer.py        # Script d'installation
├── requirements.txt    # Dépendances Python
├── templates/
│   └── index.html     # Interface web
├── static/
│   ├── css/          # Styles
│   └── js/           # JavaScript
├── uploads/          # Vidéos uploadées
├── results/          # Résultats
└── models/           # Modèles YOLO
🤝 Contribution
Les contributions sont les bienvenues !

Fork le projet
Créez votre branche (git checkout -b feature/AmazingFeature)
Committez (git commit -m 'Add AmazingFeature')
Push (git push origin feature/AmazingFeature)
Ouvrez une Pull Request

📄 License
Distribué sous licence MIT. Voir LICENSE pour plus d'informations.
🆘 Support & Contact

📧 Email : votre-email@example.com
🐛 Issues : GitHub Issues
💬 Discussions : GitHub Discussions

🙏 Remerciements

Ultralytics pour YOLO
OpenCV pour le traitement vidéo
Flask pour le framework web


<p align="center">
  Développé avec ❤️ pour la communauté Futsal
  <br>
  ⭐ Si ce projet vous aide, n'hésitez pas à lui donner une étoile !
</p>
