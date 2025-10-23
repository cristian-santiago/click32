document.addEventListener('DOMContentLoaded', function() {
    var shareButton = document.getElementById('shareButton');
    if (!shareButton) return;

    var storeId = shareButton.getAttribute('data-store-id');
    var storeName = shareButton.getAttribute('data-store-name');
    var storeUrl = shareButton.getAttribute('data-store-url') || window.location.href;

    shareButton.addEventListener('click', function() {
        // 1. PRIMEIRO registra o compartilhamento
        fetch('/track-share/' + storeId + '/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json',
            }
        }).catch(function(error) {
            console.log('Erro no tracking, mas continua...');
        });

        // 2. DEPOIS abre o share
        if (navigator.share) {
            navigator.share({
                title: storeName,
                text: 'Confira esta loja: ' + storeName,
                url: storeUrl
            }).catch(function(err) {
                // Usuário cancelou
            });
        } else {
            prompt("Copie o link da loja:", storeUrl);
        }
    });
});

// Função CSRF (certifique-se que existe)
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