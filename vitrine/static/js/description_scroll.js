document.addEventListener('DOMContentLoaded', () => {
  // Ajuste do padding da descrição para não sobrepor store-info
  function ajustarPaddingDescription() {
    const descriptionP = document.querySelector('.description p');
    const storeInfo = document.querySelector('.store-info');
    if (!descriptionP || !storeInfo) return;

    const descriptionRect = descriptionP.getBoundingClientRect();
    const descriptionBottom = descriptionRect.bottom;
    const storeInfoRect = storeInfo.getBoundingClientRect();
    const storeInfoTop = storeInfoRect.top;
    const overlap = descriptionBottom - storeInfoTop;

    if (overlap > 0) {
      descriptionP.style.paddingBottom = `${overlap + 10}px`;
    } else {
      descriptionP.style.paddingBottom = '';
    }
  }

  window.addEventListener('load', ajustarPaddingDescription);
  window.addEventListener('resize', ajustarPaddingDescription);
  window.addEventListener('scroll', ajustarPaddingDescription);

  // Sombra no scroll da descrição
  const descriptionP = document.querySelector('.description p');
  const storeName = document.querySelector('.store-name');
  const storeInfo = document.querySelector('.store-info');

  function updateScrollShadows() {
    if (!descriptionP || !storeName || !storeInfo) return;

    const scrollTop = descriptionP.scrollTop;
    const scrollHeight = descriptionP.scrollHeight;
    const clientHeight = descriptionP.clientHeight;

    // Remove classes de sombra
    storeName.classList.remove('scroll-shadow-top');
    storeInfo.classList.remove('scroll-shadow-bottom');

    // Adiciona sombra superior se não estiver no topo
    if (scrollTop > 0.5) { // Tolerância para valores fracionários
      storeName.classList.add('scroll-shadow-top');
    }

    // Adiciona sombra inferior se não estiver no final (com tolerância)
    if (scrollTop + clientHeight < scrollHeight - 1) {
      storeInfo.classList.add('scroll-shadow-bottom');
    }
  }

  if (descriptionP) {
    descriptionP.addEventListener('scroll', updateScrollShadows);
    updateScrollShadows(); // Chama inicialmente para definir o estado correto
  }
});
