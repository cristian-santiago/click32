document.addEventListener('DOMContentLoaded', function () {

    // ══════════════════════════════════
    // SCROLL REVEAL
    // ══════════════════════════════════
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


    // ══════════════════════════════════
    // SCROLL HINT: esconde ao rolar
    // ══════════════════════════════════
    const scrollHint = document.querySelector('.hero-scroll-hint');

    if (scrollHint) {
        window.addEventListener('scroll', function () {
            if (window.scrollY > 60) {
                scrollHint.style.opacity = '0';
                scrollHint.style.pointerEvents = 'none';
            }
        }, { passive: true });
    }


    // ══════════════════════════════════
    // TOOLBAR: highlight do link ativo
    // ══════════════════════════════════
    const currentPath = window.location.pathname;
    document.querySelectorAll('.toolbar-container a').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.style.color = 'var(--cyan)';
        }
    });

});