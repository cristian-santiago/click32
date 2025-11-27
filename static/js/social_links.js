// social_links.js - Debug completo
document.querySelectorAll('a.social-link[data-redirect]').forEach(link => {
    link.addEventListener('click', async function(event) {
        event.preventDefault();
        const deepLinkUrl = this.getAttribute('data-redirect');
        
        console.log('=== DEBUG SOCIAL LINKS ===');
        console.log('URL:', deepLinkUrl);
        console.log('User Agent:', navigator.userAgent);
        console.log('Protocol:', window.location.protocol);
        console.log('Standalone:', window.matchMedia('(display-mode: standalone)').matches);
        
        // Testa se o deep link é suportado
        try {
            window.location.href = deepLinkUrl;
        } catch (error) {
            console.error('Erro ao abrir deep link:', error);
        }
    });
});