(function () {

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
     POPUP MENU
  ══════════════════════════════ */
  const btnMais   = document.getElementById('btnMais');
  const popupMenu = document.getElementById('popupMenu');

  btnMais.addEventListener('click', (e) => {
    e.stopPropagation();
    const isOpen = popupMenu.classList.contains('open');
    popupMenu.classList.toggle('open', !isOpen);
    btnMais.classList.toggle('active', !isOpen);
  });

  document.addEventListener('click', (e) => {
    if (!popupMenu.contains(e.target) && e.target !== btnMais) {
      popupMenu.classList.remove('open');
      btnMais.classList.remove('active');
    }
  });

  document.querySelectorAll('.popup-item[data-action]').forEach(item => {
    item.addEventListener('click', () => {
      const action = item.dataset.action;
      popupMenu.classList.remove('open');
      btnMais.classList.remove('active');
      if (action === 'faq')     console.log('→ FAQ');
      if (action === 'anuncio') console.log('→ Anúncio');
      if (action === 'about')   console.log('→ Sobre');
    });
  });

  /* ══════════════════════════════
     CAROUSEL
  ══════════════════════════════ */
  const slides   = document.getElementById('heroSlides');
  const dotsWrap = document.getElementById('heroDots');
  const items    = slides.querySelectorAll('.hero-slide');
  let cur = 0, sx = 0, drag = false, locked = false;

  items.forEach((_, i) => {
    const d = document.createElement('div');
    d.className = 'hero-dot' + (i === 0 ? ' active' : '');
    d.addEventListener('click', () => goTo(i));
    dotsWrap.appendChild(d);
  });

  function goTo(idx) {
    cur = Math.max(0, Math.min(idx, items.length - 1));
    slides.style.transform = `translateX(-${cur * 100}%)`;
    dotsWrap.querySelectorAll('.hero-dot').forEach((d, i) =>
      d.classList.toggle('active', i === cur)
    );
  }

  const hero = document.getElementById('hero');
  hero.addEventListener('touchstart', e => {
    if (locked) return;
    sx = e.touches[0].clientX; drag = true;
  }, { passive: true });
  hero.addEventListener('touchend', e => {
    if (!drag || locked) return;
    const diff = sx - e.changedTouches[0].clientX;
    drag = false;
    if (Math.abs(diff) > 40) {
      goTo(diff > 0 ? cur + 1 : cur - 1);
      locked = true; setTimeout(() => locked = false, 350);
    }
  }, { passive: true });

  setInterval(() => { if (!drag) goTo((cur + 1) % items.length); }, 4500);

  /* ══════════════════════════════
     SHARE
  ══════════════════════════════ */
  document.getElementById('shareBtn').addEventListener('click', () => {
    navigator.share
      ? navigator.share({ title: 'Pedro Pintura & Reformas', url: location.href })
      : prompt('Copie o link:', location.href);
  });

  /* ══════════════════════════════
     SYNC bottom-panel height
  ══════════════════════════════ */
  function syncBottom() {
    const h = document.getElementById('bottomPanel').offsetHeight;
    document.documentElement.style.setProperty('--bottom-h', h + 'px');
  }
  syncBottom();
  window.addEventListener('resize', syncBottom);

})();

