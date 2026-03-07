/**
 * Flyer Modal Manager - Versão com Swiper.js integrado
 * Mantém o CSS original, adiciona classes do Swiper para compatibilidade.
 * Remove lógica custom de zoom/swipe, usa Swiper para carrossel, zoom (pinch/wheel), swipe e pagination.
 * Botões de zoom usam API do Swiper com cálculo de steps.
 */
(function() {
    'use strict';
    
    class FlyerModalManager {
        constructor() {
            this.modalElement = null;
            this.loadingSpinner = null;
            this.errorMessage = null;
            this.isFetching = false;
            this.currentFlyerIndex = 0;
            this.eventListeners = new Map();
            this.timeouts = new Set();
            this.initialized = false;
            this.swiper = null; // Instância do Swiper
            
            this.config = {
                fetchTimeout: 10000,
                preloadTimeout: 2000,
                maxZoom: 4,
                minZoom: 1,
                zoomStep: 0.35,
                swipeThreshold: 50
            };
        }

        validateStoreId(storeId) {
            const id = parseInt(storeId, 10);
            return !isNaN(id) && id > 0 && id < 1000000;
        }

        sanitizeUrl(url) {
            try {
                const parsed = new URL(url, window.location.origin);
                if (parsed.origin === window.location.origin && 
                    parsed.pathname.startsWith('/media/')) {
                    return parsed.toString();
                }
                return null;
            } catch {
                return null;
            }
        }

        createSafeElement(tag, attributes = {}, innerHTML = '') {
            try {
                const element = document.createElement(tag);
                Object.entries(attributes).forEach(([key, value]) => {
                    if (key.startsWith('on')) return;
                    element.setAttribute(key, value);
                });
                
                if (innerHTML && !innerHTML.includes('<')) {
                    element.textContent = innerHTML;
                } else if (innerHTML) {
                    element.innerHTML = innerHTML
                        .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
                        .replace(/on\w+\s*=/gi, 'blocked=');
                }
                
                return element;
            } catch (error) {
                console.error('Erro ao criar elemento:', error);
                return null;
            }
        }

        initializeModal() {
            try {
                this.modalElement = document.getElementById('flyerModal');
                this.loadingSpinner = document.querySelector('.flyer-modal .flyer-loading-spinner');
                this.errorMessage = document.querySelector('.flyer-modal .flyer-error-message');
                
                if (!this.modalElement) {
                    console.warn('Modal element não encontrado');
                    return false;
                }

                this.modalElement.classList.remove('show');
                this.modalElement.style.display = 'none';
                this.modalElement.setAttribute('aria-hidden', 'true');
                
                if (this.loadingSpinner) this.loadingSpinner.classList.remove('active');
                if (this.errorMessage) this.errorMessage.style.display = 'none';
                
                return true;
            } catch (error) {
                console.error('Erro na inicialização do modal:', error);
                return false;
            }
        }

        closeModal() {
            try {
                if (this.modalElement) {
                    this.modalElement.classList.remove('show');
                    this.modalElement.style.display = 'none';
                    this.modalElement.setAttribute('aria-hidden', 'true');
                }
                
                document.body.style.overflow = 'auto';
                if (this.loadingSpinner) this.loadingSpinner.classList.remove('active');
                if (this.errorMessage) this.errorMessage.style.display = 'none';
                
                this.isFetching = false;
                this.currentFlyerIndex = 0;
                
                const carouselTrack = document.getElementById('flyerCarouselTrack');
                const indicatorsContainer = document.getElementById('flyerCarouselIndicators');
                if (carouselTrack) carouselTrack.innerHTML = '';
                if (indicatorsContainer) indicatorsContainer.innerHTML = '';
                
                this.clearAllTimeouts();
                
                // Destroi Swiper se existir
                if (this.swiper) {
                    this.swiper.destroy(true, true);
                    this.swiper = null;
                }
                
            } catch (error) {
                console.error('Erro ao fechar modal:', error);
            }
        }

        async handleFlyerFetch(storeId) {
            if (this.isFetching || !this.validateStoreId(storeId)) return;

            this.isFetching = true;

            try {
                const carouselTrack = document.getElementById('flyerCarouselTrack');
                const indicatorsContainer = document.getElementById('flyerCarouselIndicators');

                if (!carouselTrack || !indicatorsContainer) {
                    console.error('Elementos não encontrados:', { carouselTrack, indicatorsContainer });
                    this.showError('Elementos do carrossel não encontrados.');
                    this.closeModal();
                    return;
                }

                this.showLoading();
                this.openModal();

                const timeoutId = setTimeout(() => {
                    if (this.isFetching) {
                        this.showError('A solicitação está demorando muito.');
                        this.closeModal();
                    }
                }, this.config.fetchTimeout);

                this.timeouts.add(timeoutId);

                const response = await fetch(`/fetch-flyer-pages/${storeId}/`, { 
                    method: 'GET',
                    credentials: 'same-origin'
                });

                clearTimeout(timeoutId);
                this.timeouts.delete(timeoutId);

                if (!response.ok) throw new Error(`HTTP ${response.status}`);

                const data = await response.json();

                if (data.error) {
                    this.showError(data.error);
                    return;
                }

                if (!data.page_urls || !Array.isArray(data.page_urls) || data.page_urls.length === 0) {
                    this.showError('Nenhuma imagem disponível para o encarte.');
                    return;
                }

                await this.loadFlyerPages(data.page_urls, carouselTrack, indicatorsContainer);
                
            } catch (error) {
                console.error('Erro ao carregar flyer:', error);
                this.showError('Erro ao carregar o encarte. Tente novamente.');
            } finally {
                this.hideLoading();
                this.isFetching = false;
            }
        }

        loadFlyerPages(pageUrls, carouselTrack, indicatorsContainer) {
            const safeUrls = pageUrls.map(url => this.sanitizeUrl(url)).filter(Boolean);
            if (!safeUrls.length) return this.showError('Nenhuma URL válida');

            this.createCarouselItems(safeUrls, carouselTrack, indicatorsContainer);
            this.initializeSwiper(carouselTrack, indicatorsContainer);
            this.setupWheelZoom();
            this.setupZoomControls();
        }

        createCarouselItems(urls, carouselTrack, indicatorsContainer) {
            carouselTrack.innerHTML = '';
            indicatorsContainer.innerHTML = '';

            const container = carouselTrack.parentElement;
            container.classList.add('swiper');
            carouselTrack.classList.add('swiper-wrapper');

            urls.forEach((url, i) => {
                const slide = this.createSafeElement('div', {
                    class: `swiper-slide flyer-carousel-item ${i === 0 ? 'active' : ''}`,
                    'data-index': i
                });

                const zoomContainer = this.createSafeElement('div', {
                    class: 'swiper-zoom-container flyer-pinch-zoom-container'
                });

                const img = this.createSafeElement('img', {
                    src: url,
                    alt: `Página ${i + 1}`,
                    class: 'swiper-lazy flyer-carousel-image',
                    loading: 'lazy'
                });

                const preloader = this.createSafeElement('div', { class: 'swiper-lazy-preloader' });

                zoomContainer.append(img, preloader);
                slide.appendChild(zoomContainer);
                carouselTrack.appendChild(slide);
            });
        }
initializeSwiper(track, indicators) {

    this.swiper = new Swiper(track.parentElement, {

        slidesPerView: 1,
        spaceBetween: 0,

        effect: "slide",
        speed: 350,

        centeredSlides: false,

        threshold: this.config.swipeThreshold,

        longSwipesRatio: 0.1,
        longSwipesMs: 200,
        shortSwipes: true,

        followFinger: false,

        resistance: false,
        touchReleaseOnEdges: false,

        zoom: {
            maxRatio: this.config.maxZoom,
            minRatio: this.config.minZoom,
            toggle: true
        },

        pagination: {
            el: ".swiper-pagination",
            clickable: true
        },

        lazy: true,
        preloadImages: false,

        on: {

            slideChange: () => {
                this.currentFlyerIndex = this.swiper.activeIndex;
            },

            zoomChange: (swiper, scale) => {

                if (scale > 1) {
                    swiper.allowTouchMove = false;
                } else {
                    swiper.allowTouchMove = true;
                }

            }

        }

    });

}

        setupWheelZoom() {
    const container = this.swiper?.el;

    if (!container) return;

    container.addEventListener('wheel', (e) => {
        if (!this.swiper) return;

        e.preventDefault();

        const current = this.swiper.zoom.scale || 1;

        if (e.deltaY < 0) {
            this.swiper.zoom.in(Math.min(current + this.config.zoomStep, this.config.maxZoom));
        } else {
            this.swiper.zoom.in(Math.max(current - this.config.zoomStep, this.config.minZoom));
        }

    }, { passive: false });
}

        setupZoomControls() {
            const step = this.config.zoomStep;
            document.querySelectorAll('.flyer-zoom-in').forEach(btn => {
                btn.addEventListener('click', () => {
                    if (!this.swiper) return;
                    const current = this.swiper.zoom.scale || 1;
                    this.swiper.zoom.in(Math.min(current + step, this.config.maxZoom));
                });
            });

            document.querySelectorAll('.flyer-zoom-out').forEach(btn => {
                btn.addEventListener('click', () => {
                    if (!this.swiper) return;
                    const current = this.swiper.zoom.scale || 1;
                    this.swiper.zoom.in(Math.max(current - step, this.config.minZoom));
                });
            });

            document.querySelectorAll('.flyer-zoom-reset').forEach(btn => {
                btn.addEventListener('click', () => this.swiper?.zoom.in(this.config.minZoom));
            });
        }

        showLoading() {
            if (this.loadingSpinner) this.loadingSpinner.classList.add('active');
            if (this.errorMessage) this.errorMessage.style.display = 'none';
        }

        hideLoading() {
            if (this.loadingSpinner) this.loadingSpinner.classList.remove('active');
        }

        showError(message) {
            console.error('Flyer Error:', message);
            if (this.errorMessage) {
                this.errorMessage.textContent = message;
                this.errorMessage.style.display = 'block';
            }
        }

        openModal() {
            if (this.modalElement) {
                this.modalElement.classList.add('show');
                this.modalElement.setAttribute('aria-hidden', 'false');
                this.modalElement.style.display = 'flex'; 
                document.body.style.overflow = 'hidden';
                this.hideLoading();
            }
        }

        clearAllTimeouts() {
            this.timeouts.forEach(timeoutId => clearTimeout(timeoutId));
            this.timeouts.clear();
        }

        destroy() {
            try {
                this.closeModal();
                this.clearAllTimeouts();
                this.eventListeners.forEach((listeners, element) => {
                    Object.entries(listeners).forEach(([event, handler]) => {
                        element.removeEventListener(event, handler);
                    });
                });
                this.eventListeners.clear();
                this.initialized = false;
            } catch (error) {
                console.error('Erro no cleanup:', error);
            }
        }

        initialize() {
            if (this.initialized) return;
            
            try {
                if (!this.initializeModal()) return;

                document.querySelectorAll('.open-flyer-modal').forEach(link => {
                    const handleClick = (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        const storeId = link.getAttribute('data-store-id');
                        this.handleFlyerFetch(storeId);
                    };
                    link.addEventListener('click', handleClick);
                    this.eventListeners.set(link, { click: handleClick });
                });

                const closeBtn = this.modalElement?.querySelector('.flyer-btn-close');
                if (closeBtn) {
                    const handleClose = () => {
                        this.closeModal();
                        closeBtn.blur();
                    };
                    closeBtn.addEventListener('click', handleClose);
                    this.eventListeners.set(closeBtn, { click: handleClose });
                }

                this.initialized = true;
                
            } catch (error) {
                console.error('Erro na inicialização do flyer modal:', error);
            }
        }
    }

function initializeFlyerModalSafe() {
        let modalManager = new FlyerModalManager();
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => modalManager.initialize());
        } else {
            setTimeout(() => modalManager.initialize(), 0);
        }
        window.addEventListener('beforeunload', () => modalManager.destroy?.(), { passive: true });
        return modalManager;
    }

    initializeFlyerModalSafe();
})();