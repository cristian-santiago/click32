document.querySelectorAll('a.social-item[data-store-id]').forEach(link => {
    link.addEventListener('click', function(e) {
        const trackUrl = this.getAttribute('data-track-url');
        if (trackUrl) {
            const trackingPixel = new Image();
            trackingPixel.src = trackUrl; // pega do template, não hardcoded
        }
    });
});