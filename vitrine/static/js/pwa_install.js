/**
 * Inicialização da variável global para o evento de instalação do PWA.
 */
let deferredPrompt;

/**
 * Configuração do botão de instalação do PWA.
 */
const installBtn = document.getElementById('installBtn');

/**
 * Captura o evento beforeinstallprompt para exibir o botão de instalação.
 */
window.addEventListener('beforeinstallprompt', (e) => {
  // Prevents the default browser prompt
  e.preventDefault();
  deferredPrompt = e;
  if (installBtn) {
    installBtn.classList.remove('hidden');
  }
});

/**
 * Configura o evento de clique no botão de instalação.
 */
if (installBtn) {
  installBtn.addEventListener('click', async () => {
    if (!deferredPrompt) return;

    // Shows the installation prompt
    deferredPrompt.prompt();
    const choiceResult = await deferredPrompt.userChoice;

    // Hides the button if the user accepts the installation
    if (choiceResult.outcome === 'accepted') {
      installBtn.classList.add('hidden');
      deferredPrompt = null;
    }
  });
}

/**
 * Oculta o botão de instalação após a conclusão da instalação do PWA.
 */
window.addEventListener('appinstalled', () => {
  if (installBtn) {
    installBtn.classList.add('hidden');
  }
});