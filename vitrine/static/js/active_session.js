/**
 * Session Manager - Versão corrigida para CSRF
 */
class SessionManager {
    constructor() {
        this.sessionId = null;
        this.heartbeatInterval = null;
        this.heartbeatFrequency = 120000; // 2 minutos
        this.csrfToken = null;
        this.initialized = false;
    }

    getCSRFToken() {
        // Busca o token CSRF dos cookies de forma segura
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
        if (this.initialized) return;
        
        this.sessionId = localStorage.getItem('pwa_session_id');
        this.csrfToken = this.getCSRFToken();
        
        // Se não tem CSRF token, espera um pouco e tenta novamente
        if (!this.csrfToken) {
            setTimeout(() => {
                this.csrfToken = this.getCSRFToken();
                this.continueInitialization();
            }, 1000); // Espera 1 segundo pelo cookie
        } else {
            this.continueInitialization();
        }
        
        this.initialized = true;
    }

    async continueInitialization() {
        if (!this.sessionId) {
            await this.startNewSession();
        } else {
            // Verifica se a sessão ainda é válida
            await this.sendHeartbeat();
        }
        
        this.startPeriodicHeartbeat();
        
        // Evento de visibilidade com debounce
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && this.csrfToken) {
                this.sendHeartbeat();
            }
        });
    }

    async startNewSession() {
        if (!this.csrfToken) {
            console.log('CSRF token não disponível, tentando novamente...');
            setTimeout(() => this.startNewSession(), 2000);
            return;
        }

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
                console.log('Nova sessão iniciada:', this.sessionId);
            }
        } catch (error) {
            console.log('Erro ao iniciar sessão, usando fallback local');
            this.sessionId = 'local_' + Date.now();
            localStorage.setItem('pwa_session_id', this.sessionId);
        }
    }

    async sendHeartbeat() {
        if (!this.sessionId || !this.csrfToken) return;
        
        try {
            await fetch('/heartbeat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({ session_id: this.sessionId })
            });
        } catch (error) {
            // Silencia erros - normal para usuários anônimos
        }
    }

    startPeriodicHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
        }
        
        this.heartbeatInterval = setInterval(() => {
            if (this.csrfToken) {
                this.sendHeartbeat();
            }
        }, this.heartbeatFrequency);
    }
}

// Inicialização com delay para garantir CSRF cookie
document.addEventListener('DOMContentLoaded', function() {
    // Espera um pouco para garantir que os cookies estão disponíveis
    setTimeout(() => {
        new SessionManager().initialize();
    }, 500); // 500ms de delay
});