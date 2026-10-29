(function () {
    const form = document.getElementById('signup-form');
    if (!form) return;

    const steps       = Array.from(form.querySelectorAll('.form-step'));
    const markers     = Array.from(document.querySelectorAll('.step-marker'));
    const lines       = Array.from(document.querySelectorAll('.step-line'));
    const prevBtn     = document.getElementById('prev-btn');
    const nextBtn     = document.getElementById('next-btn');
    const submitBtn   = document.getElementById('submit-btn');

    const TOTAL       = steps.length;
    let current       = 1;

    function showStep(n) {
        current = Math.max(1, Math.min(TOTAL, n));

        steps.forEach((s, i) => {
            if (i + 1 === current) {
                s.removeAttribute('hidden');
                setTimeout(() => {
                    s.classList.remove('opacity-0', 'translate-y-2');
                    s.classList.add('opacity-100', 'translate-y-0');
                }, 10);
            } else {
                s.classList.remove('opacity-100', 'translate-y-0');
                s.classList.add('opacity-0', 'translate-y-2');
                setTimeout(() => {
                    if (current !== i + 1) {
                        s.setAttribute('hidden', '');
                    }
                }, 200);
            }
        });

        // Update step circles & check icons
        markers.forEach((m, i) => {
            const idx     = i + 1;
            const circle  = m.querySelector('.step-circle');
            const num     = m.querySelector('.step-number');
            const check   = m.querySelector('.step-check');
            const label   = m.querySelector('.step-label');

            circle.classList.remove(
                'border-gray-300','dark:border-gray-700','text-gray-400',
                'border-[#D95745]','bg-[#D95745]','text-white',
                'bg-[#D95745]/10','text-[#D95745]'
            );

            if (idx < current) {
                // Completed step -> show check icon
                circle.classList.add('border-[#D95745]','bg-[#D95745]','text-white');
                if (num) num.hidden = true;
                if (check) check.hidden = false;
                label.classList.remove('text-gray-400');
                label.classList.add('text-[#D95745]');
            } else if (idx === current) {
                // Current step -> show number
                circle.classList.add('border-[#D95745]','bg-[#D95745]/10','text-[#D95745]');
                if (num) num.hidden = false;
                if (check) check.hidden = true;
                label.classList.remove('text-gray-400');
                label.classList.add('text-[#D95745]', 'font-semibold');
            } else {
                // Future step -> show number
                circle.classList.add('border-gray-300','dark:border-gray-700','text-gray-400');
                if (num) num.hidden = false;
                if (check) check.hidden = true;
                label.classList.remove('text-[#D95745]','font-semibold');
                label.classList.add('text-gray-400');
            }
        });

        // Update progress lines
        lines.forEach((line, i) => {
            const done = (i + 1) < current;
            line.classList.toggle('bg-[#D95745]', done);
            line.classList.toggle('bg-gray-200', !done);
            line.classList.toggle('dark:bg-gray-800', !done);
        });

        // Hide "Précédent" button on the first step
        if (current === 1) {
            prevBtn.classList.add('hidden');
        } else {
            prevBtn.classList.remove('hidden');
        }

        if (current === TOTAL) {
            nextBtn.hidden = true;
            submitBtn.hidden = false;
        } else {
            nextBtn.hidden = false;
            submitBtn.hidden = true;
        }
    }

    function validateStep(n) {
        const section = steps[n - 1];
        let ok = true;

        section.querySelectorAll('.error-msg').forEach(p => {
            p.textContent = '';
            p.hidden = true;
        });
        section.querySelectorAll('input,select').forEach(el => {
            el.classList.remove('border-red-500','focus:border-red-500','focus:ring-red-500/20');
        });

        section.querySelectorAll('input,select').forEach(el => {
            if (el.disabled) return;
            const required = el.hasAttribute('required') || el.name !== 'alternate_phone_number';
            const errEl    = section.querySelector(`.error-msg[data-for="${el.name}"]`);

            let message = '';
            if (required && !el.value.trim()) {
                message = 'Ce champ est requis.';
            } else if (el.type === 'email' && el.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(el.value)) {
                message = 'Adresse email invalide.';
            } else if (el.name === 'phone_number' && el.value && !/^\d{8,15}$/.test(el.value.replace(/\s+/g,''))) {
                message = 'Numéro invalide.';
            }

            if (message) {
                ok = false;
                el.classList.add('border-red-500','focus:border-red-500','focus:ring-red-500/20');
                if (errEl) {
                    errEl.textContent = message;
                    errEl.hidden = false;
                }
            }
        });

        if (n === 4) {
            const pw  = form.querySelector('input[name="password"]');
            const cpw = form.querySelector('input[name="confirm_password"]');
            if (pw.value && cpw.value && pw.value !== cpw.value) {
                ok = false;
                cpw.classList.add('border-red-500','focus:border-red-500');
                const errEl = section.querySelector('.error-msg[data-for="confirm_password"]');
                if (errEl) {
                    errEl.textContent = 'Les mots de passe ne correspondent pas.';
                    errEl.hidden = false;
                }
            }
        }

        return ok;
    }

    showStep(1);

    nextBtn.addEventListener('click', () => {
        if (!validateStep(current)) return;
        showStep(current + 1);
    });

    prevBtn.addEventListener('click', () => {
        showStep(current - 1);
    });

    // Cascading Commune -> Quartier
    const township = form.querySelector('select[name="township"]');
    const quater   = form.querySelector('select[name="quater"]');

    if (township && quater) {
        township.addEventListener('change', () => {
            quater.innerHTML = '<option value="">Choisir un quartier</option>';
            quater.disabled = true;

            const selectedTownship = township.value;
            if (window.KINSHASA_QUARTIERS && window.KINSHASA_QUARTIERS[selectedTownship]) {
                window.KINSHASA_QUARTIERS[selectedTownship].forEach(q => {
                    const opt = document.createElement('option');
                    opt.value = q;
                    opt.textContent = q;
                    quater.appendChild(opt);
                });
                quater.disabled = false;
            }
        });

        if (township.value && window.KINSHASA_QUARTIERS && window.KINSHASA_QUARTIERS[township.value]) {
            quater.disabled = false;
        }
    }

    form.addEventListener('submit', (e) => {
        if (!validateStep(TOTAL)) {
            e.preventDefault();
            showStep(TOTAL);
        }
    });
})();