# SEO checks for project detail, film and recruiter pages + sitemap (run: python3 /app/tests/seo_detail_pages_check.py)
import json, re, sys
import requests
from html.parser import HTMLParser

BASE = open('/app/frontend/.env').read().split('REACT_APP_BACKEND_URL=')[1].split()[0].rstrip('/')
DATA = json.load(open('/app/src/data.json'))
SITE = "https://jacqmagawa.com"
PROJECTS = [p['slug'] for p in DATA['projects']]
FILMS = ["film-" + f['slug'] for f in DATA['films']]
OLD = ["index", "about", "flight-log", "education", "skills", "projects", "training-films", "gallery", "contact"]
NEW = PROJECTS + FILMS + ["recruiter-summary"]
fails = []


class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.heads = []; s.meta = {}; s.links = []; s.title = ''; s.in_title = False
        s.jsonld = []; s.in_ld = False; s.buf = ''; s.imgs = []; s.hrefs = []; s.ids = []; s.testids = {}
    def handle_starttag(s, t, a):
        a = dict(a)
        if 'id' in a: s.ids.append(a['id'])
        if 'data-testid' in a: s.testids.setdefault(a['data-testid'], []).append((t, a))
        if re.fullmatch(r'h[1-6]', t): s.heads.append(int(t[1]))
        if t == 'title': s.in_title = True
        if t == 'meta':
            k = a.get('name') or a.get('property')
            if k: s.meta[k] = a.get('content')
        if t == 'link': s.links.append(a)
        if t == 'script' and a.get('type') == 'application/ld+json': s.in_ld = True; s.buf = ''
        if t == 'img': s.imgs.append(a)
        if t == 'a' and a.get('href'): s.hrefs.append(a['href'])
        if t == 'source' and a.get('src'): s.hrefs.append(a['src'])
        if t == 'video' and a.get('poster'): s.hrefs.append(a['poster'])
    def handle_endtag(s, t):
        if t == 'title': s.in_title = False
        if t == 'script' and s.in_ld: s.in_ld = False; s.jsonld.append(s.buf)
    def handle_data(s, d):
        if s.in_title: s.title += d
        if s.in_ld: s.buf += d


titles = {}
all_refs = set()
for pg in OLD + NEW:
    r = requests.get(f"{BASE}/{pg}.html")
    p = P(); p.feed(r.text)
    # recruiter CTA + footer link on every page
    for tid in ['nav-recruiter-cta', 'footer-link-recruiter']:
        el = p.testids.get(tid)
        if not el or el[0][1].get('href') != '/recruiter-summary.html':
            fails.append(f"{pg}: {tid} missing/wrong")
    for i in p.imgs:
        if i.get('src'): all_refs.add(i['src'])
    all_refs.update(h for h in p.hrefs if h.startswith('/') or h.startswith(SITE))
    if pg in OLD:
        continue
    title = p.title.strip(); desc = p.meta.get('description') or ''
    titles.setdefault(title, []).append(pg)
    h1 = p.heads.count(1)
    skips = [(a, b) for a, b in zip(p.heads, p.heads[1:]) if b > a + 1]
    canon = [l.get('href') for l in p.links if l.get('rel') == 'canonical']
    exp = f"{SITE}/{pg}.html"
    dup = {i for i in p.ids if p.ids.count(i) > 1}
    noalt = [i.get('src') for i in p.imgs if 'alt' not in i]
    if r.status_code != 200: fails.append(f"{pg}: status {r.status_code}")
    if h1 != 1: fails.append(f"{pg}: h1 count {h1}")
    if p.heads and p.heads[0] != 1: fails.append(f"{pg}: first heading h{p.heads[0]}")
    if skips: fails.append(f"{pg}: heading skips {skips}")
    if not title or len(title) > 60: fails.append(f"{pg}: title len {len(title)} '{title}'")
    if not desc or len(desc) > 160: fails.append(f"{pg}: desc len {len(desc)}")
    if canon != [exp]: fails.append(f"{pg}: canonical {canon}")
    if p.meta.get('og:url') != exp: fails.append(f"{pg}: og:url {p.meta.get('og:url')}")
    if dup: fails.append(f"{pg}: dup ids {dup}")
    if noalt: fails.append(f"{pg}: img no alt {noalt}")
    try:
        ld = json.loads(p.jsonld[0]); graph = ld['@graph']
    except Exception as e:
        fails.append(f"{pg}: bad JSON-LD {e}"); continue
    bc = [g for g in graph if g.get('@type') == 'BreadcrumbList']
    wp = [g for g in graph if g.get('@type') in ('WebPage', 'CollectionPage', 'ProfilePage')]
    items = bc[0]['itemListElement'] if bc else []
    names = [i['name'] for i in items]
    if len(items) != 3 or items[0]['item'] != f"{SITE}/" or items[-1]['item'] != exp:
        fails.append(f"{pg}: breadcrumb {[(i['name'], i['item']) for i in items]}")
    me = wp[0].get('mainEntity', {}) if wp else {}
    if pg in PROJECTS:
        if names[1:2] != ['Projects'] or items[1]['item'] != f"{SITE}/projects.html": fails.append(f"{pg}: bc parent {names}")
        if me.get('@type') != 'CreativeWork' or not me.get('name'): fails.append(f"{pg}: mainEntity {me.get('@type')}")
        gh = p.testids.get('project-github-btn')
        if not gh or 'github.com/Jackie-legit' not in gh[0][1].get('href', '') or gh[0][1].get('target') != '_blank':
            fails.append(f"{pg}: github btn {gh}")
        if (p.testids.get('project-contact-btn') or [(0, {})])[0][1].get('href') != '/contact.html': fails.append(f"{pg}: contact btn")
        if (p.testids.get('breadcrumb-parent') or [(0, {})])[0][1].get('href') != '/projects.html': fails.append(f"{pg}: breadcrumb-parent")
    elif pg in FILMS:
        slug = pg[5:]
        if names[1:2] != ['Training Films'] or items[1]['item'] != f"{SITE}/training-films.html": fails.append(f"{pg}: bc parent {names}")
        for k in ['contentUrl', 'thumbnailUrl', 'uploadDate', 'duration', 'name', 'description']:
            if not me.get(k): fails.append(f"{pg}: VideoObject missing {k}")
        if me.get('@type') != 'VideoObject': fails.append(f"{pg}: mainEntity {me.get('@type')}")
        if me.get('contentUrl') != f"{SITE}/assets/video/{slug}.mp4": fails.append(f"{pg}: contentUrl {me.get('contentUrl')}")
        if not re.fullmatch(r'PT\d+M\d+S', me.get('duration', '')): fails.append(f"{pg}: duration {me.get('duration')}")
        v = p.testids.get('film-page-video')
        if not v or not v[0][1].get('poster'): fails.append(f"{pg}: video el/poster")
        more = [k for k in p.testids if k.startswith('film-more-')]
        if len(more) != 8: fails.append(f"{pg}: film-more count {len(more)}")
    else:
        if me: print("recruiter mainEntity", me)
    print(f"{pg}: {r.status_code} title({len(title)})='{title}' desc={len(desc)} heads={p.heads} bc={names} me={me.get('@type')}")

for t, pgs in titles.items():
    if len(pgs) > 1: fails.append(f"dup title {t} {pgs}")

print(f"\nChecking {len(all_refs)} internal refs")
for h in sorted(all_refs):
    u = h.replace(SITE, BASE)
    if u.startswith('/'): u = BASE + u
    u = u.split('#')[0]
    s = requests.head(u, allow_redirects=True).status_code
    if s >= 400: fails.append(f"broken ref {h} -> {s}")

r = requests.get(f"{BASE}/sitemap.xml")
locs = re.findall(r'<loc>(.*?)</loc>', r.text)
vids = re.findall(r'<url>\s*<loc>([^<]+)</loc>(?:(?!</url>).)*<video:video>', r.text, re.S)
print("sitemap", r.status_code, len(locs), "urls;", len(vids), "with video")
if len(locs) != 22: fails.append(f"sitemap {len(locs)} urls")
if sorted(vids) != sorted(f"{SITE}/{f}.html" for f in FILMS): fails.append(f"sitemap video entries {vids}")
for l in locs + re.findall(r'<video:(?:content_loc|thumbnail_loc)>(.*?)</video', r.text):
    s = requests.head(l.replace(SITE, BASE), allow_redirects=True).status_code
    if s != 200: fails.append(f"sitemap {l} -> {s}")
pdf = requests.head(f"{BASE}/assets/resume-jacqueline-magawa.pdf")
print("resume", pdf.status_code, pdf.headers.get('content-type'))
if pdf.status_code != 200: fails.append("resume pdf")
print("\nFAILS:" if fails else "\nALL PASS", *fails, sep="\n")
