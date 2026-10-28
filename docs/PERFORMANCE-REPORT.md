# Local performance and interaction verification

Design-alignment follow-up: the original Nunito font, image banners, article images, sticky navigation and shared footer were restored after the measurements below. These timings describe the earlier layout and must be remeasured for the final visual design. Optimized WebP assets and native interactions remain in use.

Date: 2026-10-28. Target: this working tree served through Python at 127.0.0.1:8765. Browser: Chrome DevTools MCP. These are lab observations, not production PageSpeed scores or field Core Web Vitals.

## Measurements

| Check | Before | After | Conditions |
|---|---:|---:|---|
| Desktop home LCP | 211 ms | 135 ms | Cold reload, no network or CPU throttling; measured before the final CSS bundle |
| Desktop home CLS | 0.01 | 0.00 | Same desktop traces |
| Mobile home LCP, before/after CSS bundling | 3,993 ms | 2,249 ms | 390×844 viewport, Slow 4G, 4× CPU slowdown, cold reload |
| Mobile home CLS | 0.00 | 0.00 | Same mobile traces |
| Raster source library vs WebP output | 24,116,774 B | 2,508,618 B | 43 files, 89.6% aggregate reduction |
| Legacy stylesheet sources vs pruned bundle | 269,989 B | 49,583 B | Four source stylesheets combined; selectors pruned using all pages and dynamic-state safelist |

The final mobile LCP trace is 1,744 ms faster than the preceding mobile trace under the same throttling settings. The Python server does not represent production compression, CDN latency or cache policy. No real-user INP or CrUX data was available; a lab pass does not establish a production Core Web Vitals pass.

## What was verified

- All 31 pages appear in the sitemap and are reachable through homepage links.
- Local links, fragment targets, referenced HTML/CSS assets, canonicals, sharing metadata, unique titles/descriptions, single H1s, image alt/dimensions and JSON-LD syntax pass scripts/audit_site.py.
- The new data-erasure page was visually inspected in desktop Chrome and checked at a 390 px mobile viewport with no page overflow.
- Home and FAQ mobile layouts report no horizontal overflow. The mobile navigation opens and updates aria-expanded. The FAQ opens its answer and updates its expanded state using native JavaScript.
- The enquiry tool generated an editable brief containing selected cities, asset quantities, standalone erasure intent and TruWipe preference. The email action prepares a message to info@e2erecycling.com. The final implementation keeps the body out of the anchor URL so automatic click reporting cannot read it from that URL. No email was sent.
- The brief_prepared event contains only page_path; form contents are not included.
- The home and data-erasure page consoles had no error/warning messages during the inspected loads.
- The mobile home hero selects the tiny inline fallback and does not request the desktop illustration.
- JavaScript syntax and Git whitespace checks pass.

## Recheck after deployment

1. Inspect the real domain on mobile PageSpeed Insights and review production response compression/cache headers.
2. Confirm new URL indexing in Search Console/Bing and verify canonical selection.
3. Check actual traffic and field LCP/INP/CLS over time, by device and page template.
4. Confirm GA4 receives intent events and reconcile them with emails, calls, quotes and won work. Clicks alone are not qualified leads.

Threshold reference: https://web.dev/articles/vitals. Full acquisition and operations plan: ORGANIC-GROWTH.md.
