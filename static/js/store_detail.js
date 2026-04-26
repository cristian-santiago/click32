(function () {
  'use strict';

  /* ══════════════════════════════
     SIDEBAR
  ══════════════════════════════ */
  const sidebar = document.getElementById('sidebar');
  const toggle  = document.getElementById('sbToggle');
  const overlay = document.getElementById('sbOverlay');

  function openSB() {
    sidebar.classList.add('expanded');
    overlay.classList.add('visible');
  }
  function closeSB() {
    sidebar.classList.remove('expanded');
    overlay.classList.remove('visible');
    sidebar.querySelectorAll('.sb-item.open').forEach(el => el.classList.remove('open'));
  }

  toggle.addEventListener('click', () =>
    sidebar.classList.contains('expanded') ? closeSB() : openSB()
  );
  overlay.addEventListener('click', closeSB);

  sidebar.querySelectorAll('.sb-row[role="button"]').forEach(row => {
    row.addEventListener('click', () => {
      if (!sidebar.classList.contains('expanded')) { openSB(); return; }
      const item   = row.closest('.sb-item');
      const isOpen = item.classList.contains('open');
      sidebar.querySelectorAll('.sb-item.open').forEach(el => el.classList.remove('open'));
      if (!isOpen) item.classList.add('open');
    });
  });

  
  /* ══════════════════════════════
     HERO CAROUSEL
     Arquitetura: transform translateX em #heroSlides
     NÃO usa scrollLeft — diferente do store_detail
  ══════════════════════════════ */
  (function initHeroCarousel() {
    const slidesEl = document.getElementById('heroSlides');
    const dotsWrap = document.getElementById('heroDots');
    const hero     = document.getElementById('hero');

    if (!slidesEl || !dotsWrap || !hero) return;

    const items = slidesEl.querySelectorAll('.hero-slide');
    const total = items.length;
    if (total === 0) return;

    let cur    = 0;
    let drag   = false;
    let locked = false;
    let sx     = 0;
    let autoplayTimer;

    // — Dots —
    items.forEach((_, i) => {
      const d = document.createElement('div');
      d.className = 'hero-dot' + (i === 0 ? ' active' : '');
      d.setAttribute('role', 'button');
      d.setAttribute('aria-label', `Slide ${i + 1}`);
      d.addEventListener('click', () => goTo(i));
      dotsWrap.appendChild(d);
    });

    function updateDots(index) {
      dotsWrap.querySelectorAll('.hero-dot').forEach((d, i) =>
        d.classList.toggle('active', i === index)
      );
    }

    function goTo(idx) {
      cur = (idx + total) % total;                          // wrap-around
      slidesEl.style.transform = `translateX(-${cur * 100}%)`;
      updateDots(cur);
    }

    // — Autoplay —
    function startAutoplay() {
      clearInterval(autoplayTimer);
      autoplayTimer = setInterval(() => {
        if (!drag) goTo(cur + 1);
      }, 4500);
    }

    startAutoplay();

    // — Touch swipe —
    hero.addEventListener('touchstart', e => {
      if (locked) return;
      sx   = e.touches[0].clientX;
      drag = true;
      clearInterval(autoplayTimer);      // pausa durante interação
    }, { passive: true });

    hero.addEventListener('touchend', e => {
      if (!drag || locked) return;
      const diff = sx - e.changedTouches[0].clientX;
      drag = false;
      if (Math.abs(diff) > 40) {
        goTo(diff > 0 ? cur + 1 : cur - 1);
        locked = true;
        setTimeout(() => { locked = false; }, 350);
      }
      startAutoplay();                   // retoma após interação
    }, { passive: true });

  })();

    /* ══════════════════════════════
     SYNC bottom-panel height → CSS var
  ══════════════════════════════ */
  function syncBottom() {
    const panel = document.getElementById('bottomPanel');
    if (!panel) return;
    document.documentElement.style.setProperty('--bottom-h', panel.offsetHeight + 'px');
  }
  syncBottom();
  window.addEventListener('resize', syncBottom, { passive: true });

})();