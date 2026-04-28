document.addEventListener('DOMContentLoaded', function() {
    var shareTriggers = document.querySelectorAll('#shareButton, .share-trigger');
    
    if (!shareTriggers.length) return;
    
    function handleShare(event) {
        var element = event.currentTarget;

        // ─── REGRA DE CONTEXTO ───────────────────────────────────────
        // Se existe #shareButton na página (store_detail), qualquer
        // botão de share usa os dados da loja — inclusive o nav.
        var storeShareBtn = document.getElementById('shareButton');
        var sourceEl = (storeShareBtn && element !== storeShareBtn)
            ? storeShareBtn   // nav clicado dentro de store_detail → redireciona para dados da loja
            : element;        // clicado no próprio botão da loja, ou em outra página
        // ─────────────────────────────────────────────────────────────

        var storeId   = sourceEl.getAttribute('data-store-id');
        var storeName = sourceEl.getAttribute('data-store-name');
        var storeUrl  = sourceEl.getAttribute('data-store-url');
        
        if (!storeUrl) {
            storeUrl = window.location.href;
        }
        
        if (storeUrl && storeUrl.includes('\\u')) {
            storeUrl = decodeURIComponent(storeUrl);
        }
        
        if (storeUrl) {
            storeUrl = storeUrl.split('?')[0].split('#')[0];
        }
        
        if (storeId) {
            fetch('/track-share/' + storeId + '/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'Content-Type': 'application/json',
                }
            }).catch(function() {
                console.log('Erro no tracking, mas continua...');
            });
        }
        
        var title = storeName || 'Confira este app';
        var text  = storeName
            ? 'Confira esta loja: ' + storeName
            : 'Dê uma olhada neste app!';
        
        if (navigator.share && storeUrl) {
            navigator.share({ title: title, text: text, url: storeUrl })
                .catch(function(err) {
                    if (err.name !== 'AbortError') console.log('Erro no compartilhamento:', err);
                });
        } else if (storeUrl) {
            prompt("Copie o link:", storeUrl);
        }
    }
    
    shareTriggers.forEach(function(trigger) {
        trigger.addEventListener('click', handleShare);
    });
});

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