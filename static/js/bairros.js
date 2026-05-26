// Evita recarregar a página se for o mesmo bairro
document.querySelectorAll('.card-bairro a').forEach(link => {
    link.addEventListener('click', (e) => {
        const url = new URL(link.href);
        if (url.hostname === window.location.hostname) {
            e.preventDefault();
            // Mesmo bairro, navega internamente
            window.location.href = '/';
        }
        // Bairro diferente → comportamento padrão (sai do app)
    });
});