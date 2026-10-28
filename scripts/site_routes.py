"""Compatibility URLs retired from the searchable site."""
from html import escape

REDIRECTS = {'it-disposal-brief.html': 'contact-us.html#corporate-contact-form'}


def render_redirect(target):
    return f'''<!doctype html>
<html lang="en-IN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Project enquiries have moved | e2e Recycling</title>
<meta name="description" content="Send your IT disposal and data erasure requirements through our unified corporate enquiry form.">
<meta name="robots" content="noindex,follow">
<link rel="canonical" href="https://e2erecycling.com/{escape(target.split('#')[0])}">
<meta http-equiv="refresh" content="0; url={escape(target)}">
</head><body><main><h1>Plan your project with e2e</h1>
<p>Our project questions are now part of the contact form.</p>
<p><a href="{escape(target)}">Continue to the corporate enquiry form</a></p>
<p><a href="assets/downloads/corporate-it-asset-inventory.csv">Download the asset inventory template</a></p>
</main></body></html>'''
