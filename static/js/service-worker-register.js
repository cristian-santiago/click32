/**
 * Configura o registro do Service Worker para habilitar funcionalidades de PWA.
 */
if ('serviceWorker' in navigator) {
  // Registra o Service Worker ao carregar a página
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/js/service-worker.js');
  });
}