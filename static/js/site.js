
        /* ----------------------------------------------------------
           MENU MOBILE — Ouvre/ferme le menu hamburger
        ---------------------------------------------------------- */
        function toggleMenu() {
            const menu = document.getElementById('mobileMenu');
            const toggle = document.querySelector('.menu-toggle');
            menu.classList.toggle('open');
            toggle.classList.toggle('active');
            toggle.setAttribute('aria-expanded', String(menu.classList.contains('open')));
            toggle.setAttribute('aria-label', menu.classList.contains('open') ? 'Fermer le menu' : 'Ouvrir le menu');
        }

        /* ----------------------------------------------------------
           NAV ACTIVE AU SCROLL
           Met en surbrillance le lien correspondant à la section visible
        ---------------------------------------------------------- */
        document.querySelectorAll('header nav a, .mobile-menu a').forEach(link => {
            if (new URL(link.href).pathname === window.location.pathname) {
                link.setAttribute('aria-current', 'page');
            }
        });

        /* ----------------------------------------------------------
           FAQ ACCORDION
           Ouvre une question et ferme les autres
        ---------------------------------------------------------- */
        function toggleFaq(btn) {
            const item = btn.closest('.faq-item');
            const isOpen = item.classList.contains('open');

            // Ferme toutes les questions
            document.querySelectorAll('.faq-item').forEach(i => {
                i.classList.remove('open');
                i.querySelector('button').setAttribute('aria-expanded', 'false');
            });

            // Ouvre celle cliquée si elle était fermée
            if (!isOpen) {
                item.classList.add('open');
                btn.setAttribute('aria-expanded', 'true');
            }
        }

// Fade-up progressif : une apparition par bloc, sans cacher le contenu sans JS.
(() => {
    const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (motion.matches || !('IntersectionObserver' in window)) return;
    const selector = '.home-shortcuts > h2, .news-top, .page-heading, .courses-intro, .admissions-intro, .page-callout, .vie_scolaire_content, .home-shortcut, .course-card, .admissions-levels article, .admissions-steps li, .admissions-panel, .news-card, .formation-card, .feature, .img_about, .content, .vie_scolaire_content2 > div, .main-member, .dir-card, .ens-card, .testi-card, .contact-info, .contact-form-wrap';
    const observer = new IntersectionObserver(entries => {
        let position = 0;
        entries.forEach(entry => {
            if (!entry.isIntersecting) return;
            // Un bloc déjà dépassé ne doit pas clignoter en remontant la page.
            if (!motion.matches && entry.boundingClientRect.bottom > 0) {
                entry.target.style.setProperty('--reveal-delay', `${Math.min(position++, 3) * 70}ms`);
                entry.target.classList.add('reveal-visible');
            }
            observer.unobserve(entry.target);
        });
    }, { threshold: 0, rootMargin: '0px 0px -36px 0px' });
    document.querySelectorAll(selector).forEach(element => {
        // Éviter de cumuler l'animation d'un parent et de son enfant.
        if (!element.parentElement.closest(selector)) observer.observe(element);
    });
    document.addEventListener('focusin', event => {
        const block = event.target.closest('.reveal-visible');
        if (block) block.classList.remove('reveal-visible');
    });
    motion.addEventListener('change', event => {
        if (event.matches) {
            observer.disconnect();
            document.querySelectorAll('.reveal-visible').forEach(element => element.classList.remove('reveal-visible'));
        }
    });
})();

document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && document.getElementById('mobileMenu')?.classList.contains('open')) {
        toggleMenu();
        document.querySelector('.menu-toggle').focus();
    }
});
