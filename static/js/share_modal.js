document.addEventListener('DOMContentLoaded', function() {
    // Seleciona todos os elementos que podem compartilhar
    var shareTriggers = document.querySelectorAll('#shareButton, .share-trigger');
    
    if (!shareTriggers.length) return;
    
    function handleShare(event) {
        var element = event.currentTarget;
        var shareType = element.getAttribute('data-share-type');
        var storeId = element.getAttribute('data-store-id');
        var storeName = element.getAttribute('data-store-name');
        var storeUrl = element.getAttribute('data-store-url');
        
        // Se não tem URL definida, usa a URL atual
        if (!storeUrl) {
            storeUrl = window.location.href;
        }
        
        // Decodifica URL se estiver escapada
        if (storeUrl && storeUrl.includes('\\u')) {
            storeUrl = decodeURIComponent(storeUrl);
        }
        
        // Remove parâmetros para URL limpa
        if (storeUrl) {
            storeUrl = storeUrl.split('?')[0].split('#')[0];
        }
        
        // Só faz tracking se for uma loja (se tiver storeId)
        if (storeId) {
            fetch('/track-share/' + storeId + '/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'Content-Type': 'application/json',
                }
            }).catch(function(error) {
                console.log('Erro no tracking, mas continua...');
            });
        }
        
        // Define título e texto baseado no tipo
        var title = storeName || 'Confira este app';
        var text = storeName ? 'Confira esta loja: ' + storeName : 'Dê uma olhada neste app!';
        
        // 2. Compartilhamento
        if (navigator.share && storeUrl) {
            navigator.share({
                title: title,
                text: text,
                url: storeUrl
            }).catch(function(err) {
                if (err.name !== 'AbortError') {
                    console.log('Erro no compartilhamento:', err);
                }
            });
        } else if (storeUrl) {
            prompt("Copie o link:", storeUrl);
        }
    }
    
    // Adiciona evento a todos os elementos
    shareTriggers.forEach(function(trigger) {
        trigger.addEventListener('click', handleShare);
    });
});

// Função CSRF (mantém igual)
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