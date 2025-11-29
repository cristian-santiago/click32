document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('a.social-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            window.location.href = this.href;
        });
    });
});