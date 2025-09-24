/**
 * Configura o evento de compartilhamento para o botão de compartilhamento.
 */
document.addEventListener('DOMContentLoaded', () => {
  const shareButton = document.getElementById('shareButton');
  if (!shareButton) return; // Exits if shareButton is not found

  const storeUrl = window.location.href;
  const storeName = "{{ store.name }}";

  // Configura o evento de clique para o botão de compartilhamento
  shareButton.addEventListener('click', async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: storeName,
          text: `Confira esta loja: ${storeName}`,
          url: storeUrl
        });
      } catch (err) {
        // Error handling for share failure or user cancellation
        alert('Não foi possível compartilhar. Tente novamente.');
      }
    } else {
      // Fallback for desktop or older browsers
      prompt("Copie o link da loja:", storeUrl);
    }
  });
});