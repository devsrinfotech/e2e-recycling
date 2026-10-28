const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('assets/js/contact.js', 'utf8');

function setup(response, token = 'verified-token') {
  const handlers = {}, events = [], requests = [];
  const button = { disabled: false };
  const status = { textContent: '', setAttribute() {}, focus() {} };
  const names = ['contact_name', 'company', 'work_email', 'phone', 'city_locations', 'asset_types_volume', 'requirement_details', 'website'];
  const elements = Object.fromEntries(names.map(name => [name, { value: name === 'website' ? '' : '  example  ' }]));
  ['project_service', 'data_preference', 'processing_location', 'project_timing'].forEach(name => { elements[name] = { value: '' }; });
  const form = {
    elements, querySelector: () => button, reportValidity: () => true,
    addEventListener: (name, fn) => { handlers[name] = fn; },
    setAttribute() {}, removeAttribute() {},
    reset() { Object.values(elements).forEach(input => { input.value = ''; }); }
  };
  let resets = 0;
  const context = {
    URLSearchParams, AbortController, setTimeout, clearTimeout,
    document: { getElementById: id => id === 'corporate-contact-form' ? form : id === 'contact-status' ? status : { focus() {} },
      createElement: () => ({}), head: { appendChild() {} } },
    fetch: async (url, options) => { requests.push({ url, options }); return typeof response === 'function' ? response() : response; },
    window: { matchMedia: () => ({ matches: false }), grecaptcha: { render: () => 0, getResponse: () => token, reset: () => { resets++; } },
      gtag: (...args) => events.push(args) }
  };
  vm.runInNewContext(source, context);
  context.window.e2eCaptchaReady();
  return { form, button, status, requests, events, resets: () => resets, submit: () => handlers.submit({ preventDefault() {} }) };
}

(async () => {
  const ok = setup({ ok: true, json: async () => ({ message: { ok: true } }) });
  await ok.submit();
  assert.equal(ok.requests[0].options.credentials, 'omit');
  assert.equal(ok.requests[0].options.body.get('contact_name'), 'example');
  assert.equal(ok.requests[0].options.body.get('recaptcha_response'), 'verified-token');
  assert.equal(ok.requests[0].options.body.get('requirement_details'), 'example');
  assert.equal(ok.form.elements.company.value, '');
  assert.match(ok.status.textContent, /reached the e2e team/);
  assert.deepEqual(JSON.parse(JSON.stringify(ok.events)), [['event', 'generate_lead', { form_name: 'corporate_assessment' }]]);
  assert.equal(ok.resets(), 1);

  const detailed = setup({ ok: true, json: async () => ({ message: { ok: true } }) });
  const extra = {
    project_service: 'Data erasure and recycling',
    data_preference: 'Blancco erasure workflow requested',
    processing_location: 'Media must remain onsite; assess feasibility',
    project_timing: 'Monday pickup\nReport to IT & procurement'
  };
  for (const [name, value] of Object.entries(extra)) detailed.form.elements[name].value = value;
  await detailed.submit();
  const scope = detailed.requests[0].options.body.get('requirement_details');
  for (const value of Object.values(extra)) assert.ok(scope.includes(value));
  assert.match(scope, /Data handling preference: Blancco/);
  for (const name of Object.keys(extra)) assert.equal(detailed.requests[0].options.body.has(name), false);
  assert.equal(scope.startsWith('example\n\nMain requirement:'), true);

  const oversized = setup(null);
  oversized.form.elements.requirement_details.value = 'x'.repeat(1950);
  oversized.form.elements.project_timing.value = 'x'.repeat(100);
  await oversized.submit();
  assert.equal(oversized.requests.length, 0);
  assert.match(oversized.status.textContent, /2,000 characters/);
  assert.equal(oversized.form.elements.project_timing.value.length, 100);

  const absent = setup(null, '');
  await absent.submit();
  assert.equal(absent.requests.length, 0);
  assert.match(absent.status.textContent, /complete the reCAPTCHA/);

  const rejected = setup({ ok: false, status: 400, json: async () => ({ message: { ok: false, message: 'Verification failed.' } }) });
  await rejected.submit();
  assert.equal(rejected.status.textContent, 'Verification failed.');
  assert.equal(rejected.form.elements.company.value, '  example  ');
  assert.equal(rejected.events.length, 0);
  assert.equal(rejected.button.disabled, false);

  const limited = setup({ ok: false, status: 429, json: async () => ({}) });
  await limited.submit();
  assert.match(limited.status.textContent, /10 minutes/);

  let complete;
  const pending = setup(() => new Promise(resolve => { complete = resolve; }));
  const first = pending.submit();
  assert.equal(pending.button.disabled, true);
  await pending.submit();
  assert.equal(pending.requests.length, 1);
  complete({ ok: true, json: async () => ({ message: { ok: true } }) });
  await first;
  assert.equal(pending.button.disabled, false);
  console.log('Contact form: optional project details, length guard, success, privacy, missing CAPTCHA, rejection, rate limit and duplicate-click checks passed.');
})().catch(error => { console.error(error); process.exitCode = 1; });
