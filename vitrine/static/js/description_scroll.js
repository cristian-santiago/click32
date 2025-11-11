/**
 * Description Scroll Manager - Versão segura com tratamento de erros
 */
(function() {
    'use strict';
    
    class DescriptionScrollManager {
        constructor() {
            this.descriptionP = null;
            this.storeName = null;
            this.storeInfo = null;
            this.resizeTimeout = null;
            this.scrollTimeout = null;
            this.initialized = false;
            
            // Configurações
            this.config = {
                resizeDebounce: 100,
                scrollDebounce: 50,
                overlapTolerance: 10,
                scrollTolerance: 0.5
            };
        }

        /**
         * Valida e obtém elementos DOM de forma segura
         */
        getDOMElements() {
            try {
                this.descriptionP = document.querySelector('.description p');
                this.storeName = document.querySelector('.store-name');
                this.storeInfo = document.querySelector('.store-info');
                
                return this.descriptionP && this.storeName && this.storeInfo;
            } catch (error) {
                console.error('Erro ao obter elementos DOM:', error);
                return false;
            }
        }

        /**
         * Ajusta padding da descrição para evitar sobreposição
         */
        adjustDescriptionPadding() {
            try {
                if (!this.descriptionP || !this.storeInfo) return;

                const descriptionRect = this.descriptionP.getBoundingClientRect();
                const storeInfoRect = this.storeInfo.getBoundingClientRect();
                
                const descriptionBottom = descriptionRect.bottom;
                const storeInfoTop = storeInfoRect.top;
                const overlap = descriptionBottom - storeInfoTop;

                if (overlap > 0) {
                    this.descriptionP.style.paddingBottom = `${overlap + this.config.overlapTolerance}px`;
                } else {
                    this.descriptionP.style.paddingBottom = '';
                }
            } catch (error) {
                console.error('Erro ao ajustar padding:', error);
            }
        }

        /**
         * Atualiza sombras no scroll com debounce
         */
        updateScrollShadows() {
            try {
                if (!this.descriptionP || !this.storeName || !this.storeInfo) return;

                const scrollTop = this.descriptionP.scrollTop;
                const scrollHeight = this.descriptionP.scrollHeight;
                const clientHeight = this.descriptionP.clientHeight;

                // Remove classes de sombra
                this.storeName.classList.remove('scroll-shadow-top');
                this.storeInfo.classList.remove('scroll-shadow-bottom');

                // Adiciona sombra superior se não estiver no topo
                if (scrollTop > this.config.scrollTolerance) {
                    this.storeName.classList.add('scroll-shadow-top');
                }

                // Adiciona sombra inferior se não estiver no final
                if (scrollTop + clientHeight < scrollHeight - 1) {
                    this.storeInfo.classList.add('scroll-shadow-bottom');
                }
            } catch (error) {
                console.error('Erro ao atualizar sombras:', error);
            }
        }

        /**
         * Handler de resize com debounce
         */
        handleResize() {
            clearTimeout(this.resizeTimeout);
            this.resizeTimeout = setTimeout(() => {
                this.adjustDescriptionPadding();
            }, this.config.resizeDebounce);
        }

        /**
         * Handler de scroll com debounce
         */
        handleScroll() {
            clearTimeout(this.scrollTimeout);
            this.scrollTimeout = setTimeout(() => {
                this.updateScrollShadows();
            }, this.config.scrollDebounce);
        }

        /**
         * Configura event listeners de forma segura
         */
        setupEventListeners() {
            try {
                // Event listeners para ajuste de padding
                window.addEventListener('load', () => this.adjustDescriptionPadding(), { passive: true });
                window.addEventListener('resize', () => this.handleResize(), { passive: true });
                window.addEventListener('scroll', () => this.adjustDescriptionPadding(), { passive: true });

                // Event listener para sombras no scroll da descrição
                if (this.descriptionP) {
                    this.descriptionP.addEventListener('scroll', () => this.handleScroll(), { passive: true });
                }
            } catch (error) {
                console.error('Erro ao configurar event listeners:', error);
            }
        }

        /**
         * Inicialização principal
         */
        initialize() {
            if (this.initialized) return;

            try {
                if (!this.getDOMElements()) {
                    console.warn('Elementos de description scroll não encontrados');
                    return;
                }

                this.setupEventListeners();
                
                // Inicializa estados
                this.adjustDescriptionPadding();
                this.updateScrollShadows();
                
                this.initialized = true;
                
                console.log('Description scroll manager inicializado com sucesso');
            } catch (error) {
                console.error('Falha na inicialização do description scroll manager:', error);
            }
        }

        /**
         * Cleanup para evitar memory leaks
         */
        destroy() {
            try {
                // Limpa timeouts
                clearTimeout(this.resizeTimeout);
                clearTimeout(this.scrollTimeout);
                
                // Remove event listeners
                window.removeEventListener('load', this.adjustDescriptionPadding);
                window.removeEventListener('resize', this.handleResize);
                window.removeEventListener('scroll', this.adjustDescriptionPadding);
                
                if (this.descriptionP) {
                    this.descriptionP.removeEventListener('scroll', this.handleScroll);
                }
                
                // Reseta elementos
                if (this.descriptionP) {
                    this.descriptionP.style.paddingBottom = '';
                }
                
                if (this.storeName) {
                    this.storeName.classList.remove('scroll-shadow-top');
                }
                
                if (this.storeInfo) {
                    this.storeInfo.classList.remove('scroll-shadow-bottom');
                }
                
                this.initialized = false;
                
            } catch (error) {
                console.error('Erro no cleanup do description scroll manager:', error);
            }
        }
    }

    // Gerenciador de inicialização segura
    function initializeDescriptionScrollSafe() {
        let scrollManager = null;
        
        try {
            scrollManager = new DescriptionScrollManager();
            
            // Inicialização com verificação de elementos
            const initWhenReady = () => {
                if (document.querySelector('.description p')) {
                    scrollManager.initialize();
                } else {
                    // Tenta novamente se elementos ainda não carregaram
                    setTimeout(initWhenReady, 100);
                }
            };
            
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', initWhenReady);
            } else {
                initWhenReady();
            }
            
            // Cleanup em caso de unload
            window.addEventListener('beforeunload', () => {
                scrollManager?.destroy();
            }, { passive: true });
            
        } catch (error) {
            console.error('Falha crítica na inicialização do description scroll:', error);
        }
        
        return scrollManager;
    }

    // Inicialização
    initializeDescriptionScrollSafe();
})();