/**
 * Carousel Manager - Versão segura com tratamento de erros e cleanup
 */
(function() {
    'use strict';
    
    class CarouselManager {
        constructor() {
            this.carouselContainer = null;
            this.carouselItems = [];
            this.dotsContainer = null;
            this.scrollHandler = null;
            this.initialized = false;
        }

        /**
         * Valida e obtém elementos DOM de forma segura
         */
        getDOMElements() {
            try {
                this.carouselContainer = document.querySelector('.carousel-container');
                this.carouselItems = document.querySelectorAll('.carousel-container .carousel-item');
                this.dotsContainer = document.querySelector('.carousel-dots');
                
                return this.carouselContainer && 
                       this.carouselItems.length > 0 && 
                       this.dotsContainer;
            } catch (error) {
                console.error('Erro ao obter elementos DOM:', error);
                return false;
            }
        }

        /**
         * Cria dots de navegação com event listeners seguros
         */
        createDots() {
            try {
                // Limpa dots existentes para evitar duplicação
                this.dotsContainer.innerHTML = '';
                
                this.carouselItems.forEach((item, index) => {
                    const dot = document.createElement('div');
                    dot.className = 'carousel-dot';
                    dot.setAttribute('role', 'button');
                    dot.setAttribute('aria-label', `Ir para slide ${index + 1}`);
                    dot.setAttribute('tabindex', '0');
                    
                    if (index === 0) {
                        dot.classList.add('active');
                        dot.setAttribute('aria-current', 'true');
                    }

                    // Event listener com tratamento de erro
                    const handleDotClick = () => {
                        this.scrollToItem(index);
                    };

                    dot.addEventListener('click', handleDotClick);
                    
                    // Suporte a teclado (acessibilidade)
                    dot.addEventListener('keydown', (e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault();
                            this.scrollToItem(index);
                        }
                    });

                    this.dotsContainer.appendChild(dot);
                });
            } catch (error) {
                console.error('Erro ao criar dots de navegação:', error);
            }
        }

        /**
         * Scroll seguro para item específico
                */
        scrollToItem(index) {
            const itemWidth = this.carouselItems[0]?.offsetWidth + 10;
            this.carouselContainer.scrollTo({
                left: index * itemWidth,
                behavior: 'smooth'
            });
        }

        /**
         * Atualiza dot ativo com validação
         */
        updateActiveDot(activeIndex) {
            try {
                const dots = this.dotsContainer.querySelectorAll('.carousel-dot');
                
                dots.forEach((dot, index) => {
                    const isActive = index === activeIndex;
                    dot.classList.toggle('active', isActive);
                    
                    // Atualiza atributos de acessibilidade
                    if (isActive) {
                        dot.setAttribute('aria-current', 'true');
                    } else {
                        dot.removeAttribute('aria-current');
                    }
                });
            } catch (error) {
                console.error('Erro ao atualizar dots ativos:', error);
            }
        }

        /**
         * Handler de scroll com debounce para performance
         */

setupScrollHandler() {
    let isScrolling = false;
    let targetIndex = 0;
    let startX = 0;
    let startScrollLeft = 0;
    let isDragging = false;
    
    const itemWidth = this.carouselItems[0]?.offsetWidth + 20;
    
    // Eventos de toque/mouse para capturar o swipe
    this.carouselContainer.addEventListener('touchstart', (e) => {
        if (isScrolling) return;
        startX = e.touches[0].clientX;
        startScrollLeft = this.carouselContainer.scrollLeft;
        isDragging = true;
    }, { passive: true });
    
    this.carouselContainer.addEventListener('touchmove', (e) => {
        if (!isDragging || isScrolling) return;
        e.preventDefault(); // Previne o scroll padrão
        
        const currentX = e.touches[0].clientX;
        const diff = startX - currentX;
        
        // Aplica o deslocamento manualmente (sem scroll livre)
        this.carouselContainer.scrollLeft = startScrollLeft + diff;
    }, { passive: false });
    
    this.carouselContainer.addEventListener('touchend', (e) => {
        if (!isDragging || isScrolling) return;
        
        const currentX = e.changedTouches[0].clientX;
        const diff = startX - currentX;
        const threshold = 50; // Distância mínima para considerar swipe
        
        isDragging = false;
        
        // Determina direção baseado na distância percorrida
        if (Math.abs(diff) > threshold) {
            if (diff > 0 && targetIndex < this.carouselItems.length - 1) {
                // Swipe esquerda -> próximo slide
                targetIndex++;
            } else if (diff < 0 && targetIndex > 0) {
                // Swipe direita -> slide anterior
                targetIndex--;
            }
        }
        
        // Sempre faz scroll para o slide atual (targetIndex)
        isScrolling = true;
        this.scrollToItem(targetIndex);
        
        setTimeout(() => {
            isScrolling = false;
        }, 300);
        
        this.updateActiveDot(targetIndex);
    }, { passive: true });
    
    // Previne o scroll padrão do mouse também
    this.carouselContainer.addEventListener('mousedown', (e) => {
        if (isScrolling) return;
        e.preventDefault();
        startX = e.clientX;
        startScrollLeft = this.carouselContainer.scrollLeft;
        isDragging = true;
    });
    
    this.carouselContainer.addEventListener('mousemove', (e) => {
        if (!isDragging || isScrolling) return;
        e.preventDefault();
        
        const currentX = e.clientX;
        const diff = startX - currentX;
        
        this.carouselContainer.scrollLeft = startScrollLeft + diff;
    });
    
    this.carouselContainer.addEventListener('mouseup', (e) => {
        if (!isDragging || isScrolling) return;
        
        const currentX = e.clientX;
        const diff = startX - currentX;
        const threshold = 50;
        
        isDragging = false;
        
        if (Math.abs(diff) > threshold) {
            if (diff > 0 && targetIndex < this.carouselItems.length - 1) {
                targetIndex++;
            } else if (diff < 0 && targetIndex > 0) {
                targetIndex--;
            }
        }
        
        isScrolling = true;
        this.scrollToItem(targetIndex);
        
        setTimeout(() => {
            isScrolling = false;
        }, 300);
        
        this.updateActiveDot(targetIndex);
    });
    
    this.carouselContainer.addEventListener('mouseleave', () => {
        if (isDragging) {
            isDragging = false;
            // Se soltar fora, volta para o slide atual
            isScrolling = true;
            this.scrollToItem(targetIndex);
            
            setTimeout(() => {
                isScrolling = false;
            }, 300);
        }
    });
}

        /**
         * Inicialização principal com tratamento de erro
         */
        initialize() {
            if (this.initialized) return;
            
            try {
                if (!this.getDOMElements()) {
                    console.warn('Elementos do carousel não encontrados');
                    return;
                }

                this.createDots();
                this.setupScrollHandler();
                this.initialized = true;
                
                
            } catch (error) {
                console.error('Falha na inicialização do carousel:', error);
            }
        }

        /**
         * Cleanup para evitar memory leaks
         */
        destroy() {
            try {
                if (this.scrollHandler) {
                    this.carouselContainer?.removeEventListener('scroll', this.scrollHandler);
                    this.scrollHandler = null;
                }
                
                // Limpa event listeners dos dots
                const dots = this.dotsContainer?.querySelectorAll('.carousel-dot');
                dots?.forEach(dot => {
                    const newDot = dot.cloneNode(true);
                    dot.parentNode?.replaceChild(newDot, dot);
                });
                
                this.initialized = false;
            } catch (error) {
                console.error('Erro no cleanup do carousel:', error);
            }
        }
    }

    // Gerenciador de inicialização segura
    function initializeCarouselSafe() {
        let carouselManager = null;
        
        try {
            carouselManager = new CarouselManager();
            carouselManager.initialize();
            
            // Cleanup em caso de navegação SPA ou unload
            window.addEventListener('beforeunload', () => {
                carouselManager?.destroy();
            }, { passive: true });
            
            // Re-inicializa em caso de mudanças no DOM (para SPAs)
            if (typeof MutationObserver !== 'undefined') {
                const observer = new MutationObserver(() => {
                    if (!carouselManager.initialized && 
                        document.querySelector('.carousel-container')) {
                        carouselManager.initialize();
                    }
                });
                
                observer.observe(document.body, { 
                    childList: true, 
                    subtree: true 
                });
            }
            
        } catch (error) {
            console.error('Falha crítica na inicialização do carousel:', error);
        }
        
        return carouselManager;
    }

    // Inicialização condicional
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeCarouselSafe);
    } else {
        setTimeout(initializeCarouselSafe, 0);
    }
})();