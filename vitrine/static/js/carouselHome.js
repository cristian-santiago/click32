document.addEventListener('DOMContentLoaded', () => {
  const carouselContainer = document.querySelector('.carousel-container');
  const carouselItems = document.querySelectorAll('.carousel-item');
  const dotsContainer = document.querySelector('.carousel-dots');
  const fadeMask = document.querySelector('.carousel-fade-mask');
  let activated = false;

  if (carouselContainer && carouselItems.length > 0) {
    carouselContainer.style.width = `${carouselItems.length * 100}%`;

    carouselItems.forEach(item => {
      item.style.width = `${100 / carouselItems.length}%`;
    });

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

    function currentSlide(n) {
      slideIndex = n;
      showSlides(slideIndex);
      resetAutoSlide();
    }

    function showSlides(n) {
      if (n > carouselItems.length) slideIndex = 1;
      if (n < 1) slideIndex = carouselItems.length;

      const slideWidthPercent = 100 / carouselItems.length;
      carouselContainer.style.transform = `translateX(-${(slideIndex - 1) * slideWidthPercent}%)`;

      carouselItems.forEach((item, index) => {
        item.classList.toggle('active', index === slideIndex - 1);
      });

      document.querySelectorAll('.carousel-dot').forEach((dot, index) => {
        dot.classList.toggle('active', index === slideIndex - 1);
      });
    }

    function autoSlide() {
      slideIndex++;
      showSlides(slideIndex);
    }

    let autoSlideInterval = setInterval(autoSlide, 3000);

    function resetAutoSlide() {
      clearInterval(autoSlideInterval);
      autoSlideInterval = setInterval(autoSlide, 3000);
    }

    let touchStartX = 0;
    let touchEndX = 0;

    carouselContainer.addEventListener('touchstart', (e) => {
      touchStartX = e.changedTouches[0].screenX;
    });

    carouselContainer.addEventListener('touchend', (e) => {
      touchEndX = e.changedTouches[0].screenX;
      handleSwipe();
    });

    function handleSwipe() {
      const swipeThreshold = 50;
      if (touchStartX - touchEndX > swipeThreshold) {
        currentSlide(slideIndex + 1);
      } else if (touchEndX - touchStartX > swipeThreshold) {
        currentSlide(slideIndex - 1);
      }
    }
  }

  function showFadeOnScroll() {
    if (!activated && window.scrollY > 0) {
      fadeMask?.classList.remove('hidden');
      activated = true;
      window.removeEventListener('scroll', showFadeOnScroll);
    }
  }

  window.addEventListener('scroll', showFadeOnScroll);
});
