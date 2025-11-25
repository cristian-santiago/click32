// static/js/social_links.js
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('a.social-link[data-redirect]').forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            
            const webUrl = this.getAttribute('data-redirect');
            const trackUrl = this.getAttribute('href');
            
            // Se tem URL de tracking, abre numa nova aba/iframe invisível
            if (trackUrl && trackUrl !== '#') {
                const iframe = document.createElement('iframe');
                iframe.style.display = 'none';
                iframe.src = trackUrl;
                document.body.appendChild(iframe);
                
                // Remove o iframe após um tempo
                setTimeout(() => {
                    document.body.removeChild(iframe);
                }, 1000);
            }
            
            // Tenta abrir no app primeiro
            window.location.href = webUrl;
            
            // Se não abriu o app em 1 segundo, abre na web
            setTimeout(() => {
                if (!document.hidden) {
                    window.open(webUrl, '_blank', 'noopener,noreferrer');
                }
            }, 1000);
        });
        
        // Remove atributos que forçam abrir em nova aba
        link.removeAttribute('target');
        link.removeAttribute('rel');
    });
});