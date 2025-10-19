#!/usr/bin/env python3
"""
🚀 FUTSAL GPS TRACKER - Installation et Configuration
Système de tracking automatique pour analyse de matchs de futsal
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

# Couleurs pour l'affichage
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    """Affiche l'en-tête de l'application"""
    print(f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║         ⚽ FUTSAL GPS TRACKER - INSTALLATION ⚽         ║
║                                                          ║
║     Analyse vidéo intelligente pour le futsal           ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
{Colors.END}
    """)

def check_python_version():
    """Vérifie la version de Python"""
    print(f"{Colors.BLUE}🔍 Vérification de Python...{Colors.END}")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"{Colors.RED}❌ Python 3.8 ou supérieur requis!{Colors.END}")
        print(f"Version actuelle: {sys.version}")
        return False
    
    print(f"{Colors.GREEN}✅ Python {version.major}.{version.minor}.{version.micro} détecté{Colors.END}")
    return True

def install_dependencies():
    """Installe les dépendances requises"""
    print(f"\n{Colors.BLUE}📦 Installation des dépendances...{Colors.END}")
    
    dependencies = [
        ('opencv-python', 'OpenCV pour traitement vidéo'),
        ('ultralytics', 'YOLO pour détection de joueurs'),
        ('flask', 'Serveur web'),
        ('flask-cors', 'Support CORS'),
        ('pandas', 'Traitement des données'),
        ('numpy', 'Calculs numériques'),
        ('matplotlib', 'Visualisation'),
        ('seaborn', 'Graphiques avancés'),
        ('werkzeug', 'Utilitaires web'),
        ('Pillow', 'Traitement d\'images')
    ]
    
    # Mettre à jour pip d'abord
    print(f"  📥 Mise à jour de pip...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass
    
    failed_packages = []
    
    for package, description in dependencies:
        print(f"  📥 Installation de {package} ({description})...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"  {Colors.GREEN}✅ {package} installé{Colors.END}")
        except subprocess.CalledProcessError:
            print(f"  {Colors.RED}❌ Erreur lors de l'installation de {package}{Colors.END}")
            failed_packages.append(package)
    
    if failed_packages:
        print(f"\n{Colors.YELLOW}⚠️ Packages non installés: {', '.join(failed_packages)}{Colors.END}")
        print(f"Essayez: pip install {' '.join(failed_packages)}")
        return False
    
    return True

def create_project_structure():
    """Crée la structure de dossiers du projet"""
    print(f"\n{Colors.BLUE}📁 Création de la structure du projet...{Colors.END}")
    
    folders = [
        'uploads',
        'results',
        'static',
        'static/css',
        'static/js',
        'templates',
        'models'
    ]
    
    for folder in folders:
        Path(folder).mkdir(exist_ok=True, parents=True)
        print(f"  {Colors.GREEN}✅ Dossier '{folder}' créé{Colors.END}")

def download_yolo_model():
    """Télécharge le modèle YOLO si nécessaire"""
    print(f"\n{Colors.BLUE}🤖 Configuration du modèle YOLO...{Colors.END}")
    
    try:
        from ultralytics import YOLO
        print(f"  📥 Téléchargement du modèle YOLO...")
        model = YOLO('yolov8n.pt')
        print(f"  {Colors.GREEN}✅ Modèle YOLO configuré{Colors.END}")
    except Exception as e:
        print(f"  {Colors.YELLOW}⚠️ Le modèle sera téléchargé au premier lancement{Colors.END}")

def create_launcher():
    """Crée un script de lancement facile"""
    print(f"\n{Colors.BLUE}🚀 Création du lanceur...{Colors.END}")
    
    if platform.system() == "Windows":
        # Script batch pour Windows
        launcher_content = """@echo off
echo.
echo ===================================
echo   FUTSAL GPS TRACKER - DEMARRAGE
echo ===================================
echo.
python app.py
pause
"""
        launcher_name = "lancer_futsal_tracker.bat"
    else:
        # Script bash pour Linux/Mac
        launcher_content = """#!/bin/bash
echo ""
echo "==================================="
echo "  FUTSAL GPS TRACKER - DEMARRAGE"
echo "==================================="
echo ""
python3 app.py
"""
        launcher_name = "lancer_futsal_tracker.sh"
    
    with open(launcher_name, 'w') as f:
        f.write(launcher_content)
    
    if platform.system() != "Windows":
        os.chmod(launcher_name, 0o755)
    
    print(f"  {Colors.GREEN}✅ Lanceur '{launcher_name}' créé{Colors.END}")
    return launcher_name

def test_installation():
    """Teste que tout est correctement installé"""
    print(f"\n{Colors.BLUE}🧪 Test de l'installation...{Colors.END}")
    
    tests = []
    
    # Test imports
    try:
        import cv2
        tests.append(("OpenCV", True))
    except ImportError:
        tests.append(("OpenCV", False))
    
    try:
        import flask
        tests.append(("Flask", True))
    except ImportError:
        tests.append(("Flask", False))
    
    try:
        from ultralytics import YOLO
        tests.append(("YOLO", True))
    except ImportError:
        tests.append(("YOLO", False))
    
    try:
        import pandas
        tests.append(("Pandas", True))
    except ImportError:
        tests.append(("Pandas", False))
    
    # Affichage des résultats
    all_pass = True
    for module, success in tests:
        if success:
            print(f"  {Colors.GREEN}✅ {module} : OK{Colors.END}")
        else:
            print(f"  {Colors.RED}❌ {module} : Erreur{Colors.END}")
            all_pass = False
    
    return all_pass

def print_instructions(launcher_name):
    """Affiche les instructions d'utilisation"""
    print(f"""
{Colors.GREEN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║         ✅ INSTALLATION TERMINÉE AVEC SUCCÈS! ✅        ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
{Colors.END}

{Colors.CYAN}{Colors.BOLD}📖 INSTRUCTIONS D'UTILISATION:{Colors.END}

1️⃣  {Colors.YELLOW}Lancer l'application:{Colors.END}
    • Double-cliquez sur '{launcher_name}'
    • Ou tapez: python app.py

2️⃣  {Colors.YELLOW}Ouvrir l'interface web:{Colors.END}
    • Ouvrez votre navigateur
    • Allez à: http://localhost:5000

3️⃣  {Colors.YELLOW}Utilisation:{Colors.END}
    • Chargez votre vidéo de futsal
    • Calibrez le terrain (4 coins)
    • Lancez l'analyse
    • Exportez les résultats!

{Colors.BLUE}{Colors.BOLD}💡 CONSEILS:{Colors.END}
• Utilisez une vidéo HD pour de meilleurs résultats
• Filmez depuis les tribunes ou en hauteur
• Assurez-vous que tout le terrain est visible
• L'éclairage doit être suffisant

{Colors.GREEN}Support: Pour toute question, consultez la documentation{Colors.END}
{Colors.CYAN}Bon tracking! ⚽{Colors.END}
    """)

def main():
    """Fonction principale d'installation"""
    print_header()
    
    # Vérifications
    if not check_python_version():
        input("\nAppuyez sur Entrée pour fermer...")
        sys.exit(1)
    
    # Installation
    steps = [
        ("Installation des dépendances", install_dependencies),
        ("Création de la structure", create_project_structure),
        ("Configuration YOLO", download_yolo_model)
    ]
    
    for step_name, step_function in steps:
        if not step_function():
            print(f"\n{Colors.RED}❌ Erreur lors de: {step_name}{Colors.END}")
            print("Veuillez résoudre le problème et relancer l'installation")
            input("\nAppuyez sur Entrée pour fermer...")
            sys.exit(1)
    
    # Créer le lanceur
    launcher = create_launcher()
    
    # Test final
    if test_installation():
        print_instructions(launcher)
    else:
        print(f"\n{Colors.YELLOW}⚠️ Certains modules ne sont pas correctement installés{Colors.END}")
        print("L'application pourrait ne pas fonctionner correctement")
        print_instructions(launcher)
    
    input(f"\n{Colors.CYAN}Appuyez sur Entrée pour fermer...{Colors.END}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Installation annulée par l'utilisateur{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Erreur inattendue: {e}{Colors.END}")
        input("\nAppuyez sur Entrée pour fermer...")
        sys.exit(1)
