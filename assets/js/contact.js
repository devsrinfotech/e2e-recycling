(function () {
  'use strict';
  var form = document.getElementById('corporate-contact-form');
  if (!form) return;
  var status = document.getElementById('contact-status');
  var submit = form.querySelector('button[type="submit"]');
  var widget;
  var busy = false;
  var endpoint = 'https://e2e.srinfotech.biz/api/method/erpnext.crm.doctype.e2e_website_leads.website_api.submit';
  var siteKey = '6LcpwAQuAAAAAL0Bcj0j0uDE3AyqYDmOQnEaZ3Lb';

  function announce(message, error) {
    status.textContent = message;
    status.setAttribute('data-error', error ? 'true' : 'false');
  }
  function resetCaptcha() {
    if (widget !== undefined && window.grecaptcha) window.grecaptcha.reset(widget);
  }
  window.e2eCaptchaReady = function () {
    widget = window.grecaptcha.render('contact-captcha', {
      sitekey: siteKey,
      size: window.matchMedia('(max-width: 360px)').matches ? 'compact' : 'normal',
      callback: function () { announce('', false); },
      'expired-callback': function () { announce('The verification expired. Please check reCAPTCHA again.', true); },
      'error-callback': function () { announce('Verification could not load. Please retry or email info@e2erecycling.com.', true); }
    });
  };
  // Load Google's widget only when someone reaches or starts the form.
  var loaded = false;
  function loadCaptcha() {
    if (loaded) return;
    loaded = true;
    var script = document.createElement('script');
    script.src = 'https://www.google.com/recaptcha/api.js?onload=e2eCaptchaReady&render=explicit';
    script.async = true;
    script.defer = true;
    script.onerror = function () {
      loaded = false;
      script.remove();
      announce('Verification could not load. Focus a form field to retry, or email info@e2erecycling.com.', true);
    };
    document.head.appendChild(script);
  }
  form.addEventListener('focusin', loadCaptcha);
  if ('IntersectionObserver' in window) {
    var observer = new IntersectionObserver(function (entries) {
      if (entries.some(function (entry) { return entry.isIntersecting; })) {
        loadCaptcha();
        observer.disconnect();
      }
    }, { rootMargin: '200px' });
    observer.observe(form);
  } else loadCaptcha();

  form.addEventListener('submit', async function (event) {
    event.preventDefault();
    if (busy || !form.reportValidity()) return;
    var token = widget !== undefined && window.grecaptcha ? window.grecaptcha.getResponse(widget) : '';
    if (!token) {
      loadCaptcha();
      announce('Please complete the reCAPTCHA check before sending your enquiry.', true);
      document.getElementById('contact-captcha').focus();
      return;
    }
    var body = new URLSearchParams();
    ['contact_name', 'company', 'work_email', 'phone', 'city_locations', 'asset_types_volume', 'requirement_details', 'website'].forEach(function (name) {
      body.set(name, form.elements[name].value.trim());
    });
    body.set('recaptcha_response', token);
    busy = true;
    submit.disabled = true;
    form.setAttribute('aria-busy', 'true');
    announce('Sending your enquiry…', false);
    var controller = new AbortController();
    var timeout = setTimeout(function () { controller.abort(); }, 20000);
    try {
      var response = await fetch(endpoint, { method: 'POST', body: body, credentials: 'omit', signal: controller.signal });
      var data = await response.json().catch(function () { return null; });
      if (!response.ok || !data || !data.message || data.message.ok !== true) {
        if (response.status === 429) throw new Error('You have made several attempts. Please wait 10 minutes or email info@e2erecycling.com.');
        throw new Error(data && data.message && typeof data.message.message === 'string' ? data.message.message : 'We could not confirm your enquiry. Please retry or email info@e2erecycling.com.');
      }
      form.reset();
      announce('Thank you. Your enquiry has reached the e2e team. We’ll contact you using the details you provided.', false);
      status.focus();
      if (typeof window.gtag === 'function') window.gtag('event', 'generate_lead', { form_name: 'corporate_assessment' });
    } catch (error) {
      announce(error.name === 'AbortError' || error instanceof TypeError ? 'We could not confirm delivery. Your details are still here. Please contact info@e2erecycling.com before resending if you are unsure.' : error.message, true);
      status.focus();
    } finally {
      clearTimeout(timeout);
      resetCaptcha();
      busy = false;
      submit.disabled = false;
      form.removeAttribute('aria-busy');
    }
  });
}());
