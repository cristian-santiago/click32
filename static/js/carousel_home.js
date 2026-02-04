/**
 * Configura o carrossel com navegação por pontos, swipe e transição automática.
 */
(function() {
    'use strict';
    
    const CAROUSEL_CONFIG = {
        autoSlideInterval: 3000,
        swipeThreshold: 50
    };

    function initCarousel() {
        const carouselContainer = document.querySelector('.carousel-container');
        const carouselItems = document.querySelectorAll('.carousel-item');
        const dotsContainer = document.querySelector('.carousel-dots');
        const fadeMask = document.querySelector('.carousel-fade-mask');
        
        if (!carouselContainer || carouselItems.length === 0) return;

        let activated = false;
        let slideIndex = 1;
        let autoSlideInterval;

        // Configuração inicial do carrossel
        function setupCarousel() {
            carouselContainer.style.width = `${carouselItems.length * 100}%`;
            
            carouselItems.forEach(item => {
                item.style.width = `${100 / carouselItems.length}%`;
            });

            createDots();
            showSlides(slideIndex);
            startAutoSlide();
            setupTouchEvents();
        }

        function createDots() {
            carouselItems.forEach((_, index) => {
                const dot = document.createElement('div');
                dot.className = 'carousel-dot';
                if (index === 0) dot.classList.add('active');
                
                // Previne múltiplos event listeners
                dot.addEventListener('click', () => goToSlide(index + 1));
                dotsContainer.appendChild(dot);
            });
        }

        function goToSlide(n) {
            slideIndex = n;
            showSlides(slideIndex);
            resetAutoSlide();
        }

        function showSlides(n) {
            if (n > carouselItems.length) slideIndex = 1;
            if (n < 1) slideIndex = carouselItems.length;

            const slideWidthPercent = 100 / carouselItems.length;
            carouselContainer.style.transform = `translateX(-${(slideIndex - 1) * slideWidthPercent}%)`;

            // Atualiza itens ativos
            carouselItems.forEach((item, index) => {
                item.classList.toggle('active', index === slideIndex - 1);
            });

            // Atualiza dots ativos
            document.querySelectorAll('.carousel-dot').forEach((dot, index) => {
                dot.classList.toggle('active', index === slideIndex - 1);
            });
        }

        function autoSlide() {
            slideIndex++;
            showSlides(slideIndex);
        }

        function startAutoSlide() {
            autoSlideInterval = setInterval(autoSlide, CAROUSEL_CONFIG.autoSlideInterval);
        }

        function resetAutoSlide() {
            clearInterval(autoSlideInterval);
            startAutoSlide();
        }

        function setupTouchEvents() {
            let touchStartX = 0;
            let touchEndX = 0;

            const handleTouchStart = (e) => {
                touchStartX = e.changedTouches[0].screenX;
            };

            const handleTouchEnd = (e) => {
                touchEndX = e.changedTouches[0].screenX;
                handleSwipe();
            };

            function handleSwipe() {
                const diff = touchStartX - touchEndX;
                if (Math.abs(diff) < CAROUSEL_CONFIG.swipeThreshold) return;
                
                if (diff > CAROUSEL_CONFIG.swipeThreshold) {
                    goToSlide(slideIndex + 1);
                } else {
                    goToSlide(slideIndex - 1);
                }
            }

            carouselContainer.addEventListener('touchstart', handleTouchStart, { passive: true });
            carouselContainer.addEventListener('touchend', handleTouchEnd, { passive: true });
        }

        function showFadeOnScroll() {
            if (!activated && window.scrollY > 0) {
                fadeMask?.classList.remove('hidden');
                activated = true;
                window.removeEventListener('scroll', showFadeOnScroll);
            }
        }

        // Inicialização
        setupCarousel();
        window.addEventListener('scroll', showFadeOnScroll, { passive: true });

        // Cleanup para evitar memory leaks
        return () => {
            clearInterval(autoSlideInterval);
            window.removeEventListener('scroll', showFadeOnScroll);
        };
    }

    // Inicializa quando o DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initCarousel);
    } else {
        initCarousel();
    }
})();