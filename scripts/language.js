const userLang = new URLSearchParams(location.search).get('lang') || 'hu';
fetch(`lang/${userLang}.json`)  // <-- relatív útvonal
    .then(r => {
        if (!r.ok) throw new Error(`Translation file not found: ${userLang}`);
        return r.json();
    })
    .then(strings => {
        document.querySelectorAll('[data-i18n]').forEach(el => {
            el.textContent = strings[el.dataset.i18n] || el.textContent;
        });
    })
    .catch(err => console.error(err));

/* Példa: https://domain.tdl/en/ -> 'en'
const pathParts = window.location.pathname.split('/').filter(Boolean);
const userLang = pathParts[0] || 'en'
fetch(`/lang/${userLang}.json`)
    .then(r => {
        if (!r.ok) throw new Error(`Translation file not found: ${userLang}`);
        return r.json();
    })
    .then(strings => {
        document.querySelectorAll('[data-i18n]').forEach(el => {
            el.textContent = strings[el.dataset.i18n] || el.textContent;
        });
    })
    .catch(err => console.error(err)); */