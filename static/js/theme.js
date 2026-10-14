// Exécuté avant la feuille de style pour éviter un flash du mauvais thème.
(() => {
    const system = window.matchMedia('(prefers-color-scheme: dark)');
    let preference = null;
    try { preference = localStorage.getItem('gscom-theme'); } catch (_) {}
    if (!['light', 'dark'].includes(preference)) preference = null;
    function apply() {
        const theme = preference || (system.matches ? 'dark' : 'light');
        document.documentElement.dataset.theme = theme;
        const button = document.querySelector('.theme-toggle');
        if (button) {
            button.hidden = false;
            button.setAttribute('aria-pressed', String(theme === 'dark'));
            const label = theme === 'dark' ? 'Activer le mode clair' : 'Activer le mode sombre';
            button.setAttribute('aria-label', label);
            button.title = label;
        }
        const meta = document.querySelector('meta[name="theme-color"]');
        if (meta) meta.content = theme === 'dark' ? '#191c22' : '#c0392b';
    }
    apply();
    system.addEventListener('change', apply);
    window.addEventListener('storage', event => {
        if (event.key === 'gscom-theme' || event.key === null) {
            preference = ['light', 'dark'].includes(event.newValue) ? event.newValue : null;
            apply();
        }
    });
    document.addEventListener('DOMContentLoaded', () => {
        apply();
        document.querySelector('.theme-toggle')?.addEventListener('click', () => {
            preference = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
            try { localStorage.setItem('gscom-theme', preference); } catch (_) {}
            apply();
        });
    });
})();
