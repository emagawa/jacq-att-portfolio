# Check JSON-LD structure + all asset refs (img/src/srcset/link href/script src) resolve
import json, re, requests
BASE = open('/app/frontend/.env').read().split('REACT_APP_BACKEND_URL=')[1].split()[0].rstrip('/')
PAGES = ["index", "about", "flight-log", "education", "skills", "projects", "training-films", "gallery", "contact", "404"]
refs = set()
for pg in PAGES:
    t = requests.get(f"{BASE}/{pg}.html").text
    for j in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        d = json.loads(j)
        g = d.get('@graph', [d])
        print(pg, [(x.get('@type'), x.get('@id', '')[:60]) for x in g])
        for x in g:
            if x.get('@type') == 'BreadcrumbList':
                print('   crumbs', [(i['position'], i.get('name'), i.get('item')) for i in x['itemListElement']])
            if x.get('@type') == 'VideoObject': print('   video', x.get('name'), x.get('contentUrl'), x.get('thumbnailUrl'), x.get('uploadDate'))
    for m in re.findall(r'(?:src|href|poster|content)="([^"]+)"', t):
        if m.startswith('/') or m.startswith('https://jacqmagawa.com/'): refs.add(m)
    for ss in re.findall(r'srcset="([^"]+)"', t):
        for part in ss.split(','):
            refs.add(part.strip().split(' ')[0])
    vids = re.findall(r'data-slug="([^"]+)"', t)
    for v in vids: refs.add(f"/assets/video/{v}.mp4")
    for f in re.findall(r'data-file="([^"]+)"', t): refs.add(f"/assets/gallery/full/{f}")
bad = []
for r in sorted(refs):
    u = r.replace('https://jacqmagawa.com', BASE)
    if u.startswith('/'): u = BASE + u
    s = requests.head(u.split('#')[0]).status_code
    if s >= 400: bad.append((r, s))
print(len(refs), 'refs checked; bad:', bad)
