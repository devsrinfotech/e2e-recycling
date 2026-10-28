"""Repeatable static-site image and discovery improvements. Requires Pillow."""
from pathlib import Path
from urllib.parse import unquote, quote
from html import unescape
import re
import json
from PIL import Image, ImageOps
import xml.etree.ElementTree as ET
from build_growth import PAGES, DATE, BASE, card
from site_theme import apply_shell

ROOT = Path(__file__).resolve().parent.parent

def discovery():
    entries = [next(p for p in PAGES if p['slug']==slug) for slug in ('corporate-it-asset-disposal','data-erasure-services-india','server-recycling-india','hard-drive-destruction-services')]
    return '<section class="growth-discovery" aria-labelledby="growth-services"><div class="growth-container"><h2 id="growth-services">Equipment retirement and data protection for your IT team</h2><p>Choose the service for your equipment, then plan the inventory, data treatment and collection.</p><div class="growth-grid">'+''.join(card(p) for p in entries)+'</div><nav aria-label="IT planning resources"><a href="locations.html">Pan-India coverage</a><a href="e-waste-recycling-bengaluru.html">Bengaluru</a><a href="e-waste-recycling-chennai.html">Chennai</a><a href="e-waste-recycling-hyderabad.html">Hyderabad</a><a href="it-recycling-resources.html">IT guides and templates</a><a href="it-disposal-brief.html">Build an enquiry brief</a></nav></div></section>'

def optimise_images():
    mapping = {}
    original_bytes = optimized_bytes = 0
    for source in ROOT.joinpath('assets/images').rglob('*'):
        if source.suffix.lower() not in ('.png','.jpg','.jpeg') or source.stat().st_size < 18000:
            continue
        with Image.open(source) as image:
            image = ImageOps.exif_transpose(image)
            limit = (300,300) if 'icons' in source.parts else (1920,2800)
            if image.height > image.width*2:
                limit = (1400,4200)
            image.thumbnail(limit, Image.Resampling.LANCZOS)
            if image.mode not in ('RGB','RGBA'):
                image = image.convert('RGBA' if 'transparency' in image.info else 'RGB')
            target = source.with_suffix('.webp')
            if not target.exists() or target.stat().st_mtime < source.stat().st_mtime:
                image.save(target, 'WEBP', quality=84, method=6)
            mapping[source.relative_to(ROOT).as_posix()] = target.relative_to(ROOT).as_posix()
            original_bytes += source.stat().st_size
            optimized_bytes += target.stat().st_size
    return mapping, original_bytes, optimized_bytes

def optimise_html(path, mapping):
    text = apply_shell(path.read_text(encoding='utf-8'), path.name, PAGES)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    text = re.sub(r'<div\s+id="preloader"[^>]*>\s*</div>', '', text)
    # Plugin functionality is replaced by native navigation, FAQs and CSS images.
    text = re.sub(r'<script\b[^>]*\bsrc=["\'](?:assets/js/(?!custom\.js|growth\.js|brief\.js|contact\.js)[^"\']+|https://cdn\.jsdelivr\.net/[^"\']+)["\'][^>]*>\s*</script>', '', text, flags=re.I)
    text = re.sub(r'<link\b[^>]*(?:magnific-popup\.css|silverBox\.min\.css|cdn\.jsdelivr\.net)[^>]*>', '', text, flags=re.I)
    text = re.sub(r'\s+data-scroll-reveal="[^"]*"', '', text)
    text = re.sub(r'"@type"\s*:\s*"RecyclingCenter"', '"@type": ["Organization", "RecyclingCenter"]', text)
    text = re.sub(r'<a\s+class="menu-trigger">(.*?)</a>', r'<button type="button" class="menu-trigger" aria-label="Toggle navigation">\1</button>', text, flags=re.S)
    if 'fonts.googleapis.com/css' not in text:
        text = text.replace('</head>', '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Nunito:300,400,600,700&amp;display=swap">\n</head>')
    first = True
    def heading(match):
        nonlocal first
        if first:
            first = False
            return match.group(0)
        return match.group(0).replace('<h1','<h2',1).replace('</h1>','</h2>')
    text = re.sub(r'<h1\b[^>]*>.*?</h1>', heading, text, flags=re.S)
    canonical = BASE if path.name=='index.html' else BASE+path.name
    if 'rel="canonical"' not in text:
        text = text.replace('</head>',f'<link rel="canonical" href="{canonical}">\n</head>')
    if 'max-image-preview' not in text:
        text = text.replace('</head>','<meta name="robots" content="index,follow,max-image-preview:large">\n</head>')
    title_match = re.search(r'<title>(.*?)</title>',text,re.S)
    desc_match = re.search(r'<meta name="description"\s+content="([^"]+)"',text,re.S)
    title = title_match.group(1).strip() if title_match else path.stem
    description = desc_match.group(1) if desc_match else 'Corporate e-waste recycling, data sanitization and IT asset disposal with e2e Recycling.'
    meta = {'og:title':title,'og:description':description,'og:type':'article' if 'BlogPosting' in text else 'website','og:url':canonical,'og:image':BASE+'assets/images/photos/Artboard%202.png','twitter:card':'summary_large_image','twitter:title':title,'twitter:description':description,'twitter:image':BASE+'assets/images/photos/Artboard%202.png'}
    for name,value in meta.items():
        if f'="{name}"' not in text:
            attr = 'property' if name.startswith('og:') else 'name'
            text = text.replace('</head>',f'<meta {attr}="{name}" content="{value}">\n</head>')
    if 'assets/css/growth.css' not in text:
        text = text.replace('</head>','<link rel="stylesheet" href="assets/css/growth.css">\n</head>')
    if 'assets/js/growth.js' not in text:
        text = text.replace('</body>','<script defer src="assets/js/growth.js"></script>\n</body>')
    text = re.sub(r'<script src="assets/js/custom\.js">', '<script defer src="assets/js/custom.js">', text)
    def image(match):
        tag = match.group(0)
        src_match = re.search(r'\bsrc="([^"]+)"',tag)
        if not src_match:
            return tag
        src = unquote(unescape(src_match[1])).removeprefix('./')
        if src.endswith('/check.svg') and 'alt=' not in tag:
            tag = tag.replace('<img','<img alt=""',1)
        if src in mapping:
            src = mapping[src]
            tag = tag.replace(src_match[1], src,1)
        file = ROOT.joinpath(src)
        if file.is_file():
            if file.suffix.lower()=='.svg':
                svg = ET.parse(file).getroot()
                box = svg.get('viewBox','0 0 24 24').split()
                width, height = box[2], box[3]
            else:
                with Image.open(file) as img:
                    width, height = img.size
            if not re.search(r'\bwidth=',tag): tag = tag.replace('<img', f'<img width="{width}"',1)
            if not re.search(r'\bheight=',tag): tag = tag.replace('<img', f'<img height="{height}"',1)
        is_logo = 'logo.png' in src
        is_hero = path.name=='index.html' and 'Artboard 2.webp' in src
        if not is_logo and not is_hero and 'loading=' not in tag:
            tag = tag.replace('<img','<img loading="lazy" decoding="async"',1)
        if is_hero and 'fetchpriority=' not in tag:
            tag = tag.replace('<img','<img fetchpriority="high"',1)
        if is_hero:
            fallback = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'
            tag = tag.replace('src="'+src+'"','src="'+fallback+'"')
            return '<picture><source media="(min-width: 992px)" srcset="'+quote(src,safe='/')+'">'+tag+'</picture>'
        return tag
    text = re.sub(r'<img\b[^>]*>',image,text)
    def cover(match):
        src = mapping.get(match.group(1),match.group(1))
        return 'data-image="'+src+'" style="background-image:url(\''+src+'\')"'
    text = re.sub(r'data-image="([^"]+)"(?: style="background-image:[^"]*")?',cover,text)
    text = re.sub(r'<iframe\b(?![^>]*loading=)', '<iframe loading="lazy"',text)
    text = re.sub(r'\n[ \t]*\n(?:[ \t]*\n)+','\n\n',text)
    path.write_text('\n'.join(line.rstrip() for line in text.splitlines())+'\n',encoding='utf-8')

if __name__ == '__main__':
    mapping, before, after = optimise_images()
    for path in ROOT.glob('*.html'):
        optimise_html(path,mapping)
    urls = [BASE] + [BASE+p.name for p in sorted(ROOT.glob('*.html')) if p.name!='index.html']
    ROOT.joinpath('sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'  <url><loc>{u}</loc><lastmod>{DATE}</lastmod></url>\n' for u in urls)+'</urlset>\n',encoding='utf-8')
    ROOT.joinpath('docs/PERFORMANCE-ASSETS.json').write_text(json.dumps({'source_image_bytes':before,'optimized_image_bytes':after,'savings_percent':round((1-after/before)*100,1),'images':mapping},indent=2),encoding='utf-8')
    print(f'Optimized {len(mapping)} images: {before:,} -> {after:,} bytes ({(1-after/before)*100:.1f}% smaller). Updated {len(urls)} sitemap entries.')
