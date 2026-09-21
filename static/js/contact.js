(() => {
    const form = document.getElementById('contact-form');
    if (!form) return;
    const button = form.querySelector('button[type="submit"]');
    const feedback = document.getElementById('contact-feedback');
    let sending = false;
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        if (sending) return;
        sending = true;
        const label = button.textContent;
        button.disabled = true;
        button.textContent = 'Envoi en cours…';
        form.setAttribute('aria-busy', 'true');
        feedback.hidden = true;
        form.querySelectorAll('[aria-invalid]').forEach(field => field.removeAttribute('aria-invalid'));
        try {
            const response = await fetch(form.action, {
                method: 'POST', body: new FormData(form), credentials: 'same-origin',
                headers: {'X-CSRFToken': form.elements.csrfmiddlewaretoken.value,
                    'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'},
                signal: AbortSignal.timeout(25000),
            });
            const data = await response.json();
            const lines = [data.message];
            if (data.errors) Object.entries(data.errors).forEach(([name, errors]) => {
                const field = form.elements.namedItem(name);
                if (field) field.setAttribute('aria-invalid', 'true');
                errors.forEach(error => lines.push(error.message));
            });
            feedback.textContent = lines.join(' ');
            if (response.ok && data.success) form.reset();
        } catch (error) {
            feedback.textContent = 'Impossible de confirmer l’envoi. Vérifiez votre connexion et réessayez plus tard.';
        } finally {
            feedback.hidden = false;
            button.disabled = false;
            button.textContent = label;
            form.removeAttribute('aria-busy');
            sending = false;
        }
    });
})();
