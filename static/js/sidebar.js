// sidebar.js - Componente independente
(function() {
  'use strict';

  const sidebar = document.getElementById('sidebar');
  const toggle  = document.getElementById('sbToggle');
  const overlay = document.getElementById('sbOverlay');

  if (!sidebar || !toggle) return;

  function openSB() {
    sidebar.classList.add('expanded');
    if (overlay) overlay.classList.add('visible');
  }
  
  function closeSB() {
    sidebar.classList.remove('expanded');
    if (overlay) overlay.classList.remove('visible');
  }

  toggle.addEventListener('click', () =>
    sidebar.classList.contains('expanded') ? closeSB() : openSB()
  );
  
  if (overlay) {
    overlay.addEventListener('click', closeSB);
  }

  // Função para remover todas as classes active e open
  function resetAllSidebarStates() {
    sidebar.querySelectorAll('.sb-item.open').forEach(el => {
      el.classList.remove('open');
      const drop = el.querySelector('.sb-dropdown');
      if (drop) drop.style.maxHeight = '0';
    });
    sidebar.querySelectorAll('.sb-row.active, .sb-dropdown a.active').forEach(el => {
      el.classList.remove('active');
    });
  }

  // Clique nos items com dropdown
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
        // Se tem dropdown
        if (item.querySelector('.sb-dropdown')) {
          // Fecha todos os outros dropdowns
          sidebar.querySelectorAll('.sb-item.open').forEach(el => {
            if (el !== item) {
              el.classList.remove('open');
              const drop = el.querySelector('.sb-dropdown');
              if (drop) drop.style.maxHeight = '0';
              const parentRow = el.querySelector('.sb-row');
              if (parentRow) parentRow.classList.remove('active');
            }
          });

          // Toggle do dropdown clicado
          if (!isOpen) {
            item.classList.add('open');
            const drop = item.querySelector('.sb-dropdown');
            if (drop) drop.style.maxHeight = drop.scrollHeight + 'px';
            row.classList.add('active');
          } else {
            item.classList.remove('open');
            const drop = item.querySelector('.sb-dropdown');
            if (drop) drop.style.maxHeight = '0';
            row.classList.remove('active');
          }
        } else {
          // Sem dropdown: reseta e redireciona
          resetAllSidebarStates();
          row.classList.add('active');
          if (filterUrl) {
            window.location.href = filterUrl;
          }
        }
      }
    });
  });

  // Fecha sidebar ao clicar em tag (dropdown item)
  sidebar.querySelectorAll('.sb-dropdown a').forEach(link => {
    link.addEventListener('click', (e) => {
      // Marca o link como active
      sidebar.querySelectorAll('.sb-dropdown a.active').forEach(el => {
        el.classList.remove('active');
      });
      link.classList.add('active');
      
      // Remove active da categoria pai
      const parentItem = link.closest('.sb-item');
      if (parentItem) {
        const parentRow = parentItem.querySelector('.sb-row');
        if (parentRow) parentRow.classList.remove('active');
      }
      
      // Fecha o sidebar após clicar
      setTimeout(() => {
        closeSB();
      }, 150);
    });
  });

  // Marca o item ativo baseado na URL atual
  function setActiveFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    const currentTag = urlParams.get('tag');
    
    if (!currentTag) return;
    
    sidebar.querySelectorAll('.sb-row, .sb-dropdown a').forEach(el => {
      const href = el.getAttribute('href');
      if (href && href.includes(`?tag=${encodeURIComponent(currentTag)}`)) {
        el.classList.add('active');
        
        // Se for item de dropdown, abre o pai
        if (el.closest('.sb-dropdown')) {
          const parentItem = el.closest('.sb-item');
          if (parentItem && !parentItem.classList.contains('open')) {
            parentItem.classList.add('open');
            const drop = parentItem.querySelector('.sb-dropdown');
            if (drop) drop.style.maxHeight = drop.scrollHeight + 'px';
            const parentRow = parentItem.querySelector('.sb-row');
            if (parentRow) parentRow.classList.add('active');
          }
        }
      }
    });
  }

  setActiveFromURL();
})();