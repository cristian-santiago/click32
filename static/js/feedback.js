(function () {
  'use strict';

  /* ══════════════════════════════
     STATE
  ══════════════════════════════ */
  let selectedRating = 0;
  let selectedCategory = '';

  /* ══════════════════════════════
     ELEMENTS
  ══════════════════════════════ */
  const starRating = document.getElementById('starRating');
 
  const categoryGrid = document.getElementById('categoryGrid');
  const feedbackText = document.getElementById('feedbackText');
  const charCount = document.getElementById('charCount');
  const submitBtn = document.getElementById('submitBtn');
  const formWrap = document.querySelector('.feedback-form-wrap');
  const successWrap = document.getElementById('feedbackSuccess');
  const backBtn = document.getElementById('backBtn');

  /* ══════════════════════════════
     STAR RATING
  ══════════════════════════════ */
  const stars = starRating.querySelectorAll('i');

  stars.forEach((star, index) => {
    // Click
    star.addEventListener('click', () => {
      selectedRating = parseInt(star.dataset.value);
      updateStars();
      updateRatingText();
    });

    // Hover
    star.addEventListener('mouseenter', () => {
      const hoverValue = parseInt(star.dataset.value);
      stars.forEach((s, i) => {
        if (i < hoverValue) {
          s.classList.add('hovered');
        } else {
          s.classList.remove('hovered');
        }
      });
    });
  });

  starRating.addEventListener('mouseleave', () => {
    stars.forEach(s => s.classList.remove('hovered'));
  });

  function updateStars() {
    stars.forEach((s, i) => {
      if (i < selectedRating) {
        s.classList.add('selected');
      } else {
        s.classList.remove('selected');
      }
    });
  }

  /* ══════════════════════════════
     CATEGORY
  ══════════════════════════════ */
  const categoryBtns = categoryGrid.querySelectorAll('.category-btn');

  categoryBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      categoryBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      selectedCategory = btn.dataset.category;
    });
  });

  /* ══════════════════════════════
     CHAR COUNTER
  ══════════════════════════════ */
  feedbackText.addEventListener('input', () => {
    const len = feedbackText.value.length;
    charCount.textContent = len;

    if (len > 500) {
      feedbackText.value = feedbackText.value.substring(0, 500);
      charCount.textContent = 500;
    }
  });

  /* ══════════════════════════════
     SUBMIT (dummy)
  ══════════════════════════════ */
  submitBtn.addEventListener('click', () => {
    const text = feedbackText.value.trim();

    // Validação simples
    if (!selectedRating) {
      alert('Por favor, avalie o Click32 com as estrelas.');
      return;
    }

    if (!selectedCategory) {
      alert('Por favor, selecione o tipo de feedback.');
      return;
    }

    if (!text) {
      alert('Por favor, descreva seu feedback.');
      return;
    }

    // Dummy submit
    console.log({
      rating: selectedRating,
      category: selectedCategory,
      text: text
    });

    // Mostra success
    formWrap.style.display = 'none';
    successWrap.classList.add('visible');
  });

  /* ══════════════════════════════
     BACK (reset)
  ══════════════════════════════ */
  backBtn.addEventListener('click', () => {
    // Reset
    selectedRating = 0;
    selectedCategory = '';
    feedbackText.value = '';
    charCount.textContent = '0';

    stars.forEach(s => s.classList.remove('selected'));
    categoryBtns.forEach(b => b.classList.remove('active'));
    

    // Volta pro form
    successWrap.classList.remove('visible');
    formWrap.style.display = 'block';
  });

})();