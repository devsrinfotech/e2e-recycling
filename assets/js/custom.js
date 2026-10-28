/* Native navigation and FAQ interactions: no animation or plugin dependency. */
(function () {
  'use strict';
  var trigger = document.querySelector('.menu-trigger');
  var nav = document.querySelector('.header-area .nav');
  var header = document.querySelector('.header-area');
  var submenuButtons = document.querySelectorAll('.submenu-toggle');
  if (nav) {
    var currentPage = location.pathname.split('/').pop() || 'index.html';
    var matched = false;
    nav.querySelectorAll('a').forEach(function (link) {
      var url = new URL(link.href);
      if (!url.hash && url.pathname.split('/').pop() === currentPage) {
        link.setAttribute('aria-current', 'page');
        var group = link.closest('.submenu') || link.closest('li');
        group.classList.add('is-current');
        matched = true;
      }
    });
    if (!matched && document.querySelector('.blog-post-thumb.big')) {
      var blogs = nav.querySelector('a[href="blogs.html"]');
      if (blogs) blogs.closest('li').classList.add('is-current');
    }
  }
  function closeSubmenus() {
    submenuButtons.forEach(function (button) {
      button.setAttribute('aria-expanded', 'false');
      button.parentElement.classList.remove('is-expanded');
    });
  }
  submenuButtons.forEach(function (button) {
    button.addEventListener('click', function () {
      var open = button.getAttribute('aria-expanded') !== 'true';
      closeSubmenus();
      button.setAttribute('aria-expanded', String(open));
      button.parentElement.classList.toggle('is-expanded', open);
    });
  });
  document.addEventListener('click', function (event) {
    if (header && !header.contains(event.target)) closeSubmenus();
  });
  function updateHeader() {
    if (header) header.classList.toggle('header-sticky', window.innerWidth > 991 && window.scrollY >= 30);
  }
  updateHeader();
  window.addEventListener('scroll', updateHeader, { passive:true });
  window.addEventListener('resize', updateHeader, { passive:true });
  function closeMenu() {
    closeSubmenus();
    if (!trigger || !nav) return;
    trigger.classList.remove('active');
    trigger.setAttribute('aria-expanded', 'false');
    nav.classList.remove('is-open');
  }
  if (trigger && nav) {
    nav.id = 'primary-navigation';
    trigger.setAttribute('aria-controls', nav.id);
    trigger.setAttribute('aria-expanded', 'false');
    trigger.addEventListener('click', function () {
      var open = trigger.getAttribute('aria-expanded') !== 'true';
      trigger.classList.toggle('active', open);
      trigger.setAttribute('aria-expanded', String(open));
      nav.classList.toggle('is-open', open);
    });
    nav.addEventListener('click', function (event) { if (event.target.closest('a')) closeMenu(); });
    document.addEventListener('keydown', function (event) { if (event.key === 'Escape') closeMenu(); });
    window.addEventListener('resize', closeMenu, { passive:true });
  }
  document.querySelectorAll('.accordion-button[data-bs-target]').forEach(function (button) {
    button.addEventListener('click', function () {
      var panel = document.querySelector(button.getAttribute('data-bs-target'));
      if (!panel) return;
      var open = button.getAttribute('aria-expanded') !== 'true';
      var group = button.closest('.accordion');
      if (group) group.querySelectorAll('.accordion-button').forEach(function (other) {
        other.classList.add('collapsed');
        other.setAttribute('aria-expanded', 'false');
        var target = document.querySelector(other.getAttribute('data-bs-target'));
        if (target) target.classList.remove('show');
      });
      button.classList.toggle('collapsed', !open);
      button.setAttribute('aria-expanded', String(open));
      panel.classList.toggle('show', open);
    });
  });
})();
