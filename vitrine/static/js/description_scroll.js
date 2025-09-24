/**
 * Configura eventos para ajustar o padding da descrição e sombras de rolagem.
 */
document.addEventListener('DOMContentLoaded', () => {
  // Seleção dos elementos DOM
  const descriptionP = document.querySelector('.description p');
  const storeInfo = document.querySelector('.store-info');

  // Verifica se os elementos existem
  if (!descriptionP || !storeInfo) return;

  /**
   * Ajusta o padding-bottom do parágrafo da descrição para evitar sobreposição com store-info.
   */
  function ajustarPaddingDescription() {
    const descriptionRect = descriptionP.getBoundingClientRect();
    const descriptionBottom = descriptionRect.bottom;
    const storeInfoRect = storeInfo.getBoundingClientRect();
    const storeInfoTop = storeInfoRect.top;
    const overlap = descriptionBottom - storeInfoTop;

    // Aplica padding se houver sobreposição, caso contrário remove
    if (overlap > 0) {
      descriptionP.style.paddingBottom = `${overlap + 10}px`;
    } else {
      descriptionP.style.paddingBottom = '';
    }
  }

  /**
   * Atualiza as sombras de rolagem com base na posição do scroll no parágrafo.
   */
  function updateScrollShadows() {
    const scrollTop = descriptionP.scrollTop;
    const scrollHeight = descriptionP.scrollHeight;
    const clientHeight = descriptionP.clientHeight;

    // Remove classes de sombra
    descriptionP.classList.remove('scroll-shadow-top');
    storeInfo.classList.remove('scroll-shadow-top');

    // Adiciona sombra superior se o scroll não está no topo
    if (scrollTop > 5) {
      descriptionP.classList.add('scroll-shadow-top');
    }

    // Adiciona sombra inferior se o scroll não está no final
    if (scrollTop + clientHeight < scrollHeight - 5) {
      storeInfo.classList.add('scroll-shadow-top');
    }
  }

  // Configura eventos para ajustar padding e sombras
  window.addEventListener('load', ajustarPaddingDescription);
  window.addEventListener('resize', ajustarPaddingDescription);
  window.addEventListener('scroll', ajustarPaddingDescription);
  descriptionP.addEventListener('scroll', updateScrollShadows);

  // Inicializa as funções
  updateScrollShadows();
  ajustarPaddingDescription();
});