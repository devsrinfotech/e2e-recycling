// Exercise the actual brief script without launching an email client or sending data.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const elements = new Map();
function element(id) {
  if (!elements.has(id)) elements.set(id, { value:'', hidden:true, handlers:{}, addEventListener(name, fn) { this.handlers[name] = fn; }, focus() {} });
  return elements.get(id);
}
const data = { company:'Example IT Company', cities:'Bengaluru & Chennai', service:'Data erasure only; retain equipment', equipment:'12 SSDs & 3 laptops', data:'TruWipe erasure workflow requested', site:'Discuss handling and processing location', timing:'' };
const events = [];
const location = { pathname:'/it-disposal-brief.html', href:'' };
const context = { document:{ getElementById:element }, window:{ location, gtag:(...args) => events.push(args) }, location, FormData:class { get(name) { return data[name]; } } };
vm.runInNewContext(fs.readFileSync('assets/js/brief.js','utf8'), context);
element('brief-form').handlers.submit({ preventDefault() {} });
assert.equal(element('brief-result').hidden, false);
assert.match(element('brief-output').value, /Bengaluru & Chennai/);
assert.match(element('brief-output').value, /TruWipe/);
assert.ok(!element('brief-email').href.includes('body='), 'Personal scope must not appear in the link URL');
element('brief-email').handlers.click({ preventDefault() {} });
assert.equal(new URL(location.href).searchParams.get('body'), element('brief-output').value);
element('brief-output').value = 'Edited scope: π / &';
element('brief-output').handlers.input();
element('brief-email').handlers.click({ preventDefault() {} });
assert.equal(new URL(location.href).searchParams.get('body'), 'Edited scope: π / &');
element('brief-output').value = '&'.repeat(1000);
element('brief-output').handlers.input();
element('brief-email').handlers.click({ preventDefault() {} });
assert.equal(new URL(location.href).searchParams.has('body'), false);
assert.match(element('brief-status').textContent, /Copy/);
assert.equal(events[0][1], 'brief_prepared');
assert.deepEqual(Object.keys(events[0][2]), ['page_path']);
data.company = '   ';
const previousBrief = element('brief-output').value;
element('brief-form').handlers.submit({ preventDefault() {} });
assert.equal(element('brief-output').value, previousBrief);
assert.equal(events.length, 1, 'A blank company must not generate another brief event');
assert.match(element('brief-status').textContent, /company name/);
console.log('PASS: brief generation, special-character encoding, edited scope, long-email fallback and analytics fields.');
