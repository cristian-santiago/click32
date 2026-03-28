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
     SWIPE GESTURE — SIDEBAR
  ══════════════════════════════ */
  let touchStartX = 0, touchEndX = 0, touchStartY = 0, touchEndY = 0;
  let isSwiping   = false;
  const MIN_SWIPE = 60, EDGE_ZONE = 40;
  const SB_COLL   = 50, SB_EXP = 160;

  document.addEventListener('touchstart', e => {
    touchStartX = e.touches[0].clientX;
    touchStartY = e.touches[0].clientY;
    const isOpen = sidebar.classList.contains('expanded');
    if (touchStartX <= EDGE_ZONE || isOpen) {
      isSwiping = true;
      sidebar.style.transition = 'none';
      sidebar.style.willChange  = 'width';
    }
  }, { passive: true });

  document.addEventListener('touchmove', e => {
    if (!isSwiping) return;
    touchEndX = e.touches[0].clientX;
    touchEndY = e.touches[0].clientY;
    const dX     = touchEndX - touchStartX;
    const dY     = Math.abs(touchEndY - touchStartY);
    const isOpen = sidebar.classList.contains('expanded');

    if (dY > Math.abs(dX) * 1.5) {
      isSwiping = false;
      sidebar.style.transition = '';
      sidebar.style.willChange  = '';
      return;
    }
    if (!isOpen && dX > 0) {
      const w = Math.min(SB_COLL + dX, SB_EXP);
      sidebar.style.width = `${w}px`;
      const p = (w - SB_COLL) / (SB_EXP - SB_COLL);
      overlay.style.opacity = p * 0.32;
      if (dX > 20) overlay.classList.add('visible');
    }
    if (isOpen && dX < 0) {
      const w = Math.max(SB_EXP + dX, SB_COLL);
      sidebar.style.width = `${w}px`;
      const p = (w - SB_COLL) / (SB_EXP - SB_COLL);
      overlay.style.opacity = p * 0.32;
    }
  }, { passive: true });

  document.addEventListener('touchend', () => {
    if (!isSwiping) return;
    const dX     = touchEndX - touchStartX;
    const dY     = Math.abs(touchEndY - touchStartY);
    const isOpen = sidebar.classList.contains('expanded');

    sidebar.style.transition = '';
    sidebar.style.width      = '';
    sidebar.style.willChange  = '';
    overlay.style.opacity    = '';

    if (dY > Math.abs(dX) * 1.5) {
      isSwiping = false;
      if (!isOpen) overlay.classList.remove('visible');
      return;
    }
    if (dX > MIN_SWIPE && !isOpen)  { openSB(); }
    else if (dX < -MIN_SWIPE && isOpen) { closeSB(); }
    else { if (!isOpen) overlay.classList.remove('visible'); }

    isSwiping = false;
    touchStartX = touchEndX = 0;
  }, { passive: true });

  /* ══════════════════════════════
     VIP CAROUSEL
  ══════════════════════════════ */
  const vipSlides  = document.getElementById('vipSlides');
  const vipDotsWrap = document.getElementById('vipDots');

  if (vipSlides) {
    const slides = vipSlides.querySelectorAll('.vip-slide');
    const total  = slides.length;
    let   cur    = 0, sx = 0, drag = false, locked = false;
    let   timer;

    // criar dots
    slides.forEach((_, i) => {
      const d = document.createElement('div');
      d.className = 'vip-dot' + (i === 0 ? ' active' : '');
      d.addEventListener('click', () => goTo(i));
      vipDotsWrap.appendChild(d);
    });

    function goTo(idx) {
      cur = (idx + total) % total;
      vipSlides.style.transform = `translateX(-${cur * 100}%)`;
      vipDotsWrap.querySelectorAll('.vip-dot').forEach((d, i) =>
        d.classList.toggle('active', i === cur)
      );
    }

    function startTimer() {
      clearInterval(timer);
      timer = setInterval(() => { if (!drag) goTo(cur + 1); }, 3200);
    }

    // touch no carousel
    const vipEl = vipSlides.closest('.vip-carousel');
    vipEl.addEventListener('touchstart', e => {
      if (locked) return;
      sx = e.touches[0].clientX;
      drag = true;
    }, { passive: true });
    vipEl.addEventListener('touchend', e => {
      if (!drag || locked) return;
      const diff = sx - e.changedTouches[0].clientX;
      drag = false;
      if (Math.abs(diff) > 40) {
        goTo(diff > 0 ? cur + 1 : cur - 1);
        locked = true;
        setTimeout(() => locked = false, 380);
        startTimer();
      }
    }, { passive: true });

    startTimer();
  }

  /* ══════════════════════════════
     TAG PILLS — filtro visual
     (sem dinamismo Django, só UI)
  ══════════════════════════════ */
  const pills = document.querySelectorAll('.tag-pill');
  pills.forEach(pill => {
    pill.addEventListener('click', () => {
      pills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      // Aqui pode-se adicionar lógica de filtro dinâmico futuramente
    });
  });

  /* ══════════════════════════════
     STORE COUNT
  ══════════════════════════════ */
  const feed  = document.getElementById('storeFeed');
  const count = document.getElementById('sectionCount');
  if (feed && count) {
    const n = feed.querySelectorAll('.store-card').length;
    if (n > 0) count.textContent = `${n} loja${n !== 1 ? 's' : ''}`;
  }

})();