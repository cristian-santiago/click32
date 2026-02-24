if ('serviceWorker' in navigator) {
  // Registra com updateViaCache: 'none' - ESSENCIAL!
  navigator.serviceWorker.register('/service-worker.js', {
    updateViaCache: 'none'
  })
  .then(reg => {
    console.log('Service Worker registrado');

    // Força verificação de atualização a cada visita
    reg.update();

    reg.addEventListener('updatefound', () => {
      const newWorker = reg.installing;
      console.log('Nova versão encontrada!');
      
      newWorker.addEventListener('statechange', () => {
        if (newWorker.state === 'installed') {
          if (navigator.serviceWorker.controller) {
            console.log('Nova versão instalada, ativando...');
            newWorker.postMessage({ type: 'SKIP_WAITING' });
          }
        }
      });
    });
  });
}



// Força verificação periódica (a cada 1h)
setInterval(() => {
  navigator.serviceWorker.ready.then(reg => reg.update());
}, 60 * 60 * 1000);