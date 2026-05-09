/* =============================================
   notificacoes.js — Click32
   Página completa de notificações (últimos 30 dias)
   ============================================= */

document.addEventListener('DOMContentLoaded', function () {
  'use strict';

  const API_URL    = '/api/notificacoes/?periodo=30';
  const STORAGE_KEY = 'click32_notif_vistas';
  const main       = document.getElementById('notifPageMain');
  const backBtn    = document.getElementById('notifPageBack');
  const markAllBtn = document.getElementById('notifPageMarkAll');

  if (!main) return;

  /* ── LocalStorage ── */
  function getVistas() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'); }
    catch { return []; }
  }

  function salvaVistas(ids) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(ids)); }
    catch {}
  }

  function marcarComoVista(id) {
    const vistas = getVistas();
    if (!vistas.includes(id)) { vistas.push(id); salvaVistas(vistas); }
  }

  function todasVistas(ids) {
    const vistas = getVistas();
    ids.forEach(id => { if (!vistas.includes(id)) vistas.push(id); });
    salvaVistas(vistas);
    window.dispatchEvent(new CustomEvent('notif:todas-vistas'));
  }

  /* ── Estado do botão marcar todas ── */
  function atualizaBotaoMarkAll() {
    if (!markAllBtn) return;
    const temNaoVista = main.querySelector('.notif-page-item--unread');
    markAllBtn.style.opacity      = temNaoVista ? '1' : '0.3';
    markAllBtn.style.pointerEvents = temNaoVista ? 'auto' : 'none';
  }

  /* ── Cores por badge ── */
  const BADGE_COLORS = {
    novo:     'linear-gradient(135deg,#1a56f0,#1240c7)',
    encarte:  'linear-gradient(135deg,#a855f7,#ec4899)',
    contato:  'linear-gradient(135deg,#10b981,#059669)',
    social:   'linear-gradient(135deg,#f6a823,#f05c22)',
    delivery: 'linear-gradient(135deg,#ef4444,#dc2626)',
    local:    'linear-gradient(135deg,#06b6d4,#3b82f6)',
    info:     'linear-gradient(135deg,#6b7280,#374151)',
  };

  /* ── Agrupa notificações por período ── */
  function agrupa(notificacoes) {
    const agora  = new Date();
    const hoje   = new Date(agora.getFullYear(), agora.getMonth(), agora.getDate());
    const ontem  = new Date(hoje); ontem.setDate(hoje.getDate() - 1);
    const semana = new Date(hoje); semana.setDate(hoje.getDate() - 7);

    const grupos = { hoje: [], ontem: [], semana: [], antigas: [] };

    notificacoes.forEach(n => {
      const data = new Date(n.criada_em);
      const dia  = new Date(data.getFullYear(), data.getMonth(), data.getDate());

      if (dia >= hoje)        grupos.hoje.push(n);
      else if (dia >= ontem)  grupos.ontem.push(n);
      else if (dia >= semana) grupos.semana.push(n);
      else                    grupos.antigas.push(n);
    });

    return grupos;
  }

  /* ── Renderiza um item ── */
  function renderItem(notif, vistas) {
    const isNova      = !vistas.includes(notif.id);
    const bg          = BADGE_COLORS[notif.badge] || BADGE_COLORS.info;
    const itemExtra   = isNova ? ' notif-page-item--unread' : '';
    const avatarExtra = isNova ? ' notif-page-avatar--live' : '';

    const avatarInner = notif.avatar_url
      ? `<img src="${notif.avatar_url}" alt="${notif.store_name}" class="notif-page-avatar-img">`
      : `<span class="notif-page-avatar-letter">${notif.inicial}</span>`;

    const dotHtml = isNova
      ? `<div class="notif-page-dot" aria-hidden="true"></div>`
      : '';

    return `
      <li class="notif-page-item${itemExtra}"
          role="listitem"
          data-id="${notif.id}"
          data-slug="${notif.store_slug}">
        <div class="notif-page-avatar-wrap">
          <div class="notif-page-avatar${avatarExtra}" style="background:${bg}">
            ${avatarInner}
          </div>
        </div>
        <div class="notif-page-content">
          <p class="notif-page-text">
            <strong>${notif.store_name}</strong> ${notif.texto}
          </p>
          <time class="notif-page-time" datetime="${notif.criada_em}">
            ${notif.tempo}
          </time>
        </div>
        ${dotHtml}
      </li>`;
  }

  /* ── Renderiza um grupo ── */
  function renderGrupo(label, itens, vistas) {
    if (!itens.length) return '';
    return `
      <div class="notif-group">
        <div class="notif-group-label">${label}</div>
        <ul class="notif-group-list" role="list">
          ${itens.map(n => renderItem(n, vistas)).join('')}
        </ul>
      </div>`;
  }

  /* ── Renderiza tudo ── */
  function renderTudo(notificacoes, vistas) {
    const grupos = agrupa(notificacoes);
    const html = [
      renderGrupo('Hoje',         grupos.hoje,    vistas),
      renderGrupo('Ontem',        grupos.ontem,   vistas),
      renderGrupo('Essa semana',  grupos.semana,  vistas),
      renderGrupo('Mais antigas', grupos.antigas, vistas),
    ].join('');

    return html || renderVazio();
  }

  function renderVazio() {
    return `
      <div class="notif-page-empty">
        <span class="notif-page-empty-icon">🔔</span>
        <p>Nenhuma novidade por agora.</p>
        <small>Volte em breve!</small>
      </div>`;
  }

  function renderErro() {
    return `
      <div class="notif-page-empty">
        <span class="notif-page-empty-icon">⚠️</span>
        <p>Não foi possível carregar.</p>
        <small>Tente novamente em instantes.</small>
      </div>`;
  }

  function renderLoading() {
    return `
      <div class="notif-page-loading">
        <span class="notif-page-loading-dot"></span>
        <span class="notif-page-loading-dot"></span>
        <span class="notif-page-loading-dot"></span>
      </div>`;
  }

  /* ── Clique num item ── */
  function onItemClick(e) {
    const item = e.target.closest('.notif-page-item');
    if (!item || !item.dataset.slug) return;

    const id   = parseInt(item.dataset.id);
    const slug = item.dataset.slug;

    if (id) marcarComoVista(id);
    item.classList.remove('notif-page-item--unread');

    const avatar = item.querySelector('.notif-page-avatar');
    if (avatar) avatar.classList.remove('notif-page-avatar--live');

    const dot = item.querySelector('.notif-page-dot');
    if (dot) {
      dot.style.opacity    = '0';
      dot.style.transition = 'opacity 0.25s';
      setTimeout(() => dot.remove(), 250);
    }

    const sk = document.getElementById('skeletonScreen');
    if (sk) sk.classList.add('visible');

    setTimeout(() => {
      window.location.href = `/${slug}/`;
    }, 200);
  }

  /* ── Marcar todas ── */
  function markAll() {
    const items = main.querySelectorAll('.notif-page-item');
    const ids   = [];

    items.forEach(item => {
      const id = parseInt(item.dataset.id);
      if (id) ids.push(id);

      item.classList.remove('notif-page-item--unread');

      const avatar = item.querySelector('.notif-page-avatar');
      if (avatar) avatar.classList.remove('notif-page-avatar--live');

      const dot = item.querySelector('.notif-page-dot');
      if (dot) {
        dot.style.opacity    = '0';
        dot.style.transition = 'opacity 0.3s';
        setTimeout(() => dot.remove(), 300);
      }
    });

    todasVistas(ids);

    // Apaga nav dot
    const navDot = document.querySelector('[data-tab="notifications"] .nav-dot');
    if (navDot) {
      navDot.style.opacity    = '0';
      navDot.style.transition = 'opacity 0.3s';
    }

    atualizaBotaoMarkAll();

    if (markAllBtn) {
        markAllBtn.textContent = 'Marcar como lidas';
        markAllBtn.style.color = '#059669';
        setTimeout(() => {
        markAllBtn.style.opacity       = '0.3';
        markAllBtn.style.pointerEvents = 'none';
        markAllBtn.style.color         = '';
        }, 1000);
    }
  }

  /* ── Carregar ── */
  async function carrega() {
    main.innerHTML = renderLoading();

    try {
      const res  = await fetch(API_URL);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      const notificacoes = data.notificacoes || [];
      const vistas       = getVistas();

      // Limpa obsoletos do localStorage
      const idsAtivos = notificacoes.map(n => n.id);
      salvaVistas(vistas.filter(id => idsAtivos.includes(id)));

      main.innerHTML = renderTudo(notificacoes, getVistas());
      atualizaBotaoMarkAll();

    } catch (err) {
      console.error('[Click32] Erro ao carregar notificações:', err);
      main.innerHTML = renderErro();
    }
  }

  /* ── Voltar ── */
  if (backBtn) {
    backBtn.addEventListener('click', () => {
      if (history.length > 1) history.back();
      else window.location.href = '/';
    });
  }

  /* ── Eventos ── */
  main.addEventListener('click', onItemClick);
  if (markAllBtn) markAllBtn.addEventListener('click', markAll);

  /* ── Init ── */
  carrega();

});