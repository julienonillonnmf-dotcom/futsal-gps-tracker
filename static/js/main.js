// Futsal GPS Tracker - JavaScript Principal

// Configuration API
const API_BASE_URL = window.location.origin + '/api';

// État global de l'application
let SESSION_ID = null;
let TRACKING_INTERVAL = null;

// Initialisation au chargement
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Futsal GPS Tracker initialized');
    initializeEventListeners();
    checkServerHealth();
});

// Vérifier la santé du serveur
async function checkServerHealth() {
    try {
        const response = await fetch('/health');
        if (response.ok) {
            console.log('✅ Server is running');
        }
    } catch (error) {
        console.error('❌ Server health check failed:', error);
        showNotification('Erreur de connexion au serveur', 'error');
    }
}

// Initialiser les écouteurs d'événements
function initializeEventListeners() {
    // Empêcher le comportement par défaut du formulaire
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', (e) => e.preventDefault());
    });
    
    // Raccourcis clavier
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey || e.metaKey) {
            switch(e.key) {
                case 's':
                    e.preventDefault();
                    exportData('csv');
                    break;
                case 'o':
                    e.preventDefault();
                    document.getElementById('fileInput').click();
                    break;
            }
        }
    });
}

// Upload de vidéo amélioré
async function uploadVideo(file) {
    const formData = new FormData();
    formData.append('video', file);
    
    // Afficher une barre de progression
    showLoadingOverlay('Upload en cours...');
    
    try {
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Upload failed');
        }
        
        const data = await response.json();
        SESSION_ID = data.session_id;
        
        hideLoadingOverlay();
        showNotification('Vidéo uploadée avec succès!', 'success');
        
        // Afficher les métadonnées
        if (data.metadata) {
            displayVideoMetadata(data.metadata);
        }
        
        // Activer le bouton de calibration
        document.getElementById('calibrateBtn').disabled = false;
        
        return data;
    } catch (error) {
        console.error('Upload error:', error);
        hideLoadingOverlay();
        showNotification('Erreur lors de l\'upload', 'error');
        throw error;
    }
}

// Afficher les métadonnées de la vidéo
function displayVideoMetadata(metadata) {
    const infoHTML = `
        <div style="background: rgba(102, 126, 234, 0.1); padding: 15px; border-radius: 10px; margin-top: 15px;">
            <h4>Informations vidéo:</h4>
            <p>📹 FPS: ${metadata.fps}</p>
            <p>🎬 Frames: ${metadata.frames}</p>
            <p>📐 Résolution: ${metadata.width}x${metadata.height}</p>
            <p>⏱️ Durée: ${formatDuration(metadata.duration)}</p>
        </div>
    `;
    
    // Ajouter les infos après la preview vidéo
    const videoPreview = document.querySelector('.video-preview');
    videoPreview.insertAdjacentHTML('afterend', infoHTML);
}

// Calibration du terrain
async function calibrate(points) {
    if (!SESSION_ID) {
        showNotification('Aucune session active', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/calibrate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: SESSION_ID,
                points: points
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showNotification('Calibration réussie!', 'success');
            document.getElementById('trackBtn').disabled = false;
        } else {
            throw new Error('Calibration failed');
        }
        
        return data;
    } catch (error) {
        console.error('Calibration error:', error);
        showNotification('Erreur lors de la calibration', 'error');
        throw error;
    }
}

// Lancer le tracking
async function startTracking() {
    if (!SESSION_ID) {
        showNotification('Aucune session active', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/track`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: SESSION_ID
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'started') {
            showNotification('Tracking démarré!', 'info');
            startProgressPolling();
        } else {
            throw new Error('Failed to start tracking');
        }
        
        return data;
    } catch (error) {
        console.error('Tracking error:', error);
        showNotification('Erreur lors du démarrage du tracking', 'error');
        throw error;
    }
}

// Polling pour le progrès
function startProgressPolling() {
    const progressBar = document.querySelector('.progress-bar');
    progressBar.style.display = 'block';
    
    TRACKING_INTERVAL = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/progress/${SESSION_ID}`);
            const data = await response.json();
            
            updateProgressBar(data.progress);
            
            if (data.status === 'completed') {
                clearInterval(TRACKING_INTERVAL);
                loadResults();
            } else if (data.status === 'error') {
                clearInterval(TRACKING_INTERVAL);
                showNotification('Erreur pendant le tracking', 'error');
            }
        } catch (error) {
            console.error('Progress error:', error);
        }
    }, 1000);
}

// Mise à jour de la barre de progression
function updateProgressBar(progress) {
    const progressFill = document.querySelector('.progress-fill');
    if (progressFill) {
        progressFill.style.width = `${progress}%`;
        progressFill.textContent = `${Math.round(progress)}%`;
    }
}

// Chargement des résultats
async function loadResults() {
    try {
        const response = await fetch(`${API_BASE_URL}/results/${SESSION_ID}`);
        const data = await response.json();
        
        displayResults(data);
        showNotification('Analyse terminée avec succès!', 'success');
        
        // Masquer la barre de progression
        document.querySelector('.progress-bar').style.display = 'none';
        
    } catch (error) {
        console.error('Results error:', error);
        showNotification('Erreur lors du chargement des résultats', 'error');
    }
}

// Afficher les résultats
function displayResults(data) {
    // Statistiques globales
    if (data.team_stats) {
        document.getElementById('totalPlayers').textContent = data.players ? data.players.length : '0';
        document.getElementById('totalDistance').textContent = Math.round(data.team_stats.total_distance) + ' m';
        document.getElementById('avgSpeed').textContent = data.team_stats.avg_speed.toFixed(1) + ' km/h';
        document.getElementById('duration').textContent = formatDuration(data.team_stats.duration);
    }
    
    // Liste des joueurs
    if (data.players && data.players.length > 0) {
        displayPlayersList(data.players);
    }
}

// Afficher la liste des joueurs
function displayPlayersList(players) {
    const playerList = document.getElementById('playerList');
    playerList.innerHTML = '';
    
    players.forEach((player, index) => {
        const playerColor = getPlayerColor(index);
        const playerItem = document.createElement('div');
        playerItem.className = 'player-item';
        playerItem.innerHTML = `
            <div style="display: flex; align-items: center;">
                <div style="width: 30px; height: 30px; background: ${playerColor}; border-radius: 50%; margin-right: 15px;"></div>
                <strong>${player.name}</strong>
                <span style="margin-left: 10px; color: #666;">(${player.role || 'Non défini'})</span>
            </div>
            <div>
                <span>📏 ${Math.round(player.distance)}m</span>
                <span style="margin-left: 15px;">⚡ ${player.avg_speed.toFixed(1)}km/h</span>
                <span style="margin-left: 15px;">🚀 Max: ${player.max_speed.toFixed(1)}km/h</span>
            </div>
        `;
        playerList.appendChild(playerItem);
    });
}

// Export des données
async function exportData(format) {
    if (!SESSION_ID) {
        showNotification('Aucune session active', 'error');
        return;
    }
    
    try {
        // Ouvrir directement le lien de téléchargement
        window.open(`${API_BASE_URL}/export/${SESSION_ID}/${format}`, '_blank');
        showNotification(`Export ${format.toUpperCase()} réussi!`, 'success');
    } catch (error) {
        console.error('Export error:', error);
        showNotification(`Erreur lors de l'export ${format}`, 'error');
    }
}

// Utilitaires

// Formater la durée en mm:ss
function formatDuration(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

// Obtenir une couleur pour un joueur
function getPlayerColor(index) {
    const colors = [
        '#667eea', '#764ba2', '#48bb78', '#f56565', '#ed8936',
        '#38b2ac', '#ecc94b', '#9f7aea', '#fc8181', '#4299e1'
    ];
    return colors[index % colors.length];
}

// Afficher une notification
function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    if (!notification) return;
    
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.style.display = 'block';
    
    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}

// Afficher un overlay de chargement
function showLoadingOverlay(message = 'Chargement...') {
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.id = 'loadingOverlay';
    overlay.innerHTML = `
        <div class="loading-content">
            <div class="loading-spinner" style="font-size: 3em; margin-bottom: 20px;">⚽</div>
            <p>${message}</p>
        </div>
    `;
    document.body.appendChild(overlay);
}

// Masquer l'overlay de chargement
function hideLoadingOverlay() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.remove();
    }
}

// Export des fonctions pour utilisation globale
window.uploadVideo = uploadVideo;
window.calibrate = calibrate;
window.startTracking = startTracking;
window.exportData = exportData;
window.showNotification = showNotification;
