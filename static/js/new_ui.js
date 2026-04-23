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
      if (!sidebar.classList.contains('expanded')) { openSB(); return; }
      const item   = row.closest('.sb-item');
      const isOpen = item.classList.contains('open');
      sidebar.querySelectorAll('.sb-item.open').forEach(el => el.classList.remove('open'));
      if (!isOpen) item.classList.add('open');
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

/* ═══════════════════════════════
   SWIPE GESTURE - SIDEBAR (CORRIGIDO)
═══════════════════════════════ */
(function() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sbOverlay');
  
  let touchStartX = 0;
  let touchEndX = 0;
  let touchStartY = 0;
  let touchEndY = 0;
  let isSwiping = false;
  
  const MIN_SWIPE_DISTANCE = 60;
  const EDGE_ZONE = 40;
  const SIDEBAR_COLLAPSED = 50;
  const SIDEBAR_EXPANDED = 160;
  
  // ✅ detecta início do toque
  document.addEventListener('touchstart', (e) => {
    touchStartX = e.touches[0].clientX;
    touchStartY = e.touches[0].clientY;
    
    const isSidebarOpen = sidebar.classList.contains('expanded');
    const isEdgeTouch = touchStartX <= EDGE_ZONE;
    
    if (isEdgeTouch || isSidebarOpen) {
      isSwiping = true;
      // ✅ desativa transição pra seguir o dedo
      sidebar.style.transition = 'none';
      sidebar.style.willChange = 'width';
    }
  }, { passive: true });
  
  // ✅ FEEDBACK VISUAL - ajusta WIDTH
  document.addEventListener('touchmove', (e) => {
    if (!isSwiping) return;
    
    touchEndX = e.touches[0].clientX;
    touchEndY = e.touches[0].clientY;
    
    const deltaX = touchEndX - touchStartX;
    const deltaY = Math.abs(touchEndY - touchStartY);
    const isSidebarOpen = sidebar.classList.contains('expanded');
    
    // ignora movimento vertical (scroll)
    if (deltaY > Math.abs(deltaX) * 1.5) {
      isSwiping = false;
      sidebar.style.transition = '';
      sidebar.style.willChange = '';
      return;
    }
    
    // ✅ ABRINDO - arrasta da esquerda
    if (!isSidebarOpen && deltaX > 0) {
      const newWidth = Math.min(SIDEBAR_COLLAPSED + deltaX, SIDEBAR_EXPANDED);
      sidebar.style.width = `${newWidth}px`;
      
      // mostra overlay gradualmente
      const progress = (newWidth - SIDEBAR_COLLAPSED) / (SIDEBAR_EXPANDED - SIDEBAR_COLLAPSED);
      overlay.style.opacity = progress * 0.32;
      
      if (deltaX > 20) {
        overlay.classList.add('visible');
      }
    }
    
    // ✅ FECHANDO - arrasta pra esquerda
    if (isSidebarOpen && deltaX < 0) {
      const newWidth = Math.max(SIDEBAR_EXPANDED + deltaX, SIDEBAR_COLLAPSED);
      sidebar.style.width = `${newWidth}px`;
      
      // esconde overlay gradualmente
      const progress = (newWidth - SIDEBAR_COLLAPSED) / (SIDEBAR_EXPANDED - SIDEBAR_COLLAPSED);
      overlay.style.opacity = progress * 0.32;
    }
    
  }, { passive: true });
  
  // ✅ detecta fim do toque
  document.addEventListener('touchend', (e) => {
    if (!isSwiping) return;
    
    const deltaX = touchEndX - touchStartX;
    const deltaY = Math.abs(touchEndY - touchStartY);
    const isSidebarOpen = sidebar.classList.contains('expanded');
    
    // ✅ restaura comportamento normal
    sidebar.style.transition = '';
    sidebar.style.width = '';
    sidebar.style.willChange = '';
    overlay.style.opacity = '';
    
    // ignora se foi scroll vertical
    if (deltaY > Math.abs(deltaX) * 1.5) {
      isSwiping = false;
      if (!isSidebarOpen) {
        overlay.classList.remove('visible');
      }
      return;
    }
    
    // ✅ decide ação baseado na distância
    if (deltaX > MIN_SWIPE_DISTANCE && !isSidebarOpen) {
      // abrir
      sidebar.classList.add('expanded');
      overlay.classList.add('visible');
    } else if (deltaX < -MIN_SWIPE_DISTANCE && isSidebarOpen) {
      // fechar
      sidebar.classList.remove('expanded');
      overlay.classList.remove('visible');
    } else {
      // não atingiu mínimo, volta ao estado anterior
      if (!isSidebarOpen) {
        overlay.classList.remove('visible');
      }
    }
    
    isSwiping = false;
    touchStartX = 0;
    touchEndX = 0;
  }, { passive: true });
  
})();