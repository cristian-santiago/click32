if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/service-worker.js')
    .then(reg => {
      console.log('Service Worker registrado');

      reg.addEventListener('updatefound', () => {
        const newWorker = reg.installing;

        newWorker.addEventListener('statechange', () => {
          console.log('Estado do worker:', newWorker.state);

          if (newWorker.state === 'installed') {
            // Se já existe um SW ativo, significa que é update
            if (navigator.serviceWorker.controller) {
              console.log('Nova versão detectada, ativando...');
              newWorker.postMessage({ type: 'SKIP_WAITING' });
            }
          }
        });
      });
    })
    .catch(err => console.error('Erro ao registrar SW:', err));

  // Quando o novo SW assumir controle, recarrega a página
  let refreshing = false;
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    if (!refreshing) {
      refreshing = true;
      window.location.reload();
    }
  });
}