
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
        const sections = document.querySelectorAll('section[id], div[id]:not(#contact-feedback)');
        const navLinks = document.querySelectorAll('nav ul li a');

        window.addEventListener('scroll', () => {
            let current = '';
            sections.forEach(section => {
                if (window.scrollY >= section.offsetTop - 80) {
                    current = section.getAttribute('id');
                }
            });
            navLinks.forEach(link => {
                link.classList.remove('active');
                if (new URL(link.href).pathname === window.location.pathname && new URL(link.href).hash === '#' + current) {
                    link.classList.add('active');
                }
            });
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

// Une seule apparition par élément, sans masquer le contenu avant JavaScript.
(() => {
    const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (motion.matches || !('IntersectionObserver' in window)) return;
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (!entry.isIntersecting) return;
            if (!motion.matches) entry.target.classList.add('reveal-visible');
            observer.unobserve(entry.target);
        });
    }, { threshold: 0.08 });
    document.querySelectorAll('.news-card, .formation-card, .feature, .img_about, .content, .vie_scolaire_content2 > div, .main-member, .dir-card, .ens-card, .testi-card, .contact-info, .contact-form-wrap').forEach(element => observer.observe(element));
})();

document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && document.getElementById('mobileMenu')?.classList.contains('open')) {
        toggleMenu();
        document.querySelector('.menu-toggle').focus();
    }
});
