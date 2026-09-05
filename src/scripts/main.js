/* Zili-style B2B supplement site — memory-state JS (sandbox-safe: no localStorage/fetch/alert) */
(function () {
  'use strict';

  /* ---------- Mobile nav toggle (in-memory open state) ---------- */
  var navToggle = document.getElementById('navToggle');
  var mainNav = document.getElementById('mainNav');
  var navOpen = false;

  if (navToggle && mainNav) {
    navToggle.addEventListener('click', function () {
      navOpen = !navOpen;
      mainNav.classList.toggle('open', navOpen);
      navToggle.setAttribute('aria-expanded', navOpen ? 'true' : 'false');
      navToggle.setAttribute('aria-label', navOpen ? 'Close menu' : 'Open menu');
    });
    /* close on link click (same-document anchor navigation) */
    mainNav.addEventListener('click', function (e) {
      if (e.target && e.target.closest && e.target.closest('a')) {
        navOpen = false;
        mainNav.classList.remove('open');
        navToggle.setAttribute('aria-expanded', 'false');
        navToggle.setAttribute('aria-label', 'Open menu');
      }
    });
  }

  /* ---------- Restrained reveal (skipped under reduced motion) ---------- */
  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!reduceMotion && 'IntersectionObserver' in window) {
    var revealEls = document.querySelectorAll('.reveal');
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('in-view');
          observer.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -10% 0px' });
    revealEls.forEach(function (el) { observer.observe(el); });
  } else {
    document.querySelectorAll('.reveal').forEach(function (el) { el.classList.add('in-view'); });
  }

  /* ---------- Contact form: validation with in-memory error/success states ---------- */
  var form = document.getElementById('quoteForm');
  var statusBox = document.getElementById('formStatus');

  function setStatus(type, message) {
    if (!statusBox) return;
    statusBox.className = 'form-status ' + type;
    statusBox.setAttribute('role', type === 'error' ? 'alert' : 'status');
    var icon = statusBox.querySelector('.status-icon');
    var text = statusBox.querySelector('.status-text');
    if (icon && type === 'success') icon.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 12.5l5 5L20 6.5"/></svg>';
    if (icon && type === 'error') icon.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7.5v5"/><path d="M12 16.5h.01"/></svg>';
    if (text) text.textContent = message;
  }

  function clearFieldErrors() {
    form.querySelectorAll('.has-error').forEach(function (field) {
      field.classList.remove('has-error');
    });
  }

  function markError(fieldName, message) {
    var fieldGroup = form.querySelector('[data-field="' + fieldName + '"]');
    if (fieldGroup) {
      fieldGroup.classList.add('has-error');
      var errEl = fieldGroup.querySelector('.field-error');
      if (errEl) errEl.textContent = message;
    }
  }

  function validateField(name, value) {
    var v = (value || '').trim();
    if (name === 'name' && !v) return 'Please enter your name.';
    if (name === 'email') {
      if (!v) return 'Please enter your business email.';
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v)) return 'Please enter a valid email address.';
    }
    if (name === 'company' && !v) return 'Please enter your company name.';
    if (name === 'market' && !v) return 'Please select a target market.';
    if (name === 'message' && v.length < 10) return 'Please describe your inquiry (at least 10 characters).';
    return '';
  }

  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      clearFieldErrors();

      var fields = ['name', 'email', 'company', 'market', 'message'];
      var invalid = 0;
      fields.forEach(function (name) {
        var input = form.querySelector('[name="' + name + '"]');
        var err = input ? validateField(name, input.value) : 'required';
        if (err) { markError(name, err); invalid += 1; }
      });

      if (invalid > 0) {
        setStatus('error', 'Please fix the highlighted fields and submit again.');
        return;
      }

      /* Success state — no server submission on this static sample site */
      var marketSel = form.querySelector('[name="market"]');
      var marketLabel = marketSel && marketSel.options && marketSel.selectedIndex > 0
        ? marketSel.options[marketSel.selectedIndex].text
        : 'Global';
      setStatus('success', 'Thank you — your inquiry is ready. This is a sample contact form on a static demo site; connect the form to your email or CRM before go-live. We will respond to ' + marketLabel + ' inquiries within one business day outline.');
      form.reset();
    });

    /* live clear of error on input */
    form.querySelectorAll('input, textarea, select').forEach(function (input) {
      input.addEventListener('input', function () {
        var group = form.querySelector('[data-field="' + (input.getAttribute('name') || '') + '"]');
        if (group) group.classList.remove('has-error');
      });
      input.addEventListener('change', function () {
        var group = form.querySelector('[data-field="' + (input.getAttribute('name') || '') + '"]');
        if (group) group.classList.remove('has-error');
      });
    });
  }

  /* ---------- Footer year (static date fallback) ---------- */
  var yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());
})();