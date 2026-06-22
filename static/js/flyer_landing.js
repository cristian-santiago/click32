document.addEventListener('DOMContentLoaded', function () {

    // SCROLL REVEAL
    const revealEls = document.querySelectorAll('.reveal');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                const siblings = [...revealEls].filter(el =>
                    el.closest('section') === entry.target.closest('section') &&
                    !el.classList.contains('visible')
                );
                const index = siblings.indexOf(entry.target);
                setTimeout(() => {
                    entry.target.classList.add('visible');
                }, index * 80);
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.12,
        rootMargin: '0px 0px -40px 0px'
    });

    revealEls.forEach(el => observer.observe(el));

    // SCROLL HINT
    const scrollHint = document.querySelector('.hero-scroll-hint');

    if (scrollHint) {
        window.addEventListener('scroll', function () {
            if (window.scrollY > 60) {
                scrollHint.style.opacity = '0';
                scrollHint.style.pointerEvents = 'none';
            }
        }, { passive: true });
    }

    // TOOLBAR
    const currentPath = window.location.pathname;
    document.querySelectorAll('.toolbar-container a').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.style.color = 'var(--cyan)';
        }
    });

    // ══════════════════════════════════
    // CARROSSEL 3D - SOBREPOSIÇÃO
    // ══════════════════════════════════
    const slides = document.querySelectorAll('.phone-card');
    const progressBars = document.querySelectorAll('.progress-bar');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const carousel = document.getElementById('phoneCarousel');

    let currentIndex = 0;
    const totalSlides = slides.length;
    let isAnimating = false;
    let startX = 0;
    let isDragging = false;

    // Mapeamento de posições
    const positions = ['card-left', 'card-center', 'card-right', 'card-hidden-left', 'card-hidden-right'];

    function updateCarousel(newIndex) {
        if (isAnimating) return;
        if (newIndex < 0) newIndex = totalSlides - 1;
        if (newIndex >= totalSlides) newIndex = 0;

        isAnimating = true;
        currentIndex = newIndex;

        // Calcula as posições relativas
        const cards = [];
        for (let i = 0; i < totalSlides; i++) {
            let offset = i - currentIndex;
            if (offset < -1) offset += totalSlides;
            if (offset > 1) offset -= totalSlides;
            cards.push({ element: slides[i], offset: offset });
        }

        // Aplica as classes
        cards.forEach(({ element, offset }) => {
            // Remove todas as classes de posição
            element.classList.remove('card-left', 'card-center', 'card-right', 'card-hidden-left', 'card-hidden-right');

            if (offset === 0) {
                element.classList.add('card-center');
            } else if (offset === -1) {
                element.classList.add('card-left');
            } else if (offset === 1) {
                element.classList.add('card-right');
            } else if (offset < -1) {
                element.classList.add('card-hidden-left');
            } else if (offset > 1) {
                element.classList.add('card-hidden-right');
            }
        });

        // Atualiza progresso
        progressBars.forEach((bar, i) => {
            bar.classList.toggle('active', i === currentIndex);
        });

        setTimeout(() => {
            isAnimating = false;
        }, 650);
    }

    function nextSlide() {
        updateCarousel(currentIndex + 1);
    }

    function prevSlide() {
        updateCarousel(currentIndex - 1);
    }

    // Botões
    nextBtn.addEventListener('click', nextSlide);
    prevBtn.addEventListener('click', prevSlide);

    // Teclado
    document.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowRight') nextSlide();
        if (e.key === 'ArrowLeft') prevSlide();
    });

    // Drag / Swipe
    carousel.addEventListener('mousedown', function (e) {
        startX = e.clientX;
        isDragging = true;
        carousel.style.cursor = 'grabbing';
    });

    carousel.addEventListener('mousemove', function (e) {
        if (!isDragging) return;
        const diff = startX - e.clientX;
        if (Math.abs(diff) > 40) {
            if (diff > 0) nextSlide();
            else prevSlide();
            isDragging = false;
            carousel.style.cursor = 'grab';
        }
    });

    carousel.addEventListener('mouseup', function () {
        isDragging = false;
        carousel.style.cursor = 'grab';
    });

    carousel.addEventListener('mouseleave', function () {
        isDragging = false;
        carousel.style.cursor = 'grab';
    });

    // Touch
    let touchStartX = 0;
    carousel.addEventListener('touchstart', function (e) {
        touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });

    carousel.addEventListener('touchend', function (e) {
        const diff = touchStartX - e.changedTouches[0].screenX;
        if (Math.abs(diff) > 40) {
            if (diff > 0) nextSlide();
            else prevSlide();
        }
    }, { passive: true });

    // Inicializa
    updateCarousel(0);
});