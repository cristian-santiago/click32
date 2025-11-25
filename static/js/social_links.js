// social_links.js - Mobile otimizado
let linkClicked = false;

document.querySelectorAll('a.social-link[data-redirect]').forEach(link => {
    link.addEventListener('click', function(event) {
        if (linkClicked) return;
        linkClicked = true;
        
        event.preventDefault();
        const webUrl = this.getAttribute('data-redirect');
        
        // Abre o app - PWA vai para background (normal no mobile)
        window.location.href = webUrl;
        
        // Reseta após 2s (tempo pro app abrir)
        setTimeout(() => { linkClicked = false; }, 2000);
    });
});