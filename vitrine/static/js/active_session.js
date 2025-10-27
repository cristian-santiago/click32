/**
 * Session Manager - Versão otimizada
 */
class SessionManager {
    constructor() {
        this.sessionId = null;
        this.heartbeatInterval = null;
        this.heartbeatFrequency = 120000; // 2 minutos
        this.csrfToken = this.getCSRFToken();
        this.lastHeartbeat = 0;
        this.minHeartbeatInterval = 30000; // Mínimo 30 segundos entre heartbeats
    }

    getCSRFToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    async initialize() {
        this.sessionId = localStorage.getItem('pwa_session_id');
        
        if (!this.sessionId) {
            await this.startNewSession();
        }
        
        this.startPeriodicHeartbeat();
        
        // Debounce no evento de visibilidade
        document.addEventListener('visibilitychange', this.debouncedHeartbeat.bind(this));
    }

    // Debounce para evitar múltiplos heartbeats rápidos
    debouncedHeartbeat() {
        const now = Date.now();
        if (now - this.lastHeartbeat > this.minHeartbeatInterval) {
            this.sendHeartbeat();
        }
    }

    async startNewSession() {
        try {
            const response = await fetch('/start-session/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.csrfToken,
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.sessionId = data.session_id;
                localStorage.setItem('pwa_session_id', this.sessionId);
            }
        } catch (error) {
            this.sessionId = 'local_' + Date.now();
            localStorage.setItem('pwa_session_id', this.sessionId);
        }
    }

    async sendHeartbeat() {
        if (!this.sessionId) return;
        
        const now = Date.now();
        if (now - this.lastHeartbeat < this.minHeartbeatInterval) {
            return; // Ignora se foi muito recente
        }
        
        try {
            const response = await fetch('/heartbeat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({ session_id: this.sessionId })
            });
            
            if (response.ok) {
                this.lastHeartbeat = now;
                const data = await response.json();
                if (data.session_created) {
                    this.sessionId = data.session_id;
                    localStorage.setItem('pwa_session_id', this.sessionId);
                }
            }
        } catch (error) {
            // Silencia erros
        }
    }

    startPeriodicHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
        }
        
        this.heartbeatInterval = setInterval(() => {
            this.sendHeartbeat();
        }, this.heartbeatFrequency);
    }
}

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    new SessionManager().initialize();
});