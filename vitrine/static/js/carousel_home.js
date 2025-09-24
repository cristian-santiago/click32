/**
 * Configura o carrossel com navegação por pontos, swipe e transição automática.
 */
document.addEventListener('DOMContentLoaded', () => {
  // Seleção dos elementos do carrossel
  const carouselContainer = document.querySelector('.carousel-container');
  const carouselItems = document.querySelectorAll('.carousel-item');
  const dotsContainer = document.querySelector('.carousel-dots');
  const fadeMask = document.querySelector('.carousel-fade-mask');
  let activated = false;

  // Configura o carrossel se existirem itens
  if (carouselContainer && carouselItems.length > 0) {
    // Ajusta a largura do contêiner do carrossel
    carouselContainer.style.width = `${carouselItems.length * 100}%`;

    // Define a largura de cada item do carrossel
    carouselItems.forEach(item => {
      item.style.width = `${100 / carouselItems.length}%`;
    });

    // Cria os pontos de navegação
    carouselItems.forEach((item, index) => {
      const dot = document.createElement('div');
      dot.className = 'carousel-dot';
      if (index === 0) dot.classList.add('active');
      dot.addEventListener('click', () => {
        currentSlide(index + 1);
      });
      dotsContainer.appendChild(dot);
    });

    let slideIndex = 1;
    showSlides(slideIndex);

    /**
     * Define o slide atual e reinicia a transição automática.
     */
    function currentSlide(n) {
      slideIndex = n;
      showSlides(slideIndex);
      resetAutoSlide();
    }

    /**
     * Exibe o slide correspondente ao índice fornecido.
     */
    function showSlides(n) {
      if (n > carouselItems.length) slideIndex = 1;
      if (n < 1) slideIndex = carouselItems.length;

      const slideWidthPercent = 100 / carouselItems.length;
      carouselContainer.style.transform = `translateX(-${(slideIndex - 1) * slideWidthPercent}%)`;

      // Ativa/desativa a classe active nos itens
      carouselItems.forEach((item, index) => {
        item.classList.toggle('active', index === slideIndex - 1);
      });

      // Atualiza os pontos de navegação
      document.querySelectorAll('.carousel-dot').forEach((dot, index) => {
        dot.classList.toggle('active', index === slideIndex - 1);
      });
    }

    /**
     * Avança automaticamente para o próximo slide.
     */
    function autoSlide() {
      slideIndex++;
      showSlides(slideIndex);
    }

    let autoSlideInterval = setInterval(autoSlide, 3000);

    /**
     * Reinicia o intervalo de transição automática.
     */
    function resetAutoSlide() {
      clearInterval(autoSlideInterval);
      autoSlideInterval = setInterval(autoSlide, 3000);
    }

    let touchStartX = 0;
    let touchEndX = 0;

    // Captura o início do toque
    carouselContainer.addEventListener('touchstart', (e) => {
      touchStartX = e.changedTouches[0].screenX;
    });

    // Captura o fim do toque
    carouselContainer.addEventListener('touchend', (e) => {
      touchEndX = e.changedTouches[0].screenX;
      handleSwipe();
    });

    /**
     * Lida com o movimento de swipe para navegar entre slides.
     */
    function handleSwipe() {
      const swipeThreshold = 50;
      if (touchStartX - touchEndX > swipeThreshold) {
        currentSlide(slideIndex + 1);
      } else if (touchEndX - touchStartX > swipeThreshold) {
        currentSlide(slideIndex - 1);
      }
    }
  }

  /**
   * Exibe a máscara de fade ao rolar a página.
   */
  function showFadeOnScroll() {
    if (!activated && window.scrollY > 0) {
      fadeMask?.classList.remove('hidden');
      activated = true;
      window.removeEventListener('scroll', showFadeOnScroll);
    }
  }

  // Configura o evento de rolagem para a máscara de fade
  window.addEventListener('scroll', showFadeOnScroll);
});