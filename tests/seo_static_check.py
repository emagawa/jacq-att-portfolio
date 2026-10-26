# SEO static checks for generated multi-page site (run: python3 /app/tests/seo_static_check.py)
import json, re, os, sys
import requests
from html.parser import HTMLParser

BASE = open('/app/frontend/.env').read().split('REACT_APP_BACKEND_URL=')[1].split()[0].rstrip('/')
PAGES = ["index", "about", "flight-log", "education", "skills", "projects", "training-films", "gallery", "contact", "404"]
fails = []

class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.heads = []; s.meta = {}; s.links = []; s.title = ''; s.in_title = False
        s.jsonld = []; s.in_ld = False; s.buf = ''; s.imgs = []; s.hrefs = []; s.ids = []
    def handle_starttag(s, t, a):
        a = dict(a)
        if 'id' in a: s.ids.append(a['id'])
        if re.fullmatch(r'h[1-6]', t): s.heads.append(int(t[1]))
        if t == 'title': s.in_title = True
        if t == 'meta':
            k = a.get('name') or a.get('property')
            if k: s.meta[k] = a.get('content')
        if t == 'link': s.links.append(a)
        if t == 'script' and a.get('type') == 'application/ld+json': s.in_ld = True; s.buf = ''
        if t == 'img': s.imgs.append(a)
        if t == 'a' and a.get('href'): s.hrefs.append(a['href'])
    def handle_endtag(s, t):
        if t == 'title': s.in_title = False
        if t == 'script' and s.in_ld: s.in_ld = False; s.jsonld.append(s.buf)
    def handle_data(s, d):
        if s.in_title: s.title += d
        if s.in_ld: s.buf += d

all_hrefs = set()
for pg in PAGES:
    r = requests.get(f"{BASE}/{pg}.html")
    p = P(); p.feed(r.text)
    h1 = p.heads.count(1)
    skips = [(a, b) for a, b in zip(p.heads, p.heads[1:]) if b > a + 1]
    canon = [l.get('href') for l in p.links if l.get('rel') == 'canonical']
    exp = "https://jacqmagawa.com/" if pg == "index" else f"https://jacqmagawa.com/{pg}.html"
    lds = []
    for j in p.jsonld:
        try: lds.append(json.loads(j))
        except Exception as e: fails.append(f"{pg}: invalid JSON-LD {e}")
    noalt = [i.get('src') for i in p.imgs if 'alt' not in i]
    dup_ids = {i for i in p.ids if p.ids.count(i) > 1}
    print(f"{pg}: {r.status_code} title='{p.title.strip()}' ({len(p.title.strip())}) desc_len={len(p.meta.get('description') or '')} "
          f"h1={h1} heads={p.heads[:12]} canon={canon} robots={p.meta.get('robots')} og:image={p.meta.get('og:image')} "
          f"og:url={p.meta.get('og:url')} tw={p.meta.get('twitter:card')} ld_types={[ (d.get('@type') if isinstance(d,dict) else '?') for d in lds]} noalt={noalt} dupids={dup_ids}")
    if pg != "404":
        if r.status_code != 200: fails.append(f"{pg}: status {r.status_code}")
        if canon != [exp]: fails.append(f"{pg}: canonical {canon} != {exp}")
        if p.meta.get('og:url') != exp: fails.append(f"{pg}: og:url {p.meta.get('og:url')}")
        if 'noindex' in (p.meta.get('robots') or ''): fails.append(f"{pg}: noindex")
    if h1 != 1: fails.append(f"{pg}: h1 count {h1}")
    if skips: fails.append(f"{pg}: heading skips {skips}")
    if not p.meta.get('description'): fails.append(f"{pg}: no description")
    if noalt: fails.append(f"{pg}: img without alt {noalt}")
    if dup_ids: fails.append(f"{pg}: duplicate ids {dup_ids}")
    all_hrefs.update(h for h in p.hrefs if h.startswith('/') or h.startswith(BASE) or h.startswith('https://jacqmagawa.com'))
    for k in ['og:title', 'og:description', 'og:image', 'twitter:card', 'twitter:title', 'twitter:image']:
        if not p.meta.get(k): fails.append(f"{pg}: missing {k}")

print("\nInternal links:", sorted(all_hrefs))
for h in sorted(all_hrefs):
    u = h.replace('https://jacqmagawa.com', BASE)
    if u.startswith('/'): u = BASE + u
    u = u.split('#')[0]
    r = requests.head(u, allow_redirects=True)
    if r.status_code >= 400: fails.append(f"broken link {h} -> {r.status_code}")

# robots / sitemap / private files
r = requests.get(f"{BASE}/robots.txt"); print("\nrobots:", r.status_code, r.headers.get('content-type'), repr(r.text))
if 'Sitemap: https://jacqmagawa.com/sitemap.xml' not in r.text or 'text/plain' not in r.headers.get('content-type', ''): fails.append("robots.txt bad")
r = requests.get(f"{BASE}/sitemap.xml"); locs = re.findall(r'<loc>(.*?)</loc>', r.text)
print("sitemap:", r.status_code, r.headers.get('content-type'), locs)
if len(locs) != 9: fails.append(f"sitemap has {len(locs)} urls")
for l in locs:
    s = requests.get(l.replace('https://jacqmagawa.com', BASE)).status_code
    if s != 200: fails.append(f"sitemap url {l} -> {s}")
for path in ['/.env', '/backend/.env', '/frontend/.env', '/scripts/build_site.py', '/src/data.json', '/nope', '/%2e%2e/etc/passwd', '/frontend/server.js', '/.git/config']:
    r = requests.get(BASE + path); print(path, r.status_code, 'notfound-home-btn' in r.text)
    if r.status_code != 404: fails.append(f"{path} served {r.status_code}")
# all images in sitemap pages load
print("\nFAILS:" if fails else "\nALL PASS", *fails, sep="\n")
