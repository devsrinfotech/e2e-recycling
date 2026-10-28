# Website contact form → ERPNext → Discord

The form sends seven fields to the existing **e2e Website Leads** doctype in
`https://e2e.srinfotech.biz`. No ERPNext API credentials are shipped to browsers.
The endpoint permits creation of this fixed document only. It grants no Guest
read/list/update permissions and does not disable CSRF protection.

## Server installation

Target runtime verified: ERPNext 14.20.1 / Frappe 14.31.0.
Copy `website_leads.py` to this path under the remote bench:

```
apps/erpnext/erpnext/crm/doctype/e2e_website_leads/website_api.py
```

The existing custom doctype is located inside the ERPNext app. Its controller is
unchanged. Keep this adjacent module and the custom doctype in the server's own
version control/backups when upgrading ERPNext. The separate `e2e_crm` app is not
installed on this site, so it is not used by this integration.

Endpoint (POST only):
`/api/method/erpnext.crm.doctype.e2e_website_leads.website_api.submit`

Run from the bench to enter the reCAPTCHA secret securely:

```
bench --site e2e.srinfotech.biz execute erpnext.crm.doctype.e2e_website_leads.website_api.configure
```

This asks for the **secret** key using hidden input, backs up the site config,
adds only the two website origins to the existing CORS list, and stores the secret
in the private `site_config.json` with owner-only permissions. It does not print
the key. Do not put that configuration or backup in this website repository.
If an existing wildcard CORS configuration is found, setup stops for review.

Google registration: **e2e Recycling website**, reCAPTCHA v2 checkbox, domain
`e2erecycling.com` (including its subdomains). The public site key is in
`assets/js/contact.js`; the secret must be stored only on the server.
The public endpoint validates Google's response and hostname. No valid token
means no CRM record. Localhost intentionally cannot submit using production keys.

## Discord activation

Saved ERPNext webhook: [HOOK-0004](https://e2e.srinfotech.biz/app/webhook/HOOK-0004).
It is deliberately **disabled** with a placeholder URL.

1. Replace Request URL with your Discord channel's incoming webhook URL.
2. Keep DocType `e2e Website Leads`, event `after_insert`, method `POST`, structure
   `JSON`, and header `Content-Type: application/json`.
3. Keep the JSON template in `discord-webhook.json.jinja`, then enable and save.
4. Submit one clearly labelled test enquiry and verify the CRM record, Discord
   card, and ERPNext Webhook Request Log. Never paste the Discord URL into HTML,
   browser JavaScript, Git, or chat.

All seven contact fields appear in the card; requirement details are its main
description. Mentions are disabled, values are JSON-escaped, and sizes stay within
Discord's limits for form submissions. Native ERPNext webhook delivery is separate
from lead acceptance. A Discord delivery failure does not mean the CRM lead was lost.

## Form behaviour and limits

- Required fields: contact name (120), company (140), email (140), phone (40),
  locations (140), assets (1,000), requirement details (2,000 characters).
- Five endpoint attempts per IP per ten minutes; server also checks origin,
  input types, length, email/phone format, plain text and a honeypot.
- CAPTCHA loads near the form or when it receives focus. Submission does not
  send ERP login cookies. The button is locked during submission.
- Success clears the form and announces confirmation. Failure retains the
  details, resets CAPTCHA and provides an email alternative. Network timeouts
  explicitly avoid claiming the record was or was not saved.
- GA4 receives `generate_lead` only after confirmed success, without form values.
- Without JavaScript, the existing mailto fallback remains available.

## Validation

```
python integrations/erpnext/test_website_leads.py
node scripts/check_contact.cjs
python scripts/audit_site.py
node scripts/check_brief.cjs
```

Unit tests mock Google and Frappe; they do not establish live CAPTCHA or Discord
delivery. Complete the live submission check after entering the secret and
publishing the website form. The public endpoint's missing-origin rejection was
verified as HTTP 403 after server installation.

References: [Google server verification](https://developers.google.com/recaptcha/docs/verify),
[Frappe webhooks](https://docs.frappe.io/framework/user/en/guides/integration/webhooks),
[Discord webhook API](https://docs.discord.com/developers/resources/webhook#execute-webhook).
