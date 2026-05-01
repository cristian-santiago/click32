/* =============================================
   notification_modal.js — Click32
   Modal de notificações com dados reais
   ============================================= */

(function () {
  'use strict';

  /* ── Referências ── */
  const overlay    = document.getElementById('notifOverlay');
  const modal      = document.getElementById('notifModal');
  const closeBtn   = document.getElementById('notifClose');
  const markAllBtn = document.getElementById('notifMarkAll');
  const navTrigger = document.querySelector('[data-tab="notifications"]');
  const list       = document.getElementById('notifList');
  const navDot     = document.querySelector('[data-tab="notifications"] .nav-dot');

  if (!overlay || !modal) {
    console.warn('[Click32] notification_modal: elementos não encontrados.');
    return;
  }

  /* ── Constantes ── */
  const API_URL     = '/api/notificacoes/';
  const STORAGE_KEY = 'click32_notif_vistas';

  /* ── Estado ── */
  let isOpen   = false;
  let startY   = null;
  let currentY = 0;

  /* ── LocalStorage: IDs já vistos ── */
  function getVistas() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    } catch {
      return [];
    }
  }

  function salvaVistas(ids) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(ids));
    } catch {}
  }

  function marcarComoVista(id) {
    const vistas = getVistas();
    if (!vistas.includes(id)) {
      vistas.push(id);
      salvaVistas(vistas);
    }
  }

  function todasVistas(ids) {
    const vistas = getVistas();
    ids.forEach(id => {
      if (!vistas.includes(id)) vistas.push(id);
    });
    salvaVistas(vistas);
  }

  /* ── Cores por badge ── */
  const BADGE_COLORS = {
    novo:     { bg: 'linear-gradient(135deg,#1a56f0,#1240c7)' },
    encarte:  { bg: 'linear-gradient(135deg,#a855f7,#ec4899)' },
    contato:  { bg: 'linear-gradient(135deg,#10b981,#059669)' },
    social:   { bg: 'linear-gradient(135deg,#f6a823,#f05c22)' },
    delivery: { bg: 'linear-gradient(135deg,#ef4444,#dc2626)' },
    local:    { bg: 'linear-gradient(135deg,#06b6d4,#3b82f6)' },
    info:     { bg: 'linear-gradient(135deg,#6b7280,#374151)' },
  };

  /* ── Renderiza um item da lista ── */
  function renderItem(notif, vistas) {
    const isNova      = !vistas.includes(notif.id);
    const cores       = BADGE_COLORS[notif.badge] || BADGE_COLORS.info;
    const itemExtra   = isNova ? ' notif-item--unread' : '';

    // Live: anel aparece em qualquer notificação não vista
    const avatarExtra = isNova ? ' notif-avatar--live' : '';

    // Avatar: imagem da loja se disponível, senão inicial
    const avatarInner = notif.avatar_url
      ? `<img src="${notif.avatar_url}" alt="${notif.store_name}" class="notif-avatar-img">`
      : `<span class="notif-avatar-letter">${notif.inicial}</span>`;

    // Dot azul só para não vistas
    const dotHtml = isNova
      ? `<div class="notif-unread-dot" aria-hidden="true"></div>`
      : '';

    return `
      <li class="notif-item${itemExtra}"
          role="listitem"
          data-id="${notif.id}"
          data-slug="${notif.store_slug}">
        <div class="notif-avatar-wrap">
          <div class="notif-avatar${avatarExtra}"
               style="background:${cores.bg}">
            ${avatarInner}
          </div>
        </div>
        <div class="notif-content">
          <p class="notif-text">
            <strong>${notif.store_name}</strong> ${notif.texto}
          </p>
          <time class="notif-time" datetime="${notif.criada_em}">
            ${notif.tempo}
          </time>
        </div>
        ${dotHtml}
      </li>`;
  }

  /* ── Estado vazio ── */
  function renderVazio() {
    return `
      <li class="notif-empty" role="listitem">
        <span class="notif-empty-icon">🔔</span>
        <p>Nenhuma novidade por agora.</p>
        <small>Volte em breve!</small>
      </li>`;
  }

  /* ── Estado de erro ── */
  function renderErro() {
    return `
      <li class="notif-empty" role="listitem">
        <span class="notif-empty-icon">⚠️</span>
        <p>Não foi possível carregar.</p>
        <small>Tente novamente em instantes.</small>
      </li>`;
  }

  /* ── Atualiza o nav dot ── */
  function atualizaNavDot(notificacoes, vistas) {
    if (!navDot) return;
    const temNova = notificacoes.some(n => !vistas.includes(n.id));
    navDot.style.opacity    = temNova ? '1' : '0';
    navDot.style.transition = 'opacity 0.3s';
  }

  /* ── Busca e renderiza ── */
  async function carregaNotificacoes() {
    list.innerHTML = `
      <li class="notif-loading" role="listitem">
        <span class="notif-loading-dot"></span>
        <span class="notif-loading-dot"></span>
        <span class="notif-loading-dot"></span>
      </li>`;

    try {
      const res  = await fetch(API_URL);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      const notificacoes = data.notificacoes || [];
      const vistas       = getVistas();

      // Limpa IDs obsoletos do localStorage
      const idsAtivos = notificacoes.map(n => n.id);
      salvaVistas(vistas.filter(id => idsAtivos.includes(id)));

      atualizaNavDot(notificacoes, getVistas());

      if (notificacoes.length === 0) {
        list.innerHTML = renderVazio();
        return;
      }

      list.innerHTML = notificacoes
        .map(n => renderItem(n, getVistas()))
        .join('');

    } catch (err) {
      console.error('[Click32] Erro ao carregar notificações:', err);
      list.innerHTML = renderErro();
    }
  }

  /* ── Abrir ── */
  function openNotificationModal() {
    isOpen = true;
    overlay.classList.add('notif-overlay--visible');
    overlay.removeAttribute('aria-hidden');
    modal.classList.add('notif-modal--open');
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    closeBtn.focus();
    carregaNotificacoes();
  }

  /* ── Fechar ── */
  function closeNotificationModal() {
    if (!isOpen) return;
    isOpen = false;
    overlay.classList.remove('notif-overlay--visible');
    overlay.setAttribute('aria-hidden', 'true');
    modal.classList.remove('notif-modal--open');
    modal.setAttribute('aria-hidden', 'true');
    modal.style.transform = '';
    document.body.style.overflow = '';
    if (navTrigger) navTrigger.focus();
  }

  /* ── Marcar todas como visto ── */
  function markAllRead() {
    const items = list.querySelectorAll('.notif-item');
    const ids   = [];

    items.forEach(item => {
      const id = parseInt(item.dataset.id);
      if (id) ids.push(id);

      item.classList.remove('notif-item--unread');

      // Remove anel live
      const avatar = item.querySelector('.notif-avatar');
      if (avatar) avatar.classList.remove('notif-avatar--live');

      // Remove dot
      const dot = item.querySelector('.notif-unread-dot');
      if (dot) {
        dot.style.opacity    = '0';
        dot.style.transition = 'opacity 0.3s';
        setTimeout(() => dot.remove(), 300);
      }
    });

    todasVistas(ids);
    atualizaNavDot([], []);

    markAllBtn.textContent = 'Tudo visto ✓';
    markAllBtn.style.color = '#059669';
    setTimeout(() => {
      markAllBtn.textContent = 'Marcar como visto';
      markAllBtn.style.color = '';
    }, 2000);
  }

  /* ── Clique num item → navega para a loja ── */
  function onItemClick(e) {
    const item = e.target.closest('.notif-item');
    if (!item || !item.dataset.slug) return;

    const id   = parseInt(item.dataset.id);
    const slug = item.dataset.slug;

    // Marca como visto
    if (id) marcarComoVista(id);
    item.classList.remove('notif-item--unread');

    // Remove anel live
    const avatar = item.querySelector('.notif-avatar');
    if (avatar) avatar.classList.remove('notif-avatar--live');

    // Remove dot
    const dot = item.querySelector('.notif-unread-dot');
    if (dot) {
      dot.style.opacity    = '0';
      dot.style.transition = 'opacity 0.25s';
      setTimeout(() => dot.remove(), 250);
    }

    // Navega após fechar o modal
    setTimeout(() => {
      closeNotificationModal();
      window.location.href = `/${slug}/`;
    }, 180);
  }

  /* ── Drag to dismiss (touch) ── */
  function onTouchStart(e) {
    startY = e.touches[0].clientY;
    modal.style.transition = 'none';
  }

  function onTouchMove(e) {
    if (startY === null) return;
    const delta = e.touches[0].clientY - startY;
    if (delta < 0) return;
    currentY = delta;
    modal.style.transform = `translateX(-50%) translateY(${delta}px)`;
  }

  function onTouchEnd() {
    modal.style.transition = '';
    if (currentY > 120) {
      closeNotificationModal();
    } else {
      modal.style.transform = 'translateX(-50%) translateY(0)';
    }
    startY   = null;
    currentY = 0;
  }

  /* ── Verifica nav dot ao carregar a página ── */
  async function verificaNavDotInicial() {
    try {
      const res  = await fetch(API_URL);
      if (!res.ok) return;
      const data = await res.json();
      const notificacoes = data.notificacoes || [];
      const vistas       = getVistas();

      // Limpa obsoletos
      const idsAtivos = notificacoes.map(n => n.id);
      salvaVistas(vistas.filter(id => idsAtivos.includes(id)));

      atualizaNavDot(notificacoes, getVistas());
    } catch {
      // Silencioso
    }
  }

  /* ── Eventos ── */
  if (navTrigger) {
    navTrigger.addEventListener('click', () => {
      isOpen ? closeNotificationModal() : openNotificationModal();
    });
  }

  overlay.addEventListener('click', closeNotificationModal);
  closeBtn.addEventListener('click', closeNotificationModal);

  if (markAllBtn) markAllBtn.addEventListener('click', markAllRead);

  modal.addEventListener('touchstart', onTouchStart, { passive: true });
  modal.addEventListener('touchmove',  onTouchMove,  { passive: true });
  modal.addEventListener('touchend',   onTouchEnd);

  if (list) list.addEventListener('click', onItemClick);

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && isOpen) closeNotificationModal();
  });

  /* ── Inicialização ── */
  verificaNavDotInicial();

  /* ── API pública ── */
  window.openNotificationModal  = openNotificationModal;
  window.closeNotificationModal = closeNotificationModal;

})();