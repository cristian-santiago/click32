/* =============================================
   notification_modal.js — Click32
   Controle do modal de notificações
   ============================================= */

(function () {
  'use strict';

  /* ── Referências ── */
  const overlay   = document.getElementById('notifOverlay');
  const modal     = document.getElementById('notifModal');
  const closeBtn  = document.getElementById('notifClose');
  const markAllBtn = document.getElementById('notifMarkAll');
  const navTrigger = document.querySelector('[data-tab="notifications"]');

  if (!overlay || !modal) {
    console.warn('[Click32] notification_modal: elementos não encontrados.');
    return;
  }

  /* ── Estado ── */
  let isOpen = false;
  let startY = null;
  let currentY = 0;

  /* ── Abrir ── */
  function openNotificationModal() {
    isOpen = true;
    overlay.classList.add('notif-overlay--visible');
    overlay.removeAttribute('aria-hidden');
    modal.classList.add('notif-modal--open');
    modal.removeAttribute('aria-hidden');
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';

    // Foco acessível no botão de fechar
    closeBtn.focus();
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

    // Devolve foco ao trigger
    if (navTrigger) navTrigger.focus();
  }

  /* ── Marcar todas como lidas ── */
  function markAllRead() {
    const unreadItems = modal.querySelectorAll('.notif-item--unread');
    const unreadDots  = modal.querySelectorAll('.notif-unread-dot');
    const navDot      = document.querySelector('[data-tab="notifications"] .nav-dot');

    unreadItems.forEach(item => {
      item.classList.remove('notif-item--unread');
    });

    unreadDots.forEach(dot => {
      dot.style.opacity = '0';
      dot.style.transition = 'opacity 0.3s';
      setTimeout(() => dot.remove(), 300);
    });

    // Apaga o dot do nav
    if (navDot) {
      navDot.style.opacity = '0';
      navDot.style.transition = 'opacity 0.3s';
    }

    // Feedback visual no botão
    markAllBtn.textContent = 'Marcar como visto';
    markAllBtn.style.background = '#e6f9f1';
    markAllBtn.style.color = '#059669';

    setTimeout(() => {
      markAllBtn.textContent = 'Marcar como visto';
      markAllBtn.style.background = '';
      markAllBtn.style.color = '';
    }, 2000);
  }

  /* ── Drag to dismiss (touch) ── */
  function onTouchStart(e) {
    startY = e.touches[0].clientY;
    modal.style.transition = 'none';
  }

  function onTouchMove(e) {
    if (startY === null) return;
    const delta = e.touches[0].clientY - startY;
    if (delta < 0) return; // bloqueia arrastar pra cima
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
    startY = null;
    currentY = 0;
  }

  /* ── Fechar ao clicar em item (mock de navegação) ── */
  function onItemClick(e) {
    const item = e.target.closest('.notif-item');
    if (!item) return;

    // Remove estado não lido do item clicado
    item.classList.remove('notif-item--unread');
    const dot = item.querySelector('.notif-unread-dot');
    if (dot) {
      dot.style.opacity = '0';
      dot.style.transition = 'opacity 0.25s';
      setTimeout(() => dot.remove(), 250);
    }

    // Fecha após curto delay (sensação de resposta)
    setTimeout(() => closeNotificationModal(), 180);
  }

  /* ── Eventos ── */
  // Trigger do nav
  if (navTrigger) {
    navTrigger.addEventListener('click', () => {
      isOpen ? closeNotificationModal() : openNotificationModal();
    });
  }

  // Fechar pelo overlay
  overlay.addEventListener('click', closeNotificationModal);

  // Fechar pelo botão / arrow
  closeBtn.addEventListener('click', closeNotificationModal);

  // Marcar todas como lidas
  if (markAllBtn) markAllBtn.addEventListener('click', markAllRead);

  // Drag to dismiss
  modal.addEventListener('touchstart', onTouchStart, { passive: true });
  modal.addEventListener('touchmove',  onTouchMove,  { passive: true });
  modal.addEventListener('touchend',   onTouchEnd);

  // Clique nos itens
  const list = document.getElementById('notifList');
  if (list) list.addEventListener('click', onItemClick);

  // Fechar com Escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && isOpen) closeNotificationModal();
  });

  /* ── API pública ── */
  window.openNotificationModal  = openNotificationModal;
  window.closeNotificationModal = closeNotificationModal;

})();