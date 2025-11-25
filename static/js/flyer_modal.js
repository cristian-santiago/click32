/**
 * Flyer Modal Manager - Versão segura e funcional
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
            this.zoomState = this.getInitialZoomState();
            this.eventListeners = new Map();
            this.timeouts = new Set();
            this.initialized = false;
            this.touchStartX = 0;
            this.isSwiping = false;
            
            this.config = {
                fetchTimeout: 10000,
                preloadTimeout: 2000,
                maxZoom: 4,
                minZoom: 1,
                zoomStep: 0.5,
                swipeThreshold: 50,
                wheelZoomStep: 0.1
            };
        }

        getInitialZoomState() {
            return {
                scale: 1,
                translateX: 0,
                translateY: 0,
                baseTranslateY: 0,
                startDistance: 0,
                startX: 0,
                startY: 0,
                isPinching: false,
                isDragging: false
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
                this.loadingSpinner = document.querySelector('.flyer-modal .loading-spinner');
                this.errorMessage = document.querySelector('.flyer-modal .error-message');
                
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
                this.zoomState = this.getInitialZoomState();
                
                const carouselInner = document.getElementById('flyerCarouselInner');
                const indicatorsContainer = document.getElementById('flyerIndicators');
                if (carouselInner) carouselInner.innerHTML = '';
                if (indicatorsContainer) indicatorsContainer.innerHTML = '';
                
                this.clearAllTimeouts();
                
            } catch (error) {
                console.error('Erro ao fechar modal:', error);
            }
        }

        getTouchDistance(touches) {
            try {
                const dx = touches[0].clientX - touches[1].clientX;
                const dy = touches[0].clientY - touches[1].clientY;
                return Math.sqrt(dx * dx + dy * dy);
            } catch (error) {
                console.error('Erro ao calcular distância de toque:', error);
                return 0;
            }
        }

        applyTransform(img) {
            try {
                if (!img) return;
                const totalTranslateY = this.zoomState.translateY + this.zoomState.baseTranslateY;
                img.style.transform = `scale(${this.zoomState.scale}) translate(${this.zoomState.translateX}px, ${totalTranslateY}px)`;
            } catch (error) {
                console.error('Erro ao aplicar transformação:', error);
            }
        }

        adjustInitialPosition(img) {
            try {
                const container = img.parentElement;
                if (!container) return;

                const containerHeight = container.clientHeight;
                const containerWidth = container.clientWidth;
                const imgHeight = img.clientHeight;
                const imgWidth = img.clientWidth;

                this.zoomState.scale = 1;
                this.zoomState.translateX = 0;
                this.zoomState.translateY = 0;

                if (imgHeight < containerHeight) {
                    this.zoomState.baseTranslateY = (containerHeight - imgHeight) / 2;
                } else {
                    this.zoomState.baseTranslateY = 0;
                }

                if (imgWidth < containerWidth) {
                    this.zoomState.translateX = (containerWidth - imgWidth) / 2;
                }

                this.applyTransform(img);
            } catch (error) {
                console.error('Erro ao ajustar posição inicial:', error);
            }
        }

        setupSwipeNavigation() {
            const carouselInner = document.getElementById('flyerCarouselInner');
            if (!carouselInner) return;

            const handleTouchStart = (e) => {
                if (e.touches.length === 1 && this.zoomState.scale === 1) {
                    this.touchStartX = e.touches[0].clientX;
                    this.isSwiping = true;
                }
            };

            const handleTouchMove = (e) => {
                if (e.touches.length > 1) this.isSwiping = false;
            };

            const handleTouchEnd = (e) => {
                if (!this.isSwiping || this.zoomState.scale > 1) {
                    this.isSwiping = false;
                    return;
                }

                const endX = e.changedTouches[0].clientX;
                const deltaX = endX - this.touchStartX;
                const items = document.querySelectorAll('.flyer-modal .carousel-item');
                
                if (Math.abs(deltaX) > this.config.swipeThreshold) {
                    if (deltaX > 0 && this.currentFlyerIndex > 0) {
                        this.goToSlide(this.currentFlyerIndex - 1);
                    } else if (deltaX < 0 && this.currentFlyerIndex < items.length - 1) {
                        this.goToSlide(this.currentFlyerIndex + 1);
                    }
                }
                
                this.isSwiping = false;
            };

            carouselInner.addEventListener('touchstart', handleTouchStart, { passive: true });
            carouselInner.addEventListener('touchmove', handleTouchMove, { passive: true });
            carouselInner.addEventListener('touchend', handleTouchEnd, { passive: true });

            this.eventListeners.set(carouselInner, {
                touchstart: handleTouchStart,
                touchmove: handleTouchMove,
                touchend: handleTouchEnd
            });
        }

            applyModalStyles() {
                if (!this.modalElement) return;
                
                const modalDialog = this.modalElement.querySelector('.modal-dialog');
                if (modalDialog) {
                    modalDialog.style.display = 'flex';
                    modalDialog.style.alignItems = 'center';
                    modalDialog.style.minHeight = '100vh';
                    modalDialog.style.margin = '0 auto';
                }

                // SÓ configurar estilos, NÃO mostrar
                this.modalElement.style.alignItems = 'center';
                this.modalElement.style.justifyContent = 'center';
                this.modalElement.style.position = 'fixed';
                this.modalElement.style.top = '0';
                this.modalElement.style.left = '0';
                this.modalElement.style.width = '100%';
                this.modalElement.style.height = '100%';
                this.modalElement.style.zIndex = '9999';
                this.modalElement.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
                // NÃO definir display aqui - isso será feito no openModal()
            }
        async handleFlyerFetch(storeId) {
            if (this.isFetching || !this.validateStoreId(storeId)) return;

            this.isFetching = true;

            try {
                const carouselInner = document.getElementById('flyerCarouselInner');
                const indicatorsContainer = document.getElementById('flyerIndicators');

                if (!carouselInner || !indicatorsContainer) {
                    this.showError('Elementos do carrossel não encontrados.');
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

                await this.loadFlyerPages(data.page_urls, carouselInner, indicatorsContainer);
                
            } catch (error) {
                console.error('Erro ao carregar flyer:', error);
                this.showError('Erro ao carregar o encarte. Tente novamente.');
            } finally {
                this.hideLoading();
                this.isFetching = false;
            }
        }

        async loadFlyerPages(pageUrls, carouselInner, indicatorsContainer) {
            try {
                const safeUrls = pageUrls
                    .map(url => this.sanitizeUrl(url))
                    .filter(url => url !== null);

                if (safeUrls.length === 0) throw new Error('Nenhuma URL válida encontrada');

                await this.preloadImages(safeUrls);
                this.createCarouselItems(safeUrls, carouselInner, indicatorsContainer);
                this.setupSwipeNavigation();
                this.setupZoomControls();
                
            } catch (error) {
                console.error('Erro ao carregar páginas:', error);
                throw error;
            }
        }

        async preloadImages(urls) {
            const preloadPromises = urls.map((url, index) => {
                return new Promise((resolve, reject) => {
                    const img = new Image();
                    img.onload = () => resolve(url);
                    img.onerror = () => reject(new Error(`Falha ao carregar imagem ${index + 1}`));
                    img.src = url;
                });
            });

            const timeoutPromise = new Promise((_, reject) => {
                const timeoutId = setTimeout(() => {
                    reject(new Error('Timeout no carregamento de imagens'));
                }, this.config.preloadTimeout);
                this.timeouts.add(timeoutId);
            });

            return Promise.race([Promise.allSettled(preloadPromises), timeoutPromise]);
        }

        createCarouselItems(urls, carouselInner, indicatorsContainer) {
            try {
                carouselInner.innerHTML = '';
                indicatorsContainer.innerHTML = '';

                urls.forEach((url, index) => {
                    const carouselItem = this.createSafeElement('div', {
                        'class': `carousel-item ${index === 0 ? 'active' : ''}`,
                        'data-index': index
                    });
                    
                    carouselItem.style.transform = index === 0 ? 'translateX(0)' : 'translateX(100%)';
                    carouselItem.style.opacity = index === 0 ? '1' : '0';

                    const zoomContainer = this.createSafeElement('div', {
                        'class': 'pinch-zoom-container',
                        'style': 'width: 100%; height: 100%; display: flex; align-items: flex-start; justify-content: center; overflow-y: auto; overflow-x: hidden; touch-action: pan-y;'
                    });

                    const img = this.createSafeElement('img', {
                        'src': url,
                        'alt': `Página ${index + 1} do encarte`,
                        'style': 'width: 100%; height: auto; max-width: none; user-select: none; -webkit-user-drag: none; display: block;',
                        'loading': 'lazy'
                    });

                    zoomContainer.appendChild(img);
                    carouselItem.appendChild(zoomContainer);
                    carouselInner.appendChild(carouselItem);

                    this.setupImageEvents(img, zoomContainer);
                    this.createCarouselIndicator(index, indicatorsContainer);
                });

                this.currentFlyerIndex = 0;

            } catch (error) {
                console.error('Erro ao criar itens do carousel:', error);
                throw error;
            }
        }

        setupImageEvents(img, container) {
            const handleWheel = (e) => {
                e.preventDefault();
                const delta = e.deltaY > 0 ? -this.config.wheelZoomStep : this.config.wheelZoomStep;
                this.zoomState.scale = Math.max(this.config.minZoom, Math.min(this.config.maxZoom, this.zoomState.scale + delta));
                this.applyTransform(img);
            };

            const handleTouchStart = (e) => {
                if (e.touches.length === 2) {
                    this.zoomState.isPinching = true;
                    this.zoomState.startDistance = this.getTouchDistance(e.touches);
                }
            };

            const handleTouchMove = (e) => {
                if (this.zoomState.isPinching && e.touches.length === 2) {
                    e.preventDefault();
                    const currentDistance = this.getTouchDistance(e.touches);
                    const scaleChange = currentDistance / this.zoomState.startDistance;
                    this.zoomState.scale = Math.max(this.config.minZoom, Math.min(this.config.maxZoom, this.zoomState.scale * scaleChange));
                    this.zoomState.startDistance = currentDistance;
                    this.applyTransform(img);
                }
            };

            const handleTouchEnd = () => {
                this.zoomState.isPinching = false;
            };

            const handleImageLoad = () => {
                this.adjustInitialPosition(img);
            };

            container.addEventListener('wheel', handleWheel, { passive: false });
            container.addEventListener('touchstart', handleTouchStart, { passive: true });
            container.addEventListener('touchmove', handleTouchMove, { passive: false });
            container.addEventListener('touchend', handleTouchEnd, { passive: true });
            img.addEventListener('load', handleImageLoad);

            this.eventListeners.set(container, {
                wheel: handleWheel,
                touchstart: handleTouchStart,
                touchmove: handleTouchMove,
                touchend: handleTouchEnd
            });

            this.eventListeners.set(img, { load: handleImageLoad });
        }

        createCarouselIndicator(index, container) {
            const indicator = this.createSafeElement('button', {
                'type': 'button',
                'class': `carousel-indicator ${index === 0 ? 'active' : ''}`,
                'aria-label': `Slide ${index + 1}`
            });

            const handleClick = () => this.goToSlide(index);
            indicator.addEventListener('click', handleClick);
            this.eventListeners.set(indicator, { click: handleClick });
            container.appendChild(indicator);
        }

        goToSlide(index) {
            try {
                const items = document.querySelectorAll('.flyer-modal .carousel-item');
                const indicators = document.querySelectorAll('.flyer-modal .carousel-indicator');
                
                if (index < 0 || index >= items.length) return;

                items.forEach((item, i) => {
                    item.classList.remove('active');
                    item.style.transform = i < index ? 'translateX(-100%)' : 'translateX(100%)';
                    item.style.opacity = '0';
                });

                items[index].classList.add('active');
                items[index].style.transform = 'translateX(0)';
                items[index].style.opacity = '1';

                indicators.forEach(ind => ind.classList.remove('active'));
                indicators[index].classList.add('active');

                this.currentFlyerIndex = index;
                this.zoomState = this.getInitialZoomState();
                
                const img = items[index].querySelector('img');
                if (img) {
                    // REPOSICIONA a imagem após resetar o zoom
                    setTimeout(() => {
                        this.adjustInitialPosition(img);
                        this.applyTransform(img);
                    }, 50);
                }

            } catch (error) {
                console.error('Erro ao navegar para slide:', error);
            }
        }
        setupZoomControls() {
            const setupZoomButton = (selector, action) => {
                document.querySelectorAll(selector).forEach(button => {
                    const handleClick = () => {
                        const items = document.querySelectorAll('.flyer-modal .carousel-item');
                        const img = items[this.currentFlyerIndex]?.querySelector('img');
                        if (img) {
                            action();
                            this.applyTransform(img);
                        }
                    };
                    button.addEventListener('click', handleClick);
                    this.eventListeners.set(button, { click: handleClick });
                });
            };

            setupZoomButton('.zoom-in', () => {
                this.zoomState.scale = Math.min(this.config.maxZoom, this.zoomState.scale + this.config.zoomStep);
            });

            setupZoomButton('.zoom-out', () => {
                this.zoomState.scale = Math.max(this.config.minZoom, this.zoomState.scale - this.config.zoomStep);
            });

            setupZoomButton('.zoom-reset', () => {
              this.zoomState = this.getInitialZoomState();
              const items = document.querySelectorAll('.flyer-modal .carousel-item');
              const img = items[this.currentFlyerIndex]?.querySelector('img');
              if (img) {
                  // REPOSICIONA após reset
                  this.adjustInitialPosition(img);
                  this.applyTransform(img);
              }
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
            this.applyModalStyles();
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

                const closeBtn = this.modalElement?.querySelector('.btn-close');
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
        let modalManager = null;
        
        try {
            modalManager = new FlyerModalManager();
            
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => modalManager.initialize());
            } else {
                setTimeout(() => modalManager.initialize(), 0);
            }
            
            window.addEventListener('beforeunload', () => {
                modalManager?.destroy();
            }, { passive: true });
            
        } catch (error) {
            console.error('Falha crítica na inicialização do flyer modal:', error);
        }
        
        return modalManager;
    }

    initializeFlyerModalSafe();
})();