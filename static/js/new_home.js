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
      const item     = row.closest('.sb-item');
      const isOpen   = item.classList.contains('open');
      const wasCollapsed = !sidebar.classList.contains('expanded');

      if (wasCollapsed) openSB();

      // fecha todos — reseta max-height dos abertos
      sidebar.querySelectorAll('.sb-item.open').forEach(el => {
        el.classList.remove('open');
        el.querySelector('.sb-dropdown').style.maxHeight = '0';
      });

      // abre o clicado com altura real
      if (!isOpen) {
        item.classList.add('open');
        const drop = item.querySelector('.sb-dropdown');
        drop.style.maxHeight = drop.scrollHeight + 'px';
      }
    });
  });

  /* ══════════════════════════════
     VIP CAROUSEL
  ══════════════════════════════ */
  const vipSlides   = document.getElementById('vipSlides');
  const vipDotsWrap = document.getElementById('vipDots');

  if (vipSlides) {
    const slides = vipSlides.querySelectorAll('.vip-slide');
    const total  = slides.length;
    let cur = 0, sx = 0, drag = false, locked = false;
    let timer;

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
     TAG PILLS
  ══════════════════════════════ */
  const pills = document.querySelectorAll('.tag-pill');
  pills.forEach(pill => {
    pill.addEventListener('click', () => {
      pills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
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