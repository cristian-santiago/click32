// social_tracking.js - Tracking silencioso para links sociais
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('a.social-link[data-store-id]').forEach(link => {
        link.addEventListener('click', function(e) {
            const storeId = this.getAttribute('data-store-id');
            const linkType = this.getAttribute('data-link-type');
            
            // Tracking silencioso (não bloqueia navegação)
            const trackingPixel = new Image();
            trackingPixel.src = `/track-click/${storeId}/${linkType}/`;
            
            // Comportamento normal do link (abre em nova aba/app)
        });
    });
});