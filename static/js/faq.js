document.addEventListener('DOMContentLoaded', function () {

    // ── ABAS ──────────────────────────────────────────────
    const tabs = document.querySelectorAll('.faq-tab');
    const panels = document.querySelectorAll('.faq-panel');

    tabs.forEach(function (tab) {
        tab.addEventListener('click', function () {
            const target = this.dataset.tab;

            // fecha todos os itens abertos ao trocar de aba
            document.querySelectorAll('.faq-item.active').forEach(function (item) {
                item.classList.remove('active');
                item.querySelector('.faq-answer').style.maxHeight = null;
                item.querySelector('.faq-icon').textContent = '+';
            });

            tabs.forEach(function (t) { t.classList.remove('active'); });
            panels.forEach(function (p) { p.classList.remove('active'); });

            tab.classList.add('active');
            document.querySelector('[data-panel="' + target + '"]').classList.add('active');
        });
    });

    // ── ACCORDION ─────────────────────────────────────────
    document.addEventListener('click', function (e) {
        const btn = e.target.closest('[data-faq]');
        if (!btn) return;

        const faqItem = btn.closest('.faq-item');
        const answer  = faqItem.querySelector('.faq-answer');
        const icon    = btn.querySelector('.faq-icon');
        const isOpen  = faqItem.classList.contains('active');

        // fecha outros dentro do mesmo painel
        const panel = faqItem.closest('.faq-panel');
        panel.querySelectorAll('.faq-item.active').forEach(function (item) {
            if (item !== faqItem) {
                item.classList.remove('active');
                item.querySelector('.faq-answer').style.maxHeight = null;
                item.querySelector('.faq-icon').textContent = '+';
            }
        });

        if (isOpen) {
            faqItem.classList.remove('active');
            answer.style.maxHeight = null;
            icon.textContent = '+';
        } else {
            faqItem.classList.add('active');
            answer.style.maxHeight = answer.scrollHeight + 'px';
            icon.textContent = '×';
        }
    });

});