// social_links.js
document.querySelectorAll('a.social-link[data-redirect]').forEach(link => {
    link.addEventListener('click', function(event) {
        event.preventDefault();
        const url = this.getAttribute('data-redirect');
        
        // Tenta abrir o app
        window.location.href = url;
        
        // Se não abrir em 1s, abre na web
        setTimeout(() => {
            if (!document.hidden) {
                // Converte deep link de volta para web se possível
                const webUrl = url.replace(/^[a-z]+:\/\//, 'https://');
                window.open(webUrl, '_blank', 'noopener,noreferrer');
            }
        }, 1000);
    });
});