let deferredPrompt;

const installBtn = document.getElementById('installBtn');

window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  if (installBtn) {
    installBtn.classList.remove('hidden');
  }
});

if (installBtn) {
  installBtn.addEventListener('click', async () => {
    if (!deferredPrompt) return;

    deferredPrompt.prompt();
    const choiceResult = await deferredPrompt.userChoice;

    if (choiceResult.outcome === 'accepted') {
      installBtn.classList.add('hidden');
      deferredPrompt = null;
    }
  });
}

window.addEventListener('appinstalled', () => {
  if (installBtn) {
    installBtn.classList.add('hidden');
  }
});
