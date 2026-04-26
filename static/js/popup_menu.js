(function () {
  'use strict';

  const btnMais   = document.getElementById('btnMais');
  const popupMenu = document.getElementById('popupMenu');

  if (!btnMais || !popupMenu) return;

  btnMais.addEventListener('click', (e) => {
    e.stopPropagation();
    popupMenu.classList.toggle('open');
    btnMais.classList.toggle('active');
  });

  document.addEventListener('click', (e) => {
    if (!popupMenu.contains(e.target) && e.target !== btnMais) {
      popupMenu.classList.remove('open');
      btnMais.classList.remove('active');
    }
  });

})();