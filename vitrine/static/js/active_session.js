/**
 * Session Manager - Versão segura com proteções avançadas
 */
(function() {
    'use strict';
    
    class SessionManager {
        constructor() {
            this.sessionId = null;
            this.heartbeatInterval = null;
            this.heartbeatFrequency = 120000; // 2 minutos
            this.csrfToken = null;
            this.initialized = false;
            this.maxRetries = 3;
            this.retryCount = 0;
        }

        /**
         * Obtém CSRF token de forma segura
         */
        getCSRFToken() {
            try {
                // Método mais seguro usando meta tag (se disponível)
                const metaToken = document.querySelector('meta[name="csrf-token"]');
                if (metaToken && metaToken.getAttribute('content')) {
                    return metaToken.getAttribute('content');
                }
                
                // Fallback para cookie (menos seguro)
                const name = 'csrftoken';
                if (document.cookie && document.cookie !== '') {
                    const cookies = document.cookie.split(';');
                    for (let i = 0; i < cookies.length; i++) {
                        const cookie = cookies[i].trim();
                        if (cookie.substring(0, name.length + 1) === (name + '=')) {
                            return decodeURIComponent(cookie.substring(name.length + 1));
                        }
                    }
                }
                return null;
            } catch (error) {
                console.error('Erro ao obter CSRF token:', error);
                return null;
            }
        }

        /**
         * Valida session ID para prevenir injection
         */
        validateSessionId(sessionId) {
            if (!sessionId || typeof sessionId !== 'string') return false;
            
                
            const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
            const localPattern = /^local_\d+_[a-z0-9]+$/;
            
            return (uuidPattern.test(sessionId) || localPattern.test(sessionId)) && sessionId.length <= 100;
        }

        /**
         * Gera session ID local seguro
         */
            generateLocalSessionId() {
                return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                    const r = Math.random() * 16 | 0;
                    const v = c == 'x' ? r : (r & 0x3 | 0x8);
                    return v.toString(16);
                });
            }

        async initialize() {
            if (this.initialized) return;
            
            // Tenta obter session ID existente
            const storedSessionId = localStorage.getItem('pwa_session_id');
            if (this.validateSessionId(storedSessionId)) {
                this.sessionId = storedSessionId;
            }
            
            this.csrfToken = this.getCSRFToken();
            
            if (!this.csrfToken && this.retryCount < this.maxRetries) {
                this.retryCount++;
                setTimeout(() => this.initialize(), 1000 * this.retryCount);
                return;
            }
            
            await this.continueInitialization();
            this.initialized = true;
        }

        async continueInitialization() {
            if (!this.sessionId) {
                await this.startNewSession();
            } else {
                await this.sendHeartbeat();
            }
            
            this.startPeriodicHeartbeat();
            this.setupVisibilityHandler();
        }

        /**
         * Handler de visibilidade com debounce
         */
        setupVisibilityHandler() {
            let visibilityTimeout;
            
            const handleVisibilityChange = () => {
                if (!document.hidden && this.csrfToken) {
                    clearTimeout(visibilityTimeout);
                    visibilityTimeout = setTimeout(() => {
                        this.sendHeartbeat();
                    }, 1000); // Debounce de 1 segundo
                }
            };

            document.addEventListener('visibilitychange', handleVisibilityChange, { passive: true });
        }

        async startNewSession() {
            if (!this.csrfToken) {
                console.warn('CSRF token não disponível, usando sessão local');
                this.sessionId = this.generateLocalSessionId();
                localStorage.setItem('pwa_session_id', this.sessionId);
                return;
            }

            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 5000); // 5s timeout

                const response = await fetch('/start-session/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': this.csrfToken,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({}),
                    signal: controller.signal
                });
                
                clearTimeout(timeoutId);

                if (response.ok) {
                    const data = await response.json();
                    if (data.session_id && this.validateSessionId(data.session_id)) {
                        this.sessionId = data.session_id;
                        localStorage.setItem('pwa_session_id', this.sessionId);
                    } else {
                        throw new Error('Session ID inválido do servidor');
                    }
                } else {
                    throw new Error(`HTTP ${response.status}`);
                }
            } catch (error) {
                if (error.name === 'AbortError') {
                    console.warn('Timeout na criação de sessão');
                } else {
                    console.error('Erro ao iniciar sessão:', error);
                }
                
                // Fallback seguro
                this.sessionId = this.generateLocalSessionId();
                localStorage.setItem('pwa_session_id', this.sessionId);
            }
        }

        async sendHeartbeat() {
            if (!this.sessionId || !this.csrfToken || !this.validateSessionId(this.sessionId)) {
                return;
            }
            
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 3000); // 3s timeout

                await fetch('/heartbeat/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.csrfToken
                    },
                    body: JSON.stringify({ session_id: this.sessionId }),
                    signal: controller.signal
                });
                
                clearTimeout(timeoutId);
            } catch (error) {
                // Silencia erros esperados (offline, timeout, etc.)
                if (error.name !== 'AbortError') {
                    console.debug('Heartbeat falhou (esperado em alguns casos):', error);
                }
            }
        }

        startPeriodicHeartbeat() {
            if (this.heartbeatInterval) {
                clearInterval(this.heartbeatInterval);
            }
            
            this.heartbeatInterval = setInterval(() => {
                if (this.csrfToken && this.validateSessionId(this.sessionId)) {
                    this.sendHeartbeat();
                }
            }, this.heartbeatFrequency);
        }

        /**
         * Cleanup para evitar memory leaks
         */
        destroy() {
            if (this.heartbeatInterval) {
                clearInterval(this.heartbeatInterval);
                this.heartbeatInterval = null;
            }
            this.initialized = false;
        }
    }

    // Inicialização segura
    function initializeSessionManager() {
        try {
            const manager = new SessionManager();
            manager.initialize();
            
            // Cleanup em caso de unload
            window.addEventListener('beforeunload', () => {
                manager.destroy();
            }, { passive: true });
            
            return manager;
        } catch (error) {
            console.error('Falha crítica na inicialização do SessionManager:', error);
        }
    }

    // Inicialização com fallback
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeSessionManager);
    } else {
        setTimeout(initializeSessionManager, 100); // Pequeno delay
    }
})();