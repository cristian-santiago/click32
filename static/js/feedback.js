// static/js/feedback.js

(function () {
  'use strict';

  /* ══════════════════════════════
     STATE
  ══════════════════════════════ */
  let selectedRating = 0;
  let selectedCategory = '';
  let isSubmitting = false;  // ← NOVO: prevenir double submit

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
    star.addEventListener('click', () => {
      selectedRating = parseInt(star.dataset.value);
      updateStars();
    });

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
    let len = feedbackText.value.length;
    
    // CORREÇÃO 1: Limita a 500 caracteres
    if (len > 500) {
      feedbackText.value = feedbackText.value.substring(0, 500);
      len = 500;
    }
    
    charCount.textContent = len;
  });

  /* ══════════════════════════════
     SUBMIT - CORREÇÃO PRINCIPAL
  ══════════════════════════════ */
  submitBtn.addEventListener('click', () => {
    // CORREÇÃO 2: Previne double submit
    if (isSubmitting) return;
    
    const text = feedbackText.value.trim();

    // Validações
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

    if (text.length < 3) {
      alert('Mensagem muito curta (mínimo 3 caracteres).');
      return;
    }

    // CORREÇÃO 3: Desabilita botão durante envio
    isSubmitting = true;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span>Enviando...</span><i class="fas fa-spinner fa-spin"></i>';

    // CORREÇÃO 4: Envia para o backend
    const data = {
      rating: selectedRating,
      category: selectedCategory,
      message: text
    };

    // CORREÇÃO 5: Pega o session_id se existir
    const sessionId = localStorage.getItem('session_id') || '';

    fetch('/api/feedback/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
      },
      body: JSON.stringify(data)
    })
    .then(response => {
      if (!response.ok) {
        return response.json().then(err => {
          throw new Error(err.error || 'Erro ao enviar');
        });
      }
      return response.json();
    })
    .then(result => {
      // CORREÇÃO 6: Sucesso
      formWrap.style.display = 'none';
      successWrap.classList.add('visible');
      
      // Reseta estado
      isSubmitting = false;
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<span>Enviar feedback</span><i class="fas fa-paper-plane"></i>';
    })
    .catch(error => {
      // CORREÇÃO 7: Mostra erro
      alert(error.message || 'Erro ao enviar feedback. Tente novamente.');
      
      // Reativa botão
      isSubmitting = false;
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<span>Enviar feedback</span><i class="fas fa-paper-plane"></i>';
    });
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
    
    // CORREÇÃO 8: Reseta botão
    isSubmitting = false;
    submitBtn.disabled = false;
    submitBtn.innerHTML = '<span>Enviar feedback</span><i class="fas fa-paper-plane"></i>';
  });

  /* ══════════════════════════════
     HELPER: CSRF TOKEN
  ══════════════════════════════ */
  function getCSRFToken() {
    // CORREÇÃO 9: Pega do cookie ou meta tag
    const cookieValue = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='))
      ?.split('=')[1];
    
    if (cookieValue) return cookieValue;
    
    // Fallback: meta tag
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.content : '';
  }

})();