/**
 * PWA Installation and Tracking Script
 * Registra apenas a decisão do usuário (clique no botão, aceitar ou cancelar instalação)
 */
let deferredPrompt;
const installBtn = document.getElementById('installBtn');

// Evento disparado quando o PWA pode ser instalado
window.addEventListener('beforeinstallprompt', (e) => {
    // Previne o prompt automático do navegador
    e.preventDefault();
    deferredPrompt = e;
    
    // Mostra o botão de instalação customizado
    if (installBtn) {
        installBtn.classList.remove('hidden');
    }
});

// Handler do clique no botão de instalação
if (installBtn) {
    installBtn.addEventListener('click', async function(e) {
        e.preventDefault();
        
        // 1. Registra o clique no botão
        await trackPwaAction('clicked');
        
        // 2. Mostra prompt de instalação se disponível
        if (deferredPrompt) {
            try {
                // Mostra o prompt nativo de instalação
                deferredPrompt.prompt();
                const choiceResult = await deferredPrompt.userChoice;
                
                // Registra a decisão do usuário
                if (choiceResult.outcome === 'accepted') {
                    await trackPwaAction('accepted');
                } else {
                    await trackPwaAction('dismissed');
                }
                
                // Limpa a referência e esconde o botão
                deferredPrompt = null;
                installBtn.classList.add('hidden');
                
            } catch (error) {
                // Em caso de erro, registra como cancelado
                await trackPwaAction('dismissed');
            }
        } else {
            // Se não há prompt disponível, registra como cancelado
            await trackPwaAction('dismissed');
        }
    });
}

/**
 * Função para enviar tracking das ações do PWA
 * @param {string} action - Ação a ser registrada: 'clicked', 'accepted', 'dismissed'
 */
async function trackPwaAction(action) {
    try {
        const response = await fetch('/track-pwa-click/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ action: action })
        });
          
        // A resposta é ignorada propositalmente - o importante é o request ser enviado
        // Não bloqueia a experiência do usuário em caso de erro
        
    } catch (error) {
        // Falha silenciosa - não interfere na funcionalidade
    }
}

/**
 * Obtém o token CSRF dos cookies para requisições POST seguras
 * @returns {string} CSRF token ou string vazia se não encontrado
 */
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