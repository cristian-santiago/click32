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
}

toggle.addEventListener('click', () =>
  sidebar.classList.contains('expanded') ? closeSB() : openSB()
);
overlay.addEventListener('click', closeSB);

// Função para remover todas as classes active e open
function resetAllSidebarStates() {
  // Remove todos os 'open' dos dropdowns
  sidebar.querySelectorAll('.sb-item.open').forEach(el => {
    el.classList.remove('open');
    const drop = el.querySelector('.sb-dropdown');
    if (drop) drop.style.maxHeight = '0';
  });
  
  // Remove todos os 'active' dos links
  sidebar.querySelectorAll('.sb-row.active, .sb-dropdown a.active').forEach(el => {
    el.classList.remove('active');
  });
}

sidebar.querySelectorAll('.sb-row[role="button"]').forEach(row => {
  row.addEventListener('click', (e) => {
    const item = row.closest('.sb-item');
    const isExpanded = sidebar.classList.contains('expanded');
    const isOpen = item.classList.contains('open');
    const filterUrl = row.dataset.filterUrl;

    // COLAPSADO: filtra pela categoria
    if (!isExpanded && filterUrl) {
      window.location.href = filterUrl;
      return;
    }

    // EXPANDIDO: toggle dropdown
    if (isExpanded) {
      // Se clicou em um item que tem dropdown
      if (item.querySelector('.sb-dropdown')) {
        // Fecha todos os outros dropdowns E remove os active deles
        sidebar.querySelectorAll('.sb-item.open').forEach(el => {
          if (el !== item) {
            el.classList.remove('open');
            const drop = el.querySelector('.sb-dropdown');
            if (drop) drop.style.maxHeight = '0';
            
            // Remove active da categoria pai
            const parentRow = el.querySelector('.sb-row');
            if (parentRow) parentRow.classList.remove('active');
          }
        });

        // Toggle do dropdown clicado
        if (!isOpen) {
          item.classList.add('open');
          const drop = item.querySelector('.sb-dropdown');
          if (drop) drop.style.maxHeight = drop.scrollHeight + 'px';
          
          // Adiciona active apenas se tiver dropdown e estiver abrindo
          row.classList.add('active');
        } else {
          item.classList.remove('open');
          const drop = item.querySelector('.sb-dropdown');
          if (drop) drop.style.maxHeight = '0';
          row.classList.remove('active');
        }
      } else {
        // É um item sem dropdown (categoria sem tags)
        // Reseta tudo e redireciona
        resetAllSidebarStates();
        
        // Marca este item como active
        row.classList.add('active');
        
        // Redireciona para a URL da categoria
        if (filterUrl) {
          window.location.href = filterUrl;
        }
      }
    }
  });
});

// Fecha sidebar e reseta estados ao clicar em tag
sidebar.querySelectorAll('.sb-dropdown a').forEach(link => {
  link.addEventListener('click', (e) => {
    // Remove active de todos os dropdown items
    sidebar.querySelectorAll('.sb-dropdown a.active').forEach(el => {
      el.classList.remove('active');
    });
    
    // Adiciona active no link clicado
    link.classList.add('active');
    
    // Remove active da categoria pai (pois a tag filha foi clicada)
    const parentItem = link.closest('.sb-item');
    if (parentItem) {
      const parentRow = parentItem.querySelector('.sb-row');
      if (parentRow) parentRow.classList.remove('active');
    }
    
    // Fecha o sidebar após clicar (com um pequeno delay para ver o feedback visual)
    setTimeout(() => {
      closeSB();
    }, 150);
  });
});

// Função para marcar o item ativo baseado na URL atual
function setActiveFromURL() {
  const currentUrl = window.location.href;
  const urlParams = new URLSearchParams(window.location.search);
  const currentTag = urlParams.get('tag');
  
  if (!currentTag) return;
  
  // Procura por categoria ou tag que corresponde ao parâmetro
  sidebar.querySelectorAll('.sb-row, .sb-dropdown a').forEach(el => {
    const href = el.getAttribute('href');
    if (href && href.includes(`?tag=${encodeURIComponent(currentTag)}`)) {
      el.classList.add('active');
      
      // Se for um item de dropdown, abre o pai
      if (el.closest('.sb-dropdown')) {
        const parentItem = el.closest('.sb-item');
        if (parentItem && !parentItem.classList.contains('open')) {
          parentItem.classList.add('open');
          const drop = parentItem.querySelector('.sb-dropdown');
          if (drop) drop.style.maxHeight = drop.scrollHeight + 'px';
          
          // Marca o pai como active também
          const parentRow = parentItem.querySelector('.sb-row');
          if (parentRow) parentRow.classList.add('active');
        }
      }
    }
  });
}

// Executa ao carregar a página
document.addEventListener('DOMContentLoaded', () => {
  setActiveFromURL();
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