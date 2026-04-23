/**
 * Description Scroll Manager — new_store_detail
 * 3 estados:
 *   1. .fade-bottom           — início, tem texto abaixo
 *   2. .fade-top.fade-bottom  — meio do scroll
 *   3. .fade-top              — fim, todo texto lido
 *   (sem classe / .no-scroll) — texto cabe sem scroll
 */
(function () {
  'use strict';

  function init() {
    const card = document.querySelector('.desc-card');
    const text = document.querySelector('.desc-text');

    if (!card || !text) return;

    function updateFades() {
      const scrollTop    = text.scrollTop;
      const scrollHeight = text.scrollHeight;
      const clientHeight = text.clientHeight;
      const hasOverflow  = scrollHeight > clientHeight + 2;

      if (!hasOverflow) {
        card.classList.add('no-scroll');
        card.classList.remove('fade-top', 'fade-bottom');
        return;
      }

      card.classList.remove('no-scroll');

      const atTop    = scrollTop <= 4;
      const atBottom = scrollTop + clientHeight >= scrollHeight - 4;

      // fade-top: ativo quando NÃO está no topo
      card.classList.toggle('fade-top',    !atTop);

      // fade-bottom: ativo quando NÃO está no fundo
      card.classList.toggle('fade-bottom', !atBottom);
    }

    text.addEventListener('scroll', updateFades, { passive: true });
    window.addEventListener('resize', updateFades, { passive: true });

    // estado inicial após render
    requestAnimationFrame(updateFades);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();