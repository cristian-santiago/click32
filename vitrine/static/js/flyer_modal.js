/* Inicialização das variáveis globais */
const modalElement = document.getElementById('flyerModal');
const loadingSpinner = document.querySelector('.flyer-modal .loading-spinner');
const errorMessage = document.querySelector('.flyer-modal .error-message');
let isFetching = false;
let currentFlyerIndex = 0;
let zoomState = {
  scale: 1,
  translateX: 0,
  translateY: 0,
  baseTranslateY: 0,
  startDistance: 0,
  startX: 0,
  startY: 0,
  isPinching: false,
  isDragging: false
};

/**
 * Inicializa o modal de encarte, escondendo-o e resetando estados.
 */
function initializeFlyerModal() {
  if (modalElement) {
    modalElement.classList.remove('show');
    modalElement.style.display = 'none';
    modalElement.setAttribute('aria-hidden', 'true');
    loadingSpinner.classList.remove('active');
    errorMessage.style.display = 'none';
  }
}

/**
 * Fecha o modal, resetando estados e conteúdo.
 */
function closeModal() {
  modalElement.classList.remove('show');
  modalElement.style.display = 'none';
  modalElement.setAttribute('aria-hidden', 'true');
  document.body.style.overflow = 'auto';
  loadingSpinner.classList.remove('active');
  errorMessage.style.display = 'none';
  isFetching = false;
  currentFlyerIndex = 0;
  document.getElementById('flyerCarouselInner').innerHTML = '';
  document.getElementById('flyerIndicators').innerHTML = '';
  zoomState = {
    scale: 1,
    translateX: 0,
    translateY: 0,
    baseTranslateY: 0,
    startDistance: 0,
    startX: 0,
    startY: 0,
    isPinching: false,
    isDragging: false
  };
}

/**
 * Calcula a distância entre dois pontos de toque para zoom.
 */
function getTouchDistance(touches) {
  const dx = touches[0].clientX - touches[1].clientX;
  const dy = touches[0].clientY - touches[1].clientY;
  return Math.sqrt(dx * dx + dy * dy);
}

/**
 * Aplica transformações de zoom e deslocamento à imagem
 */
function applyTransform(img) {
  // Sempre aplica baseTranslateY + translateY para centralizar retrato
  const totalTranslateY = zoomState.translateY + zoomState.baseTranslateY;
  img.style.transform = `scale(${zoomState.scale}) translate(${zoomState.translateX}px, ${totalTranslateY}px)`;
}

/**
 * Ajusta posição inicial em retrato ou landscape
 */
function adjustInitialPosition(img) {
  const container = img.parentElement;
  const containerHeight = container.clientHeight;
  const imgHeight = img.clientHeight;

  zoomState.scale = 1;
  zoomState.translateX = 0;
  zoomState.translateY = 0;

  // Centraliza verticalmente se retrato ou se a imagem for menor que o container
  if (window.matchMedia("(orientation: portrait)").matches || imgHeight < containerHeight) {
    zoomState.baseTranslateY = Math.max(0, (containerHeight - imgHeight) / 2);
  } else {
    zoomState.baseTranslateY = 0;
  }

  applyTransform(img);
}

/**
 * Configura os eventos de clique para abrir e manipular o modal de encarte.
 */
function handleFlyerModal() {
  document.querySelectorAll('.open-flyer-modal').forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      if (isFetching) return;
      isFetching = true;

      const storeId = this.getAttribute('data-store-id');
      const carouselInner = document.getElementById('flyerCarouselInner');
      const indicatorsContainer = document.getElementById('flyerIndicators');

      if (!carouselInner || !indicatorsContainer) {
        window.alert('Erro: Elementos do carrossel não encontrados.');
        isFetching = false;
        return;
      }

      loadingSpinner.classList.add('active');
      errorMessage.style.display = 'none';
      carouselInner.innerHTML = '';
      indicatorsContainer.innerHTML = '';

      modalElement.classList.add('show');
      modalElement.style.display = 'flex';
      modalElement.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';

      const timeoutId = setTimeout(() => {
        if (isFetching) {
          window.alert('Erro: A solicitação está demorando muito.');
          closeModal();
        }
      }, 10000);

      fetch(`/fetch-flyer-pages/${storeId}/`, { method: 'GET' })
        .then(response => {
          clearTimeout(timeoutId);
          if (!response.ok) throw new Error('Erro na resposta do servidor: ' + response.status);
          return response.json();
        })
        .then(data => {
          if (data.error) {
            window.alert(data.error);
            closeModal();
            return;
          }

          if (!data.page_urls || !Array.isArray(data.page_urls) || data.page_urls.length === 0) {
            window.alert('Nenhuma imagem disponível para o encarte.');
            closeModal();
            return;
          }

          const preloadImages = data.page_urls.map((url, index) => {
            return new Promise((resolve, reject) => {
              const img = new Image();
              img.src = url;
              img.onload = () => resolve(url);
              img.onerror = () => reject(new Error(`Falha ao carregar a imagem ${index + 1}: ${url}`));
            });
          });

          Promise.allSettled([...preloadImages, new Promise(resolve => setTimeout(resolve, 2000))])
            .then(results => {
              const failedImages = results.filter(result => result.status === 'rejected').map(result => result.reason.message);
              if (failedImages.length > 0) {
                window.alert(`Erro ao carregar algumas imagens: ${failedImages.join(', ')}`);
                closeModal();
                return;
              }

              carouselInner.innerHTML = '';
              indicatorsContainer.innerHTML = '';

              data.page_urls.forEach((url, index) => {
                const div = document.createElement('div');
                div.className = `carousel-item ${index === 0 ? 'active' : ''}`;
                div.style.transform = index === 0 ? 'translateX(0)' : 'translateX(100%)';
                div.style.opacity = index === 0 ? '1' : '0';

                div.innerHTML = `
                  <div class="pinch-zoom-container"
                        style="width: 100%; height: 100%; display: flex; align-items: flex-start; justify-content: center; overflow-y: auto; overflow-x: hidden; touch-action: pan-y;">
                      <img src="${url}" 
                          alt="Página ${index + 1} do encarte"
                          style="width: 100%; height: auto; max-width: none; user-select: none; -webkit-user-drag: none; display: block;">
                  </div>
                `;

                const img = div.querySelector("img");
                img.onload = () => {
                  adjustInitialPosition(img);
                };
                carouselInner.appendChild(div);

                const indicator = document.createElement('button');
                indicator.type = 'button';
                indicator.className = `carousel-indicator ${index === 0 ? 'active' : ''}`;
                indicator.setAttribute('aria-label', `Slide ${index + 1}`);
                indicator.addEventListener('click', () => {
                  const items = document.querySelectorAll('.flyer-modal .carousel-item');
                  const indicators = document.querySelectorAll('.flyer-modal .carousel-indicator');
                  items.forEach((item, i) => {
                    item.classList.remove('active');
                    item.style.transform = i < index ? 'translateX(-100%)' : 'translateX(100%)';
                    item.style.opacity = '0';
                  });
                  items[index].classList.add('active');
                  items[index].style.transform = 'translateX(0)';
                  items[index].style.opacity = '1';
                  indicators.forEach(ind => ind.classList.remove('active'));
                  indicator.classList.add('active');
                  currentFlyerIndex = index;
                  zoomState = { ...zoomState, scale: 1, translateX: 0, translateY: 0 };
                  const img = items[index].querySelector('img');
                  if (img) applyTransform(img);
                });
                indicatorsContainer.appendChild(indicator);
              });

              // Setup zoom e touch
              document.querySelectorAll('.pinch-zoom-container').forEach(container => {
                const img = container.querySelector('img');
                if (!img) return;

                // Zoom mouse
                container.addEventListener('wheel', (e) => {
                  e.preventDefault();
                  const delta = e.deltaY > 0 ? -0.1 : 0.1;
                  zoomState.scale = Math.max(1, Math.min(4, zoomState.scale + delta));
                  applyTransform(img);
                });

                // Touch
                container.addEventListener('touchstart', (e) => {
                  if (e.touches.length === 2) {
                    zoomState.isPinching = true;
                    zoomState.startDistance = getTouchDistance(e.touches);
                  }
                });

                container.addEventListener('touchmove', (e) => {
                  if (zoomState.isPinching && e.touches.length === 2) {
                    e.preventDefault();
                    const currentDistance = getTouchDistance(e.touches);
                    const scaleChange = currentDistance / zoomState.startDistance;
                    zoomState.scale = Math.max(1, Math.min(4, zoomState.scale * scaleChange));
                    zoomState.startDistance = currentDistance;
                    applyTransform(img);
                  }
                });

                container.addEventListener('touchend', () => {
                  zoomState.isPinching = false;
                });
              });

              // Botões de zoom
              document.querySelectorAll('.zoom-in').forEach(button => {
                button.addEventListener('click', () => {
                  const items = document.querySelectorAll('.flyer-modal .carousel-item');
                  const img = items[currentFlyerIndex].querySelector('img');
                  if (img) {
                    zoomState.scale = Math.min(4, zoomState.scale + 0.5);
                    applyTransform(img);
                  }
                });
              });

              document.querySelectorAll('.zoom-out').forEach(button => {
                button.addEventListener('click', () => {
                  const items = document.querySelectorAll('.flyer-modal .carousel-item');
                  const img = items[currentFlyerIndex].querySelector('img');
                  if (img) {
                    zoomState.scale = Math.max(1, zoomState.scale - 0.5);
                    applyTransform(img);
                  }
                });
              });

              document.querySelectorAll('.zoom-reset').forEach(button => {
                button.addEventListener('click', () => {
                  const items = document.querySelectorAll('.flyer-modal .carousel-item');
                  const img = items[currentFlyerIndex].querySelector('img');
                  if (img) {
                    zoomState = { ...zoomState, scale: 1, translateX: 0, translateY: 0 };
                    applyTransform(img);
                  }
                });
              });

              loadingSpinner.classList.remove('active');
              isFetching = false;
            })
            .catch(() => {
              window.alert('Erro ao carregar as imagens do encarte.');
              closeModal();
            });
        })
        .catch(() => {
          window.alert('Erro ao carregar o encarte: Falha na conexão com o servidor.');
          closeModal();
        });
    });
  });

  if (modalElement) {
    modalElement.querySelector('.btn-close').addEventListener('click', () => {
      closeModal();
      modalElement.querySelector('.btn-close').blur();
    });
  }
}

/**
 * Configura eventos de swipe para navegação no carrossel do modal.
 */
function handleSwipe() {
  const flyerCarouselInner = document.getElementById('flyerCarouselInner');
  if (flyerCarouselInner) {
    let startX = 0;
    let isSwiping = false;

    flyerCarouselInner.addEventListener('touchstart', e => {
      if (e.touches.length === 1) {
        startX = e.touches[0].clientX;
        isSwiping = true;
      }
    });

    flyerCarouselInner.addEventListener('touchmove', e => {
      if (e.touches.length > 1) isSwiping = false;
    });

    flyerCarouselInner.addEventListener('touchend', e => {
      if (!isSwiping || zoomState.scale > 1) return;
      const endX = e.changedTouches[0].clientX;
      const deltaX = endX - startX;
      const items = document.querySelectorAll('.flyer-modal .carousel-item');
      const indicators = document.querySelectorAll('.flyer-modal .carousel-indicator');
      if (deltaX > 50 && currentFlyerIndex > 0) {
        items[currentFlyerIndex].classList.remove('active');
        items[currentFlyerIndex].style.transform = 'translateX(100%)';
        items[currentFlyerIndex].style.opacity = '0';
        indicators[currentFlyerIndex].classList.remove('active');
        currentFlyerIndex--;
        items[currentFlyerIndex].classList.add('active');
        items[currentFlyerIndex].style.transform = 'translateX(0)';
        items[currentFlyerIndex].style.opacity = '1';
        indicators[currentFlyerIndex].classList.add('active');
        zoomState = { ...zoomState, scale: 1, translateX: 0, translateY: 0 };
        const img = items[currentFlyerIndex].querySelector('img');
        if (img) applyTransform(img);
      } else if (deltaX < -50 && currentFlyerIndex < items.length - 1) {
        items[currentFlyerIndex].classList.remove('active');
        items[currentFlyerIndex].style.transform = 'translateX(-100%)';
        items[currentFlyerIndex].style.opacity = '0';
        indicators[currentFlyerIndex].classList.remove('active');
        currentFlyerIndex++;
        items[currentFlyerIndex].classList.add('active');
        items[currentFlyerIndex].style.transform = 'translateX(0)';
        items[currentFlyerIndex].style.opacity = '1';
        indicators[currentFlyerIndex].classList.add('active');
        zoomState = { ...zoomState, scale: 1, translateX: 0, translateY: 0 };
        const img = items[currentFlyerIndex].querySelector('img');
        if (img) applyTransform(img);
      }
      isSwiping = false;
    });
  }
}

/**
 * Inicializa as funções do modal e eventos relacionados ao carregar o DOM.
 */
document.addEventListener('DOMContentLoaded', () => {
  initializeFlyerModal();
  handleFlyerModal();
  handleSwipe();
});
