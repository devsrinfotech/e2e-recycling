(function () {
  'use strict';
  var form = document.getElementById('brief-form');
  var result = document.getElementById('brief-result');
  var output = document.getElementById('brief-output');
  var email = document.getElementById('brief-email');
  var status = document.getElementById('brief-status');
  var baseEmail = 'mailto:info@e2erecycling.com?subject=Corporate%20IT%20disposal%20and%20data%20erasure%20enquiry';
  var preparedEmail = baseEmail;
  function updateEmail() {
    var uri = baseEmail + '&body=' + encodeURIComponent(output.value);
    preparedEmail = uri.length < 1900 ? uri : baseEmail;
    // Keep form contents out of link URLs inspected by automatic click analytics.
    email.href = baseEmail;
    status.textContent = uri.length < 1900 ? 'Review your brief, then open your email app to send it.' : 'Your brief is long. Copy it into your email or attach the downloaded text file.';
  }
  form.addEventListener('submit', function (event) {
    event.preventDefault();
    var data = new FormData(form);
    if (!data.get('company').trim()) {
      status.textContent = 'Please enter your company name.';
      result.hidden = false;
      document.getElementById('brief-company').focus();
      return;
    }
    output.value = [
      'Corporate IT retirement / data erasure enquiry',
      'Company: ' + data.get('company').trim(),
      'Cities / locations: ' + data.get('cities').trim(),
      'Requirement: ' + data.get('service'),
      'Equipment / counts: ' + data.get('equipment').trim(),
      'Data handling: ' + data.get('data'),
      'Processing location: ' + data.get('site'),
      'Timing / access / reporting: ' + (data.get('timing').trim() || 'To be discussed'),
      '',
      'Please confirm feasibility, scope, handling, reporting, timing and quotation.'
    ].join('\n');
    result.hidden = false;
    updateEmail();
    output.focus();
    if (window.gtag) window.gtag('event', 'brief_prepared', { page_path: location.pathname });
  });
  output.addEventListener('input', updateEmail);
  email.addEventListener('click', function (event) {
    event.preventDefault();
    window.location.href = preparedEmail;
  });
  document.getElementById('brief-copy').addEventListener('click', async function () {
    try {
      await navigator.clipboard.writeText(output.value);
      status.textContent = 'Brief copied. Paste it into your email or internal project document.';
    } catch (_) {
      output.focus();
      output.select();
      status.textContent = 'The brief is selected. Use your device’s copy command.';
    }
  });
  document.getElementById('brief-download').addEventListener('click', function () {
    var url = URL.createObjectURL(new Blob([output.value], { type: 'text/plain;charset=utf-8' }));
    var anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = 'corporate-it-project-brief.txt';
    anchor.click();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
    status.textContent = 'Brief downloaded. You can attach it to your enquiry.';
  });
})();
