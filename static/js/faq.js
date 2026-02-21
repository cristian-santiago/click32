document.addEventListener('DOMContentLoaded', function() {
    const faqButtons = document.querySelectorAll('[data-faq]');
    
    faqButtons.forEach(button => {
        button.addEventListener('click', function() {
            const faqItem = this.closest('.faq-item');
            const answer = faqItem.querySelector('.faq-answer');
            const icon = this.querySelector('.faq-icon');
            
            if (faqItem.classList.contains('active')) {
                faqItem.classList.remove('active');
                answer.style.maxHeight = null;
                icon.textContent = '+';
            } else {
                // Fecha outros itens abertos (opcional - comentar se quiser múltiplos abertos)
                document.querySelectorAll('.faq-item.active').forEach(item => {
                    if (item !== faqItem) {
                        item.classList.remove('active');
                        item.querySelector('.faq-answer').style.maxHeight = null;
                        item.querySelector('.faq-icon').textContent = '+';
                    }
                });
                
                faqItem.classList.add('active');
                answer.style.maxHeight = answer.scrollHeight + 'px';
                icon.textContent = '×';
            }
        });
    });
});