(function () {
    const form = document.getElementById('signup-form');
    if (!form) return;

    const steps     = Array.from(form.querySelectorAll('.form-step'));
    const markers   = Array.from(document.querySelectorAll('.step-marker'));
    const lines     = Array.from(document.querySelectorAll('.step-line'));
    const prevBtn   = document.getElementById('prev-btn');
    const nextBtn   = document.getElementById('next-btn');
    const submitBtn = document.getElementById('submit-btn');

    const TOTAL = steps.length;
    let current = 1;

    function showStep(n, instant = false) {
        current = Math.max(1, Math.min(TOTAL, n));

        steps.forEach((s, i) => {
            if (i + 1 === current) {
                s.removeAttribute('hidden');
                if (instant) {
                    s.classList.remove('opacity-0', 'translate-y-2');
                    s.classList.add('opacity-100', 'translate-y-0');
                } else {
                    setTimeout(() => {
                        s.classList.remove('opacity-0', 'translate-y-2');
                        s.classList.add('opacity-100', 'translate-y-0');
                    }, 10);
                }
            } else {
                s.classList.remove('opacity-100', 'translate-y-0');
                s.classList.add('opacity-0', 'translate-y-2');
                if (instant) {
                    s.setAttribute('hidden', '');
                } else {
                    setTimeout(() => {
                        if (current !== i + 1) {
                            s.setAttribute('hidden', '');
                        }
                    }, 200);
                }
            }
        });

        markers.forEach((m, i) => {
            const idx    = i + 1;
            const circle = m.querySelector('.step-circle');
            const num    = m.querySelector('.step-number');
            const check  = m.querySelector('.step-check');
            const label  = m.querySelector('.step-label');

            circle.classList.remove(
                'border-gray-300', 'dark:border-gray-700', 'text-gray-400',
                'border-[#D95745]', 'bg-[#D95745]', 'text-white',
                'bg-[#D95745]/10', 'text-[#D95745]'
            );

            if (idx < current) {
                circle.classList.add('border-[#D95745]', 'bg-[#D95745]', 'text-white');
                if (num) num.hidden = true;
                if (check) check.hidden = false;
                label.classList.remove('text-gray-400');
                label.classList.add('text-[#D95745]');
            } else if (idx === current) {
                circle.classList.add('border-[#D95745]', 'bg-[#D95745]/10', 'text-[#D95745]');
                if (num) num.hidden = false;
                if (check) check.hidden = true;
                label.classList.remove('text-gray-400');
                label.classList.add('text-[#D95745]', 'font-semibold');
            } else {
                circle.classList.add('border-gray-300', 'dark:border-gray-700', 'text-gray-400');
                if (num) num.hidden = false;
                if (check) check.hidden = true;
                label.classList.remove('text-[#D95745]', 'font-semibold');
                label.classList.add('text-gray-400');
            }
        });

        lines.forEach((line, i) => {
            const done = (i + 1) < current;
            line.classList.toggle('bg-[#D95745]', done);
            line.classList.toggle('bg-gray-200', !done);
            line.classList.toggle('dark:bg-gray-800', !done);
        });

        prevBtn.classList.toggle('hidden', current === 1);
        nextBtn.hidden = (current === TOTAL);
        submitBtn.hidden = (current !== TOTAL);
    }

    function setFieldError(el, message) {
        const errEl = form.querySelector(`.error-msg[data-for="${el.name}"]`);
        if (message) {
            el.classList.add('border-red-500', 'focus:border-red-500', 'focus:ring-red-500/20');
            if (errEl) {
                errEl.textContent = message;
                errEl.hidden = false;
            }
        } else {
            el.classList.remove('border-red-500', 'focus:border-red-500', 'focus:ring-red-500/20');
            if (errEl) {
                errEl.textContent = '';
                errEl.hidden = true;
            }
        }
    }

    function validateStep(n) {
        const section = steps[n - 1];
        let ok = true;

        section.querySelectorAll('input, select').forEach(el => {
            if (el.disabled) return;
            const required = el.hasAttribute('required') || el.name !== 'alternate_phone_number';
            let message = '';

            if (required && !el.value.trim()) {
                message = 'Ce champ est requis.';
            } else if (el.type === 'email' && el.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(el.value)) {
                message = 'Adresse email invalide.';
            } else if (el.name === 'phone_number' && el.value && !/^\d{8,15}$/.test(el.value.replace(/\s+/g, ''))) {
                message = 'Numéro invalide.';
            }

            if (message) ok = false;
            setFieldError(el, message);
        });

        if (n === 4) {
            const pw  = form.querySelector('input[name="password"]');
            const cpw = form.querySelector('input[name="confirm_password"]');
            if (pw && cpw && pw.value && cpw.value && pw.value !== cpw.value) {
                ok = false;
                setFieldError(cpw, 'Les mots de passe ne correspondent pas.');
            }
        }

        return ok;
    }

    // 1. Gestion Commune -> Quartier
    const township = form.querySelector('select[name="township"]');
    const quarter  = form.querySelector('select[name="quarter"]');

    function populateQuarters(selectedTownship, selectedQuarter = '') {
        if (!quarter) return;
        const data = window.KINSHASA_QUARTIERS || {};
        const list = data[selectedTownship];

        if (Array.isArray(list) && list.length > 0) {
            quarter.innerHTML = '<option value="">Choisir un quartier</option>';
            list.forEach(q => {
                const opt = document.createElement('option');
                opt.value = q;
                opt.textContent = q;
                if (q === selectedQuarter) opt.selected = true;
                quarter.appendChild(opt);
            });
            quarter.disabled = false;
            quarter.removeAttribute('disabled');
        } else {
            quarter.innerHTML = '<option value="">Choisir d\'abord une commune</option>';
            quarter.disabled = true;
        }
    }

    if (township && quarter) {
        township.addEventListener('change', () => {
            populateQuarters(township.value);
            setFieldError(township, '');
            setFieldError(quarter, '');
        });

        if (township.value) {
            populateQuarters(township.value, quarter.value);
        }
    }

    // 2. Mise en évidence des erreurs renvoyées par le serveur au chargement
    let firstServerErrorStep = 1;
    let foundServerError = false;

    steps.forEach((section, index) => {
        section.querySelectorAll('.error-msg:not([hidden])').forEach(errEl => {
            const field = section.querySelector(`[name="${errEl.dataset.for}"]`);
            if (field && errEl.textContent.trim()) {
                field.classList.add('border-red-500', 'focus:border-red-500', 'focus:ring-red-500/20');
                if (!foundServerError) {
                    firstServerErrorStep = index + 1;
                    foundServerError = true;
                }
            }
        });
    });

    const errorSummary = document.getElementById('signup-error-summary');
    if (!foundServerError && errorSummary) {
        const firstErrorLink = errorSummary.querySelector('[data-error-target]');
        const firstErrorField = firstErrorLink ? document.getElementById(firstErrorLink.dataset.errorTarget) : null;
        if (firstErrorField) {
            const stepIdx = steps.indexOf(firstErrorField.closest('.form-step')) + 1;
            if (stepIdx > 0) firstServerErrorStep = stepIdx;
        }
    }

    showStep(firstServerErrorStep, true);

    errorSummary?.addEventListener('click', (event) => {
        const link = event.target.closest('[data-error-target]');
        if (!link) return;

        const field = document.getElementById(link.dataset.errorTarget);
        const section = field?.closest('.form-step');
        const step = steps.indexOf(section) + 1;
        if (!field || step < 1) return;

        event.preventDefault();
        showStep(step, true);
        field.focus();
        field.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });

    nextBtn.addEventListener('click', () => {
        if (!validateStep(current)) return;
        showStep(current + 1);
    });

    prevBtn.addEventListener('click', () => {
        showStep(current - 1);
    });

    form.addEventListener('submit', (e) => {
        for (let step = 1; step <= TOTAL; step++) {
            if (!validateStep(step)) {
                e.preventDefault();
                showStep(step, true);
                const firstInvalid = steps[step - 1].querySelector('.border-red-500');
                firstInvalid?.focus();
                return;
            }
        }
    });
})();