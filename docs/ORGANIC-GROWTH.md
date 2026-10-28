# Corporate recycling and data erasure acquisition plan

Updated: 2026-10-28. Scope: the static website at https://e2erecycling.com/.

## Objective and audience

Generate qualified enquiries from IT managers, infrastructure teams, procurement and facilities for corporate laptops, desktops, workstations, monitors, servers and electronic equipment. Data erasure is a standalone service as well as a component of IT asset disposition. Lead with operational scope, data handling, reporting and collection; explain environmental benefits as a supporting result.

The owner confirmed KSPCB registration, Pan-India collection and logistics, physical drive destruction, prototype destruction, onsite assessments and the use of Blancco, TruWipe and BitRaser. No unprovided registration numbers, software partnerships, accreditations, customer logos, reviews, prices or case studies have been created. Onsite assessment is confirmed; onsite erasure execution is offered for feasibility review, not promised universally.

## Search intent and landing pages

These are qualitative intent groups, not invented search-volume or ranking estimates.

| Buyer intent | Page | Next step |
|---|---|---|
| Company computer, laptop, monitor and electronic waste disposal; ITAD partner India | corporate-it-asset-disposal.html | Prepare inventory and request scope |
| Corporate data wiping, data erasure, HDD/SSD sanitization; Blancco, TruWipe or BitRaser service | data-erasure-services-india.html | Specify media, tool, location and evidence |
| Server, storage and engineering workstation retirement | server-recycling-india.html | Share chassis and drive counts |
| Physical HDD/SSD destruction; failed media disposal | hard-drive-destruction-services.html | Agree media list and physical process |
| Corporate recycler Bengaluru/Bangalore, Chennai, Hyderabad | Three e-waste-recycling-{city}.html pages | City-specific collection planning |
| Corporate collection Mumbai, Pune, Delhi NCR, Kolkata, Ahmedabad and other metros | locations.html | Submit a site-by-site national scope |
| Wipe vs destroy, laptop disposal checklist, server decommissioning, erasure report, national collections | Five new articles, linked from blogs.html and it-recycling-resources.html | Relevant service or corporate enquiry form |
| Internal planning and vendor scoping | contact-us.html and blank asset inventory CSV | Submit one CRM enquiry with optional project details |

The national page is the coverage hub. Three priority-city pages address different planning needs. Avoid multiplying near-identical service/city combinations; expand only when there is real local evidence and useful unique information. All areas are explicitly collection coverage, with the real Tumkur location retained.

## SEO, GEO and answer usefulness implemented

- [x] Four dedicated service pages, three priority-city pages and a national coverage page.
- [x] Five IT buyer guides with direct answers, checklists, comparison tables, related service links and commercial next steps.
- [x] Clear vendor naming and source links; current NIST publication reference without claiming NIST certification.
- [x] Visible questions and answers covering reuse, erasure failures, onsite constraints, reporting and collection.
- [x] WebPage, Service, Article and BreadcrumbList data on appropriate new pages, with a consistent business identity. City pages describe City service areas and the actual Tumkur business address.
- [x] Unique titles/descriptions, canonical and sharing metadata, one H1, crawlable links and sitemap inclusion for 30 content pages; the retired brief URL redirects to the contact form.
- [x] Updated llms.txt as a readable source index. It is supplementary; no special AI file, FAQ schema or markup guarantees indexing, ranking, rich results or AI citations.
- [x] Existing blog bodies retained; discovery, duplicate headings, navigation, metadata and image delivery improved.
- [x] Native mobile navigation and FAQ interaction; links and answers remain in server-delivered HTML.

## Lead capture and measurement

The unified contact form submits to ERPNext with server-side reCAPTCHA verification and an enabled Discord notification. Optional project requirements cover the service, erasure preference, processing location, timing, access and reporting. These are included in the existing requirement details field and Discord description. The former brief URL redirects to this form; the inventory CSV remains a separate download. Email and phone remain fallback contact methods.

Existing GA4 property: G-P57BF6R1W2. The shared script tracks:

| Event | Meaning | Caveat |
|---|---|---|
| contact_intent | Click on email or phone link | A click is not a received enquiry |
| resource_download | Click on the inventory template | A click is not a qualified lead |
| generate_lead | CRM confirms a successful form submission | No form contents or company details are sent |

Use an internal enquiry register to record received email/call, source where known, service, city, equipment count, qualification, quote and won job. Do not label contact clicks as confirmed leads. No form contents, drive serials, email addresses or company names are included in these analytics events. Do not put personal data in page URLs.

## Speed work and reproduction

- 43 source raster images: 24,116,774 bytes. WebP outputs: 2,508,618 bytes, 89.6% smaller in aggregate. This is the image-library comparison, not a measured page-load percentage.
- Source PNG/JPEG files remain as regeneration inputs and existing social-image assets. Page image requests use WebP. Large diagrams preserve higher resolution for readable text.
- Below-the-fold images use lazy loading and asynchronous decoding; intrinsic dimensions reserve space. The home hero is eager with high fetch priority.
- Removed unused Swiper and SilverBox requests, blocking remote font import, jQuery and legacy animation/image/parallax plugin requests. Navigation and FAQs use a small native script. Decorative cover images use static CSS backgrounds.
- A conservative selector-pruning build combines legacy CSS into a 49,583-byte stylesheet, from 269,989 bytes of sources. It preserves dynamic navigation/FAQ states. The mobile Slow 4G / 4× CPU lab trace improved from 3,993 ms to 2,249 ms LCP after this change; CLS remained 0.00. See PERFORMANCE-REPORT.md for the exact limitations and checks.
- All pages use the original shared site stylesheet and native JavaScript. Nunito is retained with display=swap to preserve the existing appearance. Analytics loads asynchronously.
- Hosting controls response compression, CDN caching and TTFB. The repository has a CNAME and static files; no unsupported server-header file was added. Verify the actual production host before changing headers.

Run from the repository root:

```text
python scripts/build_growth.py
python scripts/optimize_site.py
python scripts/build_styles.py
python scripts/audit_site.py
node --check assets/js/custom.js
node --check assets/js/growth.js
node --check assets/js/contact.js
node scripts/check_contact.cjs
git diff --check
```

Python image optimization requires Pillow. Generated HTML is deployed as ordinary static files; production has no Python dependency. The content source for new pages is scripts/build_growth.py. Re-run optimization and then build_styles.py after a content build or source style change. Audit checks HTML/CSS assets, local links/fragments, metadata, JSON-LD syntax, image dimensions, unique H1s, sitemap coverage and homepage reachability. It does not establish schema rich-result eligibility or external-link availability.

## Launch and account work

| Priority | Action | Owner | Status |
|---|---|---|---|
| P0 | Review site copy and deploy the prepared static changes | Owner/Codex when authorised | Ready for review after local validation |
| P0 | Verify Google Search Console and Bing Webmaster Tools ownership; submit sitemap.xml and inspect the new service URLs | Owner | Account access required |
| P0 | Check GA4 contact_intent and generate_lead in the production property | Owner | After deployment |
| P1 | Mark only appropriate intent events as key events; reconcile actual qualified enquiries separately | Owner | After data review |
| P1 | Check production compression, caching, mobile PageSpeed and Search Console Core Web Vitals | Owner/Codex | After deployment |
| P1 | Provide current registration evidence, an approved example of an erasure report and an approved collection record | Owner | Evidence not yet organised |
| P1 | Review the actual business profile for the Tumkur location, service areas, contact consistency and genuine facility photos | Owner | No profile credentials provided |
| P2 | Publish approved case studies by service and city, with real process photos and customer permission | Owner | Evidence required |
| P2 | Seek relevant industry/customer directory links and request genuine customer reviews | Owner | No messages or submissions sent |

Do not create fake city offices, buy ranking links, fabricate reviews, publish unsupported certification claims or promise a timeframe for rankings. Google describes doorway and scaled-content abuse in its spam policies. Useful content and a verified business footprint are the basis for durable acquisition.

## 90-day operating plan

| Window | Task | Owner | Measure |
|---|---|---|---|
| Launch week | Publish, submit sitemap, inspect service URLs and confirm event reception | Owner | Live URLs, indexing status and working enquiry email |
| Weeks 2–4 | Review query/page impressions and actual IT enquiries by service/city; fix indexing or scope confusion | Owner | Qualified enquiries and quoted projects, not raw traffic alone |
| Month 2 | Add approved evidence and a case study on the service drawing the strongest relevant impressions | Owner | Relevant clicks, enquiry quality and quote conversion |
| Month 3 | Expand one coverage topic only if actual delivery evidence and buyer questions support it | Owner | Qualified leads from the new content, no duplicated city pages |
| Monthly | Review actual questions from enquiries; update corresponding answers and verify citations | Owner | Content usefulness and fewer unqualified contacts |

There is no traffic baseline or account access in this workspace, so results must be measured after deployment. Suggested good Core Web Vitals targets are LCP ≤2.5 s, INP ≤200 ms and CLS ≤0.1 at the 75th percentile. A local lab trace does not prove those real-user outcomes; INP needs real interactions and field reporting.

## Sources checked

- Google AI features and websites: https://developers.google.com/search/docs/appearance/ai-features
- Google spam policies: https://developers.google.com/search/docs/essentials/spam-policies
- Web Vitals: https://web.dev/articles/vitals
- NIST SP 800-88 Revision 2 (September 2025): https://csrc.nist.gov/pubs/sp/800/88/r2/final
- Blancco Drive Eraser: https://blancco.com/products/drive-eraser/
- TruWipe, confirmed by the owner: https://truwipe.com/
- BitRaser report examples: https://www.bitraser.com/reports-and-certificates.php
- CPCB e-waste portal: https://eprewaste.cpcb.gov.in/

## Original-theme alignment

The original navigation (including Blogs), footer, Nunito typography and image banners are shared across all 31 pages. scripts/templates contains the common header/footer; scripts/site_theme.py applies them to new content. The original nine blog cards stay first, with five new illustrated guide cards below them. Legacy plugin image wrappers were replaced with ordinary responsive images. Historical lab timings in PERFORMANCE-REPORT.md predate this visual restoration and need remeasurement.
