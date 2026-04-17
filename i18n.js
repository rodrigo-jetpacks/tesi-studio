// i18n — language detection and switching

(function () {
  const SUPPORTED = ['en', 'es'];
  const STORAGE_KEY = 'tesi-lang';
  const cache = {};

  // Detect language: saved preference > browser language > default English
  function detectLang() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved && SUPPORTED.includes(saved)) return saved;

    const browserLang = (navigator.language || '').slice(0, 2).toLowerCase();
    return SUPPORTED.includes(browserLang) ? browserLang : 'en';
  }

  // Resolve a dot-notated key like "hero.title" from an object
  function resolve(obj, key) {
    return key.split('.').reduce((o, k) => (o ? o[k] : undefined), obj);
  }

  // Load a language JSON (cached)
  async function load(lang) {
    if (cache[lang]) return cache[lang];
    const res = await fetch(`i18n/${lang}.json`);
    cache[lang] = await res.json();
    return cache[lang];
  }

  // Apply translations to the DOM
  function apply(translations) {
    // data-i18n → textContent
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const val = resolve(translations, el.dataset.i18n);
      if (val) el.textContent = val;
    });

    // data-i18n-html → innerHTML (for <br>, <em>, etc.)
    document.querySelectorAll('[data-i18n-html]').forEach(el => {
      const val = resolve(translations, el.dataset.i18nHtml);
      if (val) el.innerHTML = val;
    });

    // data-i18n-attr → attribute values (e.g. "content:meta.description")
    document.querySelectorAll('[data-i18n-attr]').forEach(el => {
      el.dataset.i18nAttr.split(';').forEach(pair => {
        const [attr, key] = pair.split(':');
        const val = resolve(translations, key);
        if (val) el.setAttribute(attr, val);
      });
    });

    // Update <title>
    const title = resolve(translations, 'meta.title');
    if (title) document.title = title;
  }

  // Set language
  async function setLang(lang) {
    const translations = await load(lang);
    apply(translations);
    document.documentElement.lang = lang;
    localStorage.setItem(STORAGE_KEY, lang);

    // Update toggle button label to show the OTHER language
    const btn = document.getElementById('lang-toggle');
    if (btn) {
      const otherLang = lang === 'es' ? 'EN' : 'ES';
      btn.querySelector('.lang-toggle__label').textContent = otherLang;
    }
  }

  // Initialize
  const currentLang = detectLang();
  setLang(currentLang);

  // Toggle button
  const btn = document.getElementById('lang-toggle');
  if (btn) {
    btn.addEventListener('click', () => {
      const now = document.documentElement.lang;
      setLang(now === 'es' ? 'en' : 'es');
    });
  }
})();
