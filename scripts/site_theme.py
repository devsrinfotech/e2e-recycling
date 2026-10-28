"""Shared original-site shell for service pages, guides and existing pages."""
from pathlib import Path
from html import escape
import re

ROOT=Path(__file__).resolve().parent.parent
HEADER=(ROOT/'scripts/templates/header.html').read_text(encoding='utf-8')
FOOTER=(ROOT/'scripts/templates/footer.html').read_text(encoding='utf-8')
ARTICLE_IMAGES={
 'data-erasure-vs-drive-destruction':'blog/it-erasure-vs-destruction.webp',
 'corporate-laptop-disposal-checklist':'blog/it-laptop-disposal-checklist.webp',
 'server-decommissioning-checklist':'blog/it-server-decommissioning.webp',
 'data-erasure-certificate-checklist':'blog/it-erasure-report-checklist.webp',
 'multi-office-e-waste-collection-plan':'blog/it-multi-office-collection.webp',
}

def article_image(p):
    src='assets/images/photos/'+ARTICLE_IMAGES[p['slug']]
    return f'<div class="img"><img src="{src}" alt="{escape(p["h1"])}"></div>'

def wrap_page(html,p):
    head=html.split('<body',1)[0].replace('assets/css/growth.css','assets/css/site.min.css')
    head=re.sub(r'<script defer src="assets/js/(?:growth|brief)\.js"></script>','',head)
    content=html.split('<div class="growth-container growth-content">',1)[1].split('</main>',1)[0].removesuffix('</div>')
    article=p['kind']=='article'
    if article:
        head=head.replace('assets/images/photos/Artboard%202.png','assets/images/photos/'+ARTICLE_IMAGES[p['slug']].replace('.webp','.png'))
    image=article_image(p) if article else ''
    banner='hero.webp' if article else 'services.webp'
    title=escape(p['h1'])
    crumb='<li><a href="blogs.html">Blogs</a></li>' if article else '<li><a href="services.html">Services</a></li>'
    body=f'''<body class="content-page"><a class="skip-link" href="#main-content">Skip to content</a>{HEADER}
<main class="page" id="main-content"><div class="cover" data-image="assets/images/photos/{banner}"><div class="page-top"><div class="container"><div class="row"><div class="col-lg-12"><h1>{title}</h1></div><div class="col-lg-12"><ol class="breadcrumb"><li><a href="index.html">Home</a></li>{crumb}</ol></div></div></div></div></div>
<div class="page-bottom"><div class="container"><div class="row justify-content-center"><div class="col-lg-10 col-md-12"><div class="{'blog-post-thumb big' if article else 'service-detail'}">{image}<div class="theme-content"><p>{escape(p['intro'])}</p><div class="growth-actions"><a class="btn-primary-line btn-assessment" href="{'#brief-heading' if p['kind']=='tool' else 'it-disposal-brief.html'}">{'Start your brief' if p['kind']=='tool' else 'Request an assessment'}</a></div>{content}</div></div></div></div></div></div></main>{FOOTER}<script defer src="assets/js/custom.js"></script><script defer src="assets/js/growth.js"></script>{'<script defer src="assets/js/brief.js"></script>' if p['kind']=='tool' else ''}</body></html>'''
    # The original button styles are shared with the enquiry tool and all CTAs.
    body=body.replace('class="growth-button secondary"','class="btn-primary-line btn-assessment"').replace('class="growth-button"','class="btn-primary-line btn-assessment"')
    if article:
        body=body.replace('class="col-lg-10 col-md-12"','class="col-lg-10 col-md-12 blog-list"')
        body=body.replace('class="theme-content"','class="theme-content text post-detail"')
    return head+body

def apply_shell(text, name, pages):
    text=re.sub(r'<header\b.*?</header>',lambda _:HEADER,text,count=1,flags=re.S)
    text=re.sub(r'<footer\b.*?</footer>',lambda _:FOOTER,text,count=1,flags=re.S)
    text=re.sub(r'<section class="growth-discovery".*?</section>','',text,flags=re.S)
    text=re.sub(r'<section id="it-buyer-guides".*?</section>','',text,flags=re.S)
    if name=='services.html' and 'id="service-directory"' not in text:
        cards=''.join(f'<div class="col-lg-6 col-md-6"><a class="features-small-item" href="{p["slug"]}.html"><h2 class="features-title">{escape(p["h1"])}</h2><p>{escape(p["description"])}</p><span>View service →</span></a></div>' for p in pages if p['kind']=='service')
        directory='<section id="service-directory" class="container"><div class="left-heading"><h2 class="section-title">Explore our corporate services</h2></div><div class="row">'+cards+'</div><p class="pb-40"><a href="locations.html">View collection coverage</a> · <a href="it-recycling-resources.html">IT guides and templates</a> · <a href="it-disposal-brief.html">Build an enquiry brief</a></p></section>'
        text=text.replace('<div class="page-bottom">','<div class="page-bottom">'+directory,1)
    # Old articles were saved with plugin-generated nested image wrappers.
    text=re.sub(r'<div class="img imgfix_top_container"[^>]*>\s*<div[^>]*>\s*(<img\b[^>]*>)\s*</div>\s*</div>',lambda m:'<div class="img">'+re.sub(r'\s+style="[^"]*"','',m[1])+'</div>',text,flags=re.S)
    if name=='blogs.html':
        text=re.sub(r'<section id="new-it-articles".*?</section>','',text,flags=re.S)
        cards=''
        for p in pages:
            if p['kind']!='article': continue
            cards+=f'<div class="col-lg-6 col-md-6 col-sm-12"><div class="blog-post-thumb">{article_image(p)}<h3><a href="{p["slug"]}.html">{escape(p["h1"])}</a></h3><div class="text">{escape(p["description"])}</div><a href="{p["slug"]}.html" class="btn-primary-line">Read More</a></div></div>'
        section='<section id="new-it-articles" class="container blog-list"><h2 class="section-title pb-40">IT disposal and data erasure guides</h2><div class="row">'+cards+'</div></section>'
        text=text.replace('<footer>',section+'<footer>',1)
    return text
