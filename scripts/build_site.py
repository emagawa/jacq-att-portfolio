"""Builds all public HTML pages, sitemap.xml and robots.txt from /app/src. Run: python3 scripts/build_site.py"""
import hashlib
import json
import re
from datetime import date
from html import escape
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
SITE = "https://jacqmagawa.com"
TODAY = date.today().isoformat()
DATA = json.loads((SRC / "data.json").read_text())

PERSON_ID = f"{SITE}/#person"
NAV = [
    ("/", "Home", "home"),
    ("/about.html", "About", "about"),
    ("/flight-log.html", "Flight Log", "log"),
    ("/education.html", "Education", "education"),
    ("/skills.html", "Checklist", "skills"),
    ("/projects.html", "Projects", "projects"),
    ("/training-films.html", "Training Films", "films"),
    ("/gallery.html", "Gallery", "gallery"),
    ("/contact.html", "Contact", "contact"),
]

PAGES = [
    {"file": "about.html", "section": "about", "nav": "about", "crumb": "About", "type": "ProfilePage",
     "title": "About Jacqueline Magawa | Aviation & Cyber Student",
     "desc": "Meet Jacqueline Magawa: Aviation Management graduate (A.S. 2024) earning a B.S. in Computer Science with a Cybersecurity minor at University at Albany."},
    {"file": "flight-log.html", "section": "flight-log", "nav": "log", "crumb": "Flight Log", "type": "WebPage",
     "title": "Flight Log: Pilot Training Timeline | Jacqueline Magawa",
     "desc": "Jacqueline Magawa's flight training timeline, from EAA Young Eagles flights in 2011 to an FAA Student Pilot Certificate in 2021."},
    {"file": "education.html", "section": "education", "nav": "education", "crumb": "Education", "type": "WebPage",
     "title": "Education & Credentials | Jacqueline Magawa",
     "desc": "B.S. Computer Science, Cybersecurity minor, at University at Albany; A.S. Aviation Management from Dutchess Community College; FAA and EAA credentials."},
    {"file": "skills.html", "section": "skills", "nav": "skills", "crumb": "Skills", "type": "WebPage",
     "title": "Skills: Cybersecurity, IT & Aviation | Jacqueline Magawa",
     "desc": "Jacqueline Magawa's skills: Java, C, Linux, cybersecurity, networking, IT support, customer service, and bilingual English and Swahili."},
    {"file": "projects.html", "section": "projects", "nav": "projects", "crumb": "Projects", "type": "CollectionPage",
     "title": "Cybersecurity & CS Projects | Jacqueline Magawa",
     "desc": "Projects by Jacqueline Magawa: a cybersecurity tabletop exercise, a Java interpreter for a custom language, and a SolarWinds supply-chain attack case study."},
    {"file": "training-films.html", "section": "training-films", "nav": "films", "crumb": "Training Films", "type": "CollectionPage",
     "title": "Flight Training Videos | Jacqueline Magawa",
     "desc": "Watch Jacqueline Magawa's flight training films: first flights at Brookhaven, takeoffs at Republic Airport, and a cross-country flight to Edgartown."},
    {"file": "gallery.html", "section": "gallery", "nav": "gallery", "crumb": "Gallery", "type": "CollectionPage",
     "title": "Aviation Photo Gallery | Jacqueline Magawa",
     "desc": "Photos from Jacqueline Magawa's flight training: cockpit checklists, instructors, Young Eagles certificates, and days on the ramp."},
    {"file": "contact.html", "section": "contact", "nav": "contact", "crumb": "Contact", "type": "ContactPage",
     "title": "Contact Jacqueline Magawa | Cyber, IT & Aviation Roles",
     "desc": "Contact Jacqueline Magawa about cybersecurity, IT and aviation internships or full-time roles. Send a message, email, call, or download her résumé."},
]

HOME = {"file": "index.html", "nav": "home", "type": "WebPage",
        "title": "Jacqueline Magawa | Aviation & Cybersecurity Portfolio",
        "desc": "Aviation Management graduate and Computer Science / Cybersecurity student at University at Albany. Flight log, projects, credentials and contact."}

EXPLORE = [
    ("01", "/about.html", "About", "From airport ramps to security operations: the story so far."),
    ("02", "/flight-log.html", "Flight Log", "A timeline of flight training, from Young Eagles to an FAA Student Pilot Certificate."),
    ("03", "/education.html", "Education & credentials", "University at Albany, Dutchess Community College, and FAA and EAA certificates."),
    ("04", "/skills.html", "Pre-Flight Checklist", "Cybersecurity, IT support, programming, and bilingual customer service skills."),
    ("05", "/projects.html", "Build Log", "A tabletop cyber exercise, a custom-language interpreter, and a SolarWinds case study."),
    ("06", "/training-films.html", "Training Films", "Cockpit videos from Brookhaven, Republic Airport, and a flight to Martha's Vineyard."),
    ("07", "/gallery.html", "Gallery", "Photos from the ramp, the cockpit, and the logbook."),
    ("08", "/contact.html", "Cleared for Contact", "Open to cybersecurity, IT, and aviation roles worldwide. Get in touch."),
]


def asset_version(rel):
    return hashlib.md5((ROOT / rel).read_bytes()).hexdigest()[:8]


def section(name):
    return (SRC / "sections" / f"{name}.html").read_text()


def indent(html, n=8):
    pad = " " * n
    return "\n".join(pad + line if line.strip() else line for line in html.splitlines())


def img_size(rel):
    with Image.open(ROOT / rel.lstrip("/")) as im:
        return im.size


def person():
    return {
        "@type": "Person", "@id": PERSON_ID, "name": "Jacqueline Magawa", "url": f"{SITE}/",
        "image": f"{SITE}/assets/img/portrait.jpg", "email": "mailto:jacqmagawa.ernest@gmail.com",
        "jobTitle": "Computer Science & Cybersecurity Student",
        "description": HOME["desc"],
        "address": {"@type": "PostalAddress", "addressLocality": "Albany", "addressRegion": "NY", "addressCountry": "US"},
        "affiliation": {"@type": "CollegeOrUniversity", "name": "University at Albany, SUNY", "url": "https://www.albany.edu/"},
        "alumniOf": {"@type": "CollegeOrUniversity", "name": "Dutchess Community College", "url": "https://www.sunydutchess.edu/"},
        "knowsLanguage": ["English", "Swahili"],
        "knowsAbout": ["Cybersecurity", "Computer Science", "Aviation Management", "Java", "C", "Linux",
                       "Computer Networking", "IT Support", "Threat Modeling", "MITRE ATT&CK"],
        "hasCredential": [
            {"@type": "EducationalOccupationalCredential", "name": "FAA Student Pilot Certificate", "credentialCategory": "certificate"},
            {"@type": "EducationalOccupationalCredential", "name": "Associate in Science, Aviation Management", "credentialCategory": "degree"},
        ],
        "sameAs": ["https://www.linkedin.com/in/jacquelinem25/", "https://github.com/Jackie-legit"],
    }


def films_schema():
    items = []
    for i, f in enumerate(DATA["films"]):
        items.append({"@type": "ListItem", "position": i + 1, "item": {
            "@type": "VideoObject", "name": f["title"], "description": f"{f['desc']} ({f['meta']})",
            "thumbnailUrl": f"{SITE}/assets/video/posters/{f['slug']}.jpg",
            "contentUrl": f"{SITE}/assets/video/{f['slug']}.mp4",
            "uploadDate": DATA["videoUploadDate"], "duration": f["duration"],
            "embedUrl": f"{SITE}/training-films.html"}})
    return {"@type": "ItemList", "name": "Flight training films", "itemListElement": items}


def gallery_schema():
    return {"@type": "ImageGallery", "name": "Aviation photo gallery", "image": [
        {"@type": "ImageObject", "contentUrl": f"{SITE}/assets/gallery/full/{g['file']}",
         "thumbnailUrl": f"{SITE}/assets/gallery/thumb/{g['file']}", "name": g["title"], "description": g["desc"],
         "creator": {"@id": PERSON_ID}} for g in DATA["gallery"]]}


def projects_schema():
    return {"@type": "ItemList", "name": "Projects", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "item": {"@type": "CreativeWork", "name": p["name"],
         "description": p["desc"], "dateCreated": "2026-04", "author": {"@id": PERSON_ID}}}
        for i, p in enumerate(DATA["projects"])]}


def json_ld(page, url):
    graph = [person()]
    webpage = {"@type": page["type"], "@id": f"{url}#webpage", "url": url, "name": page["title"],
               "description": page["desc"], "isPartOf": {"@id": f"{SITE}/#website"},
               "inLanguage": "en", "primaryImageOfPage": f"{SITE}/assets/img/og-image.jpg"}
    if page["nav"] == "home":
        graph.append({"@type": "WebSite", "@id": f"{SITE}/#website", "url": f"{SITE}/", "name": "Jacqueline Magawa",
                      "publisher": {"@id": PERSON_ID}, "inLanguage": "en"})
        webpage["about"] = {"@id": PERSON_ID}
    else:
        webpage["breadcrumb"] = {"@id": f"{url}#breadcrumb"}
        graph.append({"@type": "BreadcrumbList", "@id": f"{url}#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": page["crumb"], "item": url}]})
    if page["type"] == "ProfilePage":
        webpage["mainEntity"] = {"@id": PERSON_ID}
    extra = {"films": films_schema, "gallery": gallery_schema, "projects": projects_schema}.get(page["nav"])
    if extra:
        webpage["mainEntity"] = extra()
    graph.append(webpage)
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)


def head(page, url):
    t, d = escape(page["title"]), escape(page["desc"])
    css_v, js_v = asset_version("css/style.css"), asset_version("js/main.js")
    ld = (f'        <script type="application/ld+json">\n{json_ld(page, url)}\n        </script>'
          if page["nav"] else "")
    preload = ""
    if page["nav"] == "home":
        preload = ('\n        <link rel="preload" as="image" type="image/webp" href="/assets/img/portrait-420.webp" '
                   'imagesrcset="/assets/img/portrait-420.webp 420w, /assets/img/portrait.webp 720w" '
                   'imagesizes="(max-width: 720px) 82vw, 360px" fetchpriority="high" />')
    verify = ('\n        <meta name="google-site-verification" content="O1eQb3070F7YRxMfTstngAh38rn86dI0sbJe6DB02RY" />'
              if page["nav"] == "home" else "")
    return f"""<head>
        <!-- Google Tag Manager -->
        <script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
        new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
        j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
        'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
        }})(window,document,'script','dataLayer','GTM-NPG82L6T');</script>
        <!-- End Google Tag Manager -->
        <meta charset="UTF-8" />{verify}
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>{t}</title>
        <meta name="description" content="{d}" />
        <meta name="robots" content="index, follow, max-image-preview:large" />
        <meta name="theme-color" content="#13293b" />
        <meta name="author" content="Jacqueline Magawa" />
        <link rel="canonical" href="{url}" />
        <meta property="og:type" content="{'profile' if page['type'] == 'ProfilePage' else 'website'}" />
        <meta property="og:url" content="{url}" />
        <meta property="og:title" content="{t}" />
        <meta property="og:description" content="{d}" />
        <meta property="og:image" content="{SITE}/assets/img/og-image.jpg" />
        <meta property="og:image:type" content="image/jpeg" />
        <meta property="og:image:width" content="1200" />
        <meta property="og:image:height" content="630" />
        <meta property="og:image:alt" content="Jacqueline Magawa, Aviation Enthusiast and Cybersecurity / CS Student" />
        <meta property="og:site_name" content="Jacqueline Magawa" />
        <meta property="og:locale" content="en_US" />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="{t}" />
        <meta name="twitter:description" content="{d}" />
        <meta name="twitter:image" content="{SITE}/assets/img/og-image.jpg" />
        <meta name="twitter:image:alt" content="Jacqueline Magawa, Aviation Enthusiast and Cybersecurity / CS Student" />
        <link rel="icon" href="/assets/img/favicon.png" type="image/png" />
        <link rel="icon" href="/assets/img/favicon-32.png" sizes="32x32" type="image/png" />
        <link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png" />{preload}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Hanken+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
        <link rel="stylesheet" href="/css/style.css?v={css_v}" />
        <script src="/js/main.js?v={js_v}" defer></script>
{ld}
</head>"""


def nav(active):
    links = []
    for href, label, key in NAV:
        cls = "nav-link active" if key == active else "nav-link"
        cur = ' aria-current="page"' if key == active else ""
        links.append(f'<a href="{href}" class="{cls}"{cur} data-testid="nav-link-{key}">{label}</a>')
    joined = "\n                        ".join(links)
    return f"""<header class="site-nav" id="siteNav">
        <div class="container">
                <a href="/" class="brand" aria-label="Jacqueline Magawa, home" data-testid="nav-brand-link">
                        <picture>
                                <source type="image/webp" srcset="/assets/img/logo-magawa-nav.webp" />
                                <img src="/assets/img/logo-magawa-nav.png" width="120" height="134" alt="Jacqueline Magawa logo" />
                        </picture>
                        <span class="brand-name">Jacqueline</span>
                </a>
                <nav class="nav-links" id="navLinks" aria-label="Main">
                        {joined}
                </nav>
                <button class="nav-toggle" id="navToggle" aria-label="Toggle menu" aria-controls="navLinks" aria-expanded="false" data-testid="nav-toggle-btn">
                        <span></span><span></span><span></span>
                </button>
        </div>
</header>"""


def breadcrumb(page):
    return f"""<nav class="breadcrumb reveal" aria-label="Breadcrumb" data-testid="breadcrumb">
        <a href="/" data-testid="breadcrumb-home">Home</a><span aria-hidden="true">/</span><span aria-current="page">{escape(page['crumb'])}</span>
</nav>"""


def next_links(page):
    idx = [p["file"] for p in PAGES].index(page["file"])
    nxt = PAGES[(idx + 1) % len(PAGES)]
    prev = PAGES[idx - 1]
    return f"""<nav class="page-pager" aria-label="More pages" data-testid="page-pager">
        <div class="container page-pager-inner">
                <a href="/{prev['file']}" class="pager-link pager-prev" data-testid="pager-prev"><span class="pager-k">Previous</span><span class="pager-v">{escape(prev['crumb'])}</span></a>
                <a href="/{nxt['file']}" class="pager-link pager-next" data-testid="pager-next"><span class="pager-k">Next</span><span class="pager-v">{escape(nxt['crumb'])}</span></a>
        </div>
</nav>"""


def footer():
    links = "\n                        ".join(
        f'<a href="{h}" data-testid="footer-link-{k}">{l}</a>' for h, l, k in NAV[1:])
    return f"""<footer class="site-footer">
        <div class="container footer-inner">
                <span class="footer-brand">
                        <span>© <span id="year">{date.today().year}</span> Jacqueline Magawa. All rights reserved.</span>
                </span>
                <nav class="footer-nav" aria-label="Footer">
                        {links}
                </nav>
                <div class="footer-socials">
                        <span class="footer-tagline">Jacqueline Magawa — Computer Science, minor in Cybersecurity, Class of 2027</span>
                </div>
        </div>
</footer>"""


def films_html():
    cards = []
    for i, f in enumerate(DATA["films"]):
        w, h = img_size(f"assets/video/posters/{f['slug']}.jpg")
        alt = escape(f"{f['title']}: {f['desc']}")
        cards.append(f"""<article class="film-card reveal" data-testid="film-card-{i}">
        <div class="film-media" data-slug="{f['slug']}" role="button" tabindex="0" aria-label="Play video: {escape(f['title'])}" data-testid="film-media-{i}">
                <img class="film-poster" src="/assets/video/posters/{f['slug']}.jpg" width="{w}" height="{h}" alt="{alt}" loading="lazy" decoding="async" />
                <div class="film-play" aria-hidden="true">
                        <svg viewBox="0 0 24 24" fill="rgba(255,255,255,0.95)"><circle cx="12" cy="12" r="11" fill="rgba(8,21,33,0.5)" stroke="rgba(255,255,255,0.85)" stroke-width="1"/><path d="M10 8l6 4-6 4V8z"/></svg>
                </div>
                <span class="film-badge">Muted preview · click for sound</span>
        </div>
        <div class="film-body">
                <div class="card-meta">{escape(f['meta'])}</div>
                <h2>{escape(f['title'])}</h2>
                <p>{escape(f['desc'])}</p>
        </div>
</article>""")
    return indent("\n".join(cards), 32)


def gallery_html():
    items = []
    for i, g in enumerate(DATA["gallery"]):
        w, h = img_size(f"assets/gallery/thumb/{g['file']}")
        items.append(f"""<figure class="gallery-item reveal" data-index="{i}" data-file="{g['file']}" role="button" tabindex="0" aria-label="Open photo: {escape(g['title'])}" data-testid="gallery-item-{i}">
        <img src="/assets/gallery/thumb/{g['file']}" width="{w}" height="{h}" alt="{escape(g['title'] + ': ' + g['desc'])}" loading="lazy" decoding="async" />
        <figcaption class="gallery-cap"><b>{escape(g['title'])}</b><span>{escape(g['desc'])}</span></figcaption>
</figure>""")
    return indent("\n".join(items), 32)


def explore_html():
    cards = "\n".join(f"""<a class="explore-card reveal" href="{h}" data-testid="explore-card-{h.strip('/').replace('.html', '')}">
        <span class="sec-index">{n}</span>
        <h2>{escape(t)}</h2>
        <p>{escape(d)}</p>
        <span class="explore-go">Open page <span aria-hidden="true">→</span></span>
</a>""" for n, h, t, d in EXPLORE)
    return f"""<section class="section on-paper explore" id="explore" aria-labelledby="explore-title">
        <div class="container">
                <header class="sec-head sec-head--split reveal">
                        <span class="sec-index">00</span>
                        <h2 id="explore-title">Explore the portfolio</h2>
                        <span class="sec-kicker">Eight stops on the route</span>
                </header>
                <div class="explore-grid">
{indent(cards, 24)}
                </div>
        </div>
</section>"""


def body_extras(page_nav):
    out = []
    if page_nav == "contact":
        out.append(section("_resume-modal"))
    if page_nav == "gallery":
        out.append(section("_lightbox"))
    return "\n".join(out)


def render(page, main_html):
    url = f"{SITE}/" if page["file"] == "index.html" else f"{SITE}/{page['file']}"
    return f"""<!doctype html>
<html lang="en">
{indent(head(page, url))}
        <body data-page="{page['nav']}">
                <!-- Google Tag Manager (noscript) -->
                <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-NPG82L6T"
                height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
                <!-- End Google Tag Manager (noscript) -->
                <a class="skip-link" href="#main">Skip to content</a>
{indent(nav(page['nav']), 16)}
                <main id="main">
{indent(main_html, 16)}
                </main>
{indent(footer(), 16)}
{indent(body_extras(page['nav']), 16)}
                <div class="cursor-dot" id="cursorDot" aria-hidden="true"></div>
                <button type="button" id="backToTop" class="back-to-top" aria-label="Back to top" title="Back to top" data-testid="back-to-top">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 15l-6-6-6 6" /></svg>
                </button>
        </body>
</html>
"""


def sub_main(page):
    html = section(page["section"])
    html = html.replace("{{FILMS}}", films_html()).replace("{{GALLERY}}", gallery_html())
    html = re.sub(r'(<div class="container">)', r'\1\n' + indent(breadcrumb(page), 16), html, count=1)
    return html + "\n" + next_links(page)


def sitemap():
    def url(loc, prio, images=""):
        return f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{TODAY}</lastmod>
    <priority>{prio}</priority>{images}
  </url>"""
    gallery_imgs = "".join(f"""
    <image:image><image:loc>{SITE}/assets/gallery/full/{g['file']}</image:loc></image:image>""" for g in DATA["gallery"])
    entries = [url(f"{SITE}/", "1.0", f"""
    <image:image><image:loc>{SITE}/assets/img/portrait.jpg</image:loc></image:image>""")]
    for p in PAGES:
        entries.append(url(f"{SITE}/{p['file']}", "0.8", gallery_imgs if p["nav"] == "gallery" else ""))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n' + "\n".join(entries) + "\n</urlset>\n")


ROBOTS = f"""User-agent: *
Allow: /
Disallow: /api/
Disallow: /admin.html

Sitemap: {SITE}/sitemap.xml
"""

NOT_FOUND = {"file": "404.html", "nav": "", "type": "WebPage", "title": "Page not found | Jacqueline Magawa",
             "desc": "This page does not exist. Head back to Jacqueline Magawa's portfolio."}
NOT_FOUND_MAIN = """<section class="section page-first on-cream" id="not-found">
        <div class="container">
                <header class="sec-head sec-head--split">
                        <span class="sec-index">404</span>
                        <h1>Off the flight plan</h1>
                        <span class="sec-kicker">Page not found</span>
                </header>
                <p class="lead">The page you were looking for doesn't exist. Try one of these instead:</p>
                <p class="not-found-links"><a href="/" class="btn btn-rust" data-testid="notfound-home-btn">Back to home</a> <a href="/contact.html" class="btn btn-ghost" data-testid="notfound-contact-btn">Contact</a></p>
        </div>
</section>"""


def main():
    (ROOT / "index.html").write_text(render(HOME, section("hero") + "\n" + explore_html()))
    for p in PAGES:
        (ROOT / p["file"]).write_text(render(p, sub_main(p)))
    nf = render(NOT_FOUND, NOT_FOUND_MAIN).replace(
        '<meta name="robots" content="index, follow, max-image-preview:large" />',
        '<meta name="robots" content="noindex, follow" />')
    nf = re.sub(r'\s*<link rel="canonical"[^>]*>', "", nf)
    (ROOT / "404.html").write_text(nf)
    sm = sitemap()
    (ROOT / "sitemap.xml").write_text(sm)
    (ROOT / "backend" / "sitemap.xml").write_text(sm)
    (ROOT / "robots.txt").write_text(ROBOTS)
    print("Built", 2 + len(PAGES), "pages + sitemap.xml + robots.txt")


if __name__ == "__main__":
    main()
