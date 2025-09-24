/**
 * Inicializa a funcionalidade do carrossel, incluindo navegação por dots e eventos de rolagem.
 */
function initializeCarousel() {
  const carouselContainer = document.querySelector('.carousel-container');
  const carouselItems = document.querySelectorAll('.carousel-container .carousel-item');
  const dotsContainer = document.querySelector('.carousel-dots');

  if (carouselContainer && carouselItems.length > 0) {
    // Cria dots para cada item do carrossel
    carouselItems.forEach((item, index) => {
      const dot = document.createElement('div');
      dot.className = 'carousel-dot';
      if (index === 0) dot.classList.add('active');
      dot.addEventListener('click', () => {
        carouselContainer.scrollTo({
          left: item.offsetLeft - carouselContainer.offsetLeft,
          behavior: 'smooth'
        });
        document.querySelectorAll('.carousel-dots .carousel-dot').forEach(d => d.classList.remove('active'));
        dot.classList.add('active');
      });
      dotsContainer.appendChild(dot);
    });

    // Manipula evento de rolagem para atualizar cada dot ativo
    carouselContainer.addEventListener('scroll', () => {
      const scrollLeft = carouselContainer.scrollLeft;
      const itemWidth = carouselItems[0].offsetWidth + 20;
      const activeIndex = Math.round(scrollLeft / itemWidth);
      document.querySelectorAll('.carousel-dots .carousel-dot').forEach((dot, index) => {
        dot.classList.toggle('active', index === activeIndex);
      });
    });
  }
}

/**
 * Inicializa o carrossel quando o DOM estiver carregado.
 */
document.addEventListener('DOMContentLoaded', initializeCarousel);