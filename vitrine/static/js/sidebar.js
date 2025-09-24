/* Inicialização da URL base */
const homeUrl = window.homeUrl || "/";

/* Configuração inicial do evento DOMContentLoaded */
document.addEventListener('DOMContentLoaded', () => {
  const sidebar = document.getElementById('sidebar');
  const toggleBtn = document.getElementById('toggleBtn');
  const overlay = document.getElementById('overlay');
  const isMobile = window.innerWidth <= 768;
  const isExpanded = localStorage.getItem('sidebar-expanded') === 'true';

  if (!sidebar || !toggleBtn || !overlay) {
    return;
  }

  if (!isMobile && isExpanded) {
    sidebar.classList.remove('collapsed');
    overlay.style.display = 'block';
  } else {
    sidebar.classList.add('collapsed');
    overlay.style.display = 'none';
  }

  const lastOpenDropdown = localStorage.getItem('sidebar-last-dropdown');
  if (lastOpenDropdown && !sidebar.classList.contains('collapsed')) {
    openDropdown(lastOpenDropdown);
  }

  /* Evento de clique no botão de alternância */
  toggleBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    e.preventDefault();
    sidebar.classList.toggle('collapsed');
    const isNowExpanded = !sidebar.classList.contains('collapsed');
    localStorage.setItem('sidebar-expanded', isNowExpanded);
    overlay.style.display = isNowExpanded ? 'block' : 'none';

    if (isNowExpanded) {
      const lastOpenDropdown = localStorage.getItem('sidebar-last-dropdown');
      if (lastOpenDropdown) {
        openDropdown(lastOpenDropdown);
      }
    }
  });

  /* Evento de clique no overlay */
  overlay.addEventListener('click', () => {
    collapseSidebar();
    document.querySelectorAll('.dropdown').forEach(d => d.classList.remove('open'));
  });

  /* Evento de clique nos cabeçalhos do menu */
  document.querySelectorAll('.menu-header').forEach(header => {
    header.addEventListener('click', (e) => {
      const group = header.getAttribute('data-dropdown');
      if (!group) {
        return;
      }

      if (sidebar.classList.contains('collapsed')) {
        e.preventDefault();
        e.stopPropagation();
        localStorage.setItem('sidebar-last-dropdown', group);
        // Uses homeUrl for redirection
        window.location.href = homeUrl + '?tag=' + encodeURIComponent(group);
      } else {
        const dropdown = header.nextElementSibling;
        const isOpen = dropdown.classList.contains('open');
        document.querySelectorAll('.dropdown').forEach(d => d.classList.remove('open'));
        if (!isOpen) {
          dropdown.classList.add('open');
          localStorage.setItem('sidebar-last-dropdown', group);
        } else {
          localStorage.removeItem('sidebar-last-dropdown');
        }
      }
    });
  });

  /* Evento de clique nos itens do dropdown */
  document.querySelectorAll('.dropdown-item').forEach(item => {
    item.addEventListener('click', (e) => {
      e.stopPropagation();
      const dropdown = item.closest('.dropdown');
      if (!dropdown) {
        return;
      }
      const header = dropdown.previousElementSibling;
      if (!header) {
        return;
      }
      const group = header.getAttribute('data-dropdown');
      if (!group) {
        return;
      }
      localStorage.setItem('sidebar-last-dropdown', group);
      collapseSidebar();
    });
  });

  /* Evento de clique fora da sidebar em dispositivos móveis */
  document.addEventListener('click', (e) => {
    if (isMobile && !sidebar.contains(e.target) && e.target !== toggleBtn && !toggleBtn.contains(e.target) && !e.target.closest('.menu-header')) {
      collapseSidebar();
      document.querySelectorAll('.dropdown').forEach(d => d.classList.remove('open'));
    }
  });
});

/* Função para abrir um dropdown */
function openDropdown(group) {
  const escapedGroup = CSS.escape(group);
  const target = document.querySelector(`[data-dropdown="${escapedGroup}"]`);
  if (target) {
    document.querySelectorAll('.dropdown').forEach(d => d.classList.remove('open'));
    target.nextElementSibling.classList.add('open');
  }
}

/* Função para colapsar a sidebar */
function collapseSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('overlay');
  sidebar.classList.add('collapsed');
  overlay.style.display = 'none';
  localStorage.setItem('sidebar-expanded', 'false');
}

/* Função para controlar o bloqueio de scroll */
function shouldBlockScroll(el, deltaY) {
  const scrollTop = el.scrollTop;
  const scrollHeight = el.scrollHeight;
  const clientHeight = el.clientHeight;

  const isScrollingDown = deltaY > 0;
  const isScrollingUp = deltaY < 0;

  const atTop = scrollTop === 0;
  const atBottom = scrollTop + clientHeight >= scrollHeight;

  return (isScrollingDown && atBottom) || (isScrollingUp && atTop);
}

/* Configuração de eventos de scroll no menu */
const scrollContainer = document.querySelector('.menu');

if (scrollContainer) {
  // Mouse scroll
  scrollContainer.addEventListener('wheel', function(e) {
    if (shouldBlockScroll(this, e.deltaY)) {
      e.preventDefault();
    }
  }, { passive: false });

  // Touch scroll
  let touchStartY = 0;
  scrollContainer.addEventListener('touchstart', function(e) {
    touchStartY = e.touches[0].clientY;
  }, { passive: true });

  scrollContainer.addEventListener('touchmove', function(e) {
    const currentY = e.touches[0].clientY;
    const deltaY = touchStartY - currentY;

    if (shouldBlockScroll(this, deltaY)) {
      e.preventDefault();
    }
  }, { passive: false });
}