/* Measure contact intent without sending form contents or personal data to analytics. */
(function () {
  'use strict';
  if (typeof window.gtag !== 'function') {
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', 'G-P57BF6R1W2');
    var tag = document.createElement('script');
    tag.async = true;
    tag.src = 'https://www.googletagmanager.com/gtag/js?id=G-P57BF6R1W2';
    document.head.appendChild(tag);
  }
  document.addEventListener('click', function (event) {
    var anchor = event.target.closest('a');
    if (!anchor) return;
    var href = anchor.getAttribute('href') || '';
    var method = href.startsWith('mailto:') ? 'email' : href.startsWith('tel:') ? 'phone' : '';
    if (method) window.gtag('event', 'contact_intent', { contact_method: method, page_path: location.pathname, transport_type: 'beacon' });
    if (anchor.hasAttribute('download') || href.startsWith('assets/downloads/')) {
      window.gtag('event', 'resource_download', { resource_name: href.split('/').pop(), page_path: location.pathname });
    }
  });
})();
