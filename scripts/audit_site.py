"""Validate local links, assets, SEO metadata, JSON-LD and sitemap coverage."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from collections import Counter
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
BASE = 'https://e2erecycling.com/'

class Document(HTMLParser):
    def __init__(self,text):
        super().__init__(convert_charrefs=True)
        self.ids=[]; self.refs=[]; self.links=[]; self.h1=0; self.titles=[]; self.metas={}; self.canonical=[]; self.images=[]; self.schemas=[]; self.capture=None
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        if tag=='h1': self.h1+=1
        if tag=='title': self.capture=('title',[])
        if tag=='meta': self.metas[a.get('name',a.get('property',''))]=a.get('content','')
        if tag=='script' and a.get('type')=='application/ld+json': self.capture=('schema',[])
        if tag=='link' and a.get('rel')=='canonical': self.canonical.append(a.get('href'))
        if tag=='img': self.images.append(a)
        for name in ('href','src','data-image'):
            if a.get(name): self.refs.append((tag,name,a[name]))
        if a.get('srcset'):
            for candidate in a['srcset'].split(','):
                self.refs.append((tag,'srcset',candidate.strip().split()[0]))
        if tag=='a' and a.get('href'): self.links.append(a['href'])
    def handle_data(self,data):
        if self.capture: self.capture[1].append(data)
    def handle_endtag(self,tag):
        if self.capture and ((tag=='title' and self.capture[0]=='title') or (tag=='script' and self.capture[0]=='schema')):
            target=self.titles if self.capture[0]=='title' else self.schemas
            target.append(''.join(self.capture[1])); self.capture=None

def local_target(value, origin):
    parts=urlsplit(value)
    if parts.scheme and parts.scheme not in ('http','https'): return None
    if parts.netloc and parts.netloc not in ('e2erecycling.com','www.e2erecycling.com'): return None
    target=(ROOT/unquote(parts.path).lstrip('/')) if parts.netloc or parts.path.startswith('/') else origin.parent/unquote(parts.path)
    if not parts.path: target=origin
    if target.is_dir(): target=target/'index.html'
    return target.resolve(),unquote(parts.fragment)

def audit():
    errors=[]; warnings=[]; pages={p.resolve():Document(p.read_text(encoding='utf-8')) for p in ROOT.glob('*.html')}
    seen_titles={}; seen_desc={}
    for path,doc in pages.items():
        name=path.name
        if doc.h1!=1: errors.append(f'{name}: {doc.h1} H1 elements')
        if len(doc.titles)!=1: errors.append(f'{name}: title count {len(doc.titles)}')
        title=doc.titles[0] if doc.titles else ''
        description=doc.metas.get('description','')
        for value,seen,label in ((title,seen_titles,'title'),(description,seen_desc,'description')):
            if not value: errors.append(f'{name}: missing {label}')
            elif value in seen: errors.append(f'{name}: duplicate {label} with {seen[value]}')
            else: seen[value]=name
        canonical=BASE if name=='index.html' else BASE+name
        if doc.canonical!=[canonical]: errors.append(f'{name}: unexpected canonical {doc.canonical}')
        for field in ('og:title','og:description','og:url','og:image','twitter:card'):
            if not doc.metas.get(field): errors.append(f'{name}: missing {field}')
        if doc.metas.get('og:url')!=canonical: errors.append(f'{name}: OG URL differs from canonical')
        duplicates=[i for i,n in Counter(doc.ids).items() if n>1]
        if duplicates: errors.append(f'{name}: duplicate IDs {duplicates}')
        for tag,attr,value in doc.refs:
            target=local_target(value,path)
            if not target: continue
            file,fragment=target
            if not file.is_file(): errors.append(f'{name}: missing {attr} {value}')
            elif fragment and file in pages and fragment not in pages[file].ids:
                errors.append(f'{name}: missing fragment {value}')
        for img in doc.images:
            if 'alt' not in img: errors.append(f'{name}: image missing alt {img.get("src")}')
            if not img.get('width') or not img.get('height'): errors.append(f'{name}: image dimensions missing {img.get("src")}')
        for raw in doc.schemas:
            try: json.loads(raw)
            except ValueError as e: errors.append(f'{name}: invalid JSON-LD {e}')
    for css in ROOT.joinpath('assets/css').glob('*.css'):
        # Only audit stylesheets actually used by HTML pages.
        if not any(css.name in value for doc in pages.values() for _,attr,value in doc.refs if attr=='href'): continue
        for value in re.findall(r'url\([\'"]?([^\)\'\"]+)',css.read_text(encoding='utf-8')):
            target=local_target(value,css)
            if target and not target[0].is_file(): errors.append(f'{css.name}: missing CSS asset {value}')
    sitemap=ET.parse(ROOT/'sitemap.xml')
    urls=[e.text for e in sitemap.findall('.//{*}loc')]
    expected={BASE if p.name=='index.html' else BASE+p.name for p in pages}
    if set(urls)!=expected or len(urls)!=len(expected): errors.append('Sitemap does not exactly match live pages')
    visited=set(); todo=[ROOT.joinpath('index.html').resolve()]
    while todo:
        path=todo.pop()
        if path in visited: continue
        visited.add(path)
        for href in pages[path].links:
            target=local_target(href,path)
            if target and target[0] in pages and target[0] not in visited: todo.append(target[0])
    for orphan in pages.keys()-visited: errors.append(f'Orphan page: {orphan.name}')
    print(f'Audited {len(pages)} HTML pages; {len(urls)} sitemap URLs; {len(visited)} reachable from homepage.')
    for issue in errors: print('ERROR:',issue)
    for issue in warnings: print('WARN:',issue)
    if errors: raise SystemExit(1)
    print('PASS: links, assets, fragments, metadata, headings, image dimensions, JSON-LD and crawl discovery.')

if __name__=='__main__': audit()
