document.addEventListener('DOMContentLoaded', function() {
    var shareButton = document.getElementById('shareButton');
    if (!shareButton) return;

    shareButton.addEventListener('click', function() {
        var storeId = this.getAttribute('data-store-id');
        var storeName = this.getAttribute('data-store-name');
        var storeUrl = this.getAttribute('data-store-url') || window.location.href;
        
        // Decodifica URL se estiver escapada (ex: \u002D → -)
        if (storeUrl.includes('\\u')) {
            storeUrl = decodeURIComponent(storeUrl);
        }
        
        // Remove parâmetros para URL limpa
        storeUrl = storeUrl.split('?')[0].split('#')[0];
        
        // 1. Tracking do compartilhamento
        fetch('/track-share/' + storeId + '/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json',
            }
        }).catch(function(error) {
            console.log('Erro no tracking, mas continua...');
        });

        // 2. Compartilhamento
        if (navigator.share) {
            navigator.share({
                title: storeName,
                text: 'Confira esta loja: ' + storeName,
                url: storeUrl
            }).catch(function(err) {
                // Usuário cancelou - não faz nada
            });
        } else {
            prompt("Copie o link da loja:", storeUrl);
        }
    });
});

// Função CSRF
function getCSRFToken() {
    var name = 'csrftoken';
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}