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
    {"file": "projects.html", "section": "projects", "nav": "projects", "crumb": "Projects", "type": "CollectionPage", "entity": "projects",
     "title": "Cybersecurity & CS Projects | Jacqueline Magawa",
     "desc": "Projects by Jacqueline Magawa: a cybersecurity tabletop exercise, a Java interpreter for a custom language, and a SolarWinds supply-chain attack case study."},
    {"file": "training-films.html", "section": "training-films", "nav": "films", "crumb": "Training Films", "type": "CollectionPage", "entity": "films",
     "title": "Flight Training Videos | Jacqueline Magawa",
     "desc": "Watch Jacqueline Magawa's flight training films: first flights at Brookhaven, takeoffs at Republic Airport, and a cross-country flight to Edgartown."},
    {"file": "gallery.html", "section": "gallery", "nav": "gallery", "crumb": "Gallery", "type": "CollectionPage", "entity": "gallery",
     "title": "Aviation Photo Gallery | Jacqueline Magawa",
     "desc": "Photos from Jacqueline Magawa's flight training: cockpit checklists, instructors, Young Eagles certificates, and days on the ramp."},
    {"file": "contact.html", "section": "contact", "nav": "contact", "crumb": "Contact", "type": "ContactPage",
     "title": "Contact Jacqueline Magawa | Cyber, IT & Aviation Roles",
     "desc": "Contact Jacqueline Magawa about cybersecurity, IT and aviation internships or full-time roles. Send a message, email, call, or download her résumé."},
]

HOME = {"file": "index.html", "nav": "home", "type": "WebPage",
        "title": "Jacqueline Magawa | Aviation & Cybersecurity Portfolio",
        "desc": "Aviation Management graduate and Computer Science / Cybersecurity student at University at Albany. Flight log, projects, credentials and contact."}

RECRUITER_FILE = "recruiter-summary.html"
RECRUITER = {"file": RECRUITER_FILE, "nav": "recruiter", "crumb": "Recruiter Summary", "type": "WebPage",
             "title": "Recruiter Summary: Jacqueline Magawa | One-Page Profile",
             "desc": "One-page summary of Jacqueline Magawa for recruiters: contact details, education, skills, projects and flight training highlights. Print or save as PDF."}


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


def film_page_file(f):
    return f"film-{f['slug']}.html"


def video_object(f):
    video = {"@type": "VideoObject", "@id": f"{SITE}/{film_page_file(f)}#video", "name": f["title"],
             "description": f"{f['desc']} ({f['meta']})",
             "thumbnailUrl": f"{SITE}/assets/video/posters/{f['slug']}.jpg",
             "uploadDate": DATA["videoUploadDate"], "duration": f["duration"],
             "creator": {"@id": PERSON_ID}}
    if f.get("youtube"):
        video["embedUrl"] = f"https://www.youtube.com/embed/{f['youtube']}"
    else:
        video["contentUrl"] = f"{SITE}/assets/video/{f['slug']}.mp4"
    return video


def films_schema():
    return {"@type": "ItemList", "name": "Flight training films", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "url": f"{SITE}/{film_page_file(f)}", "name": f["title"]}
        for i, f in enumerate(DATA["films"])]}


def gallery_schema():
    return {"@type": "ImageGallery", "name": "Aviation photo gallery", "image": [
        {"@type": "ImageObject", "contentUrl": f"{SITE}/assets/gallery/full/{g['file']}",
         "thumbnailUrl": f"{SITE}/assets/gallery/thumb/{g['file']}", "name": g["title"], "description": g["desc"],
         "creator": {"@id": PERSON_ID}} for g in DATA["gallery"]]}


def projects_schema():
    return {"@type": "ItemList", "name": "Projects", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "url": f"{SITE}/{p['slug']}.html", "name": p["name"]}
        for i, p in enumerate(DATA["projects"])]}


def project_object(p):
    return {"@type": "CreativeWork", "@id": f"{SITE}/{p['slug']}.html#project", "name": p["name"],
            "description": p["card"], "dateCreated": p["dateISO"], "keywords": ", ".join(p["tags"]),
            "author": {"@id": PERSON_ID}}


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
        trail = [("Home", f"{SITE}/")] + [(n, SITE + h) for n, h in page.get("parents", [])] + [(page["crumb"], url)]
        graph.append({"@type": "BreadcrumbList", "@id": f"{url}#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(trail)]})
    if page["type"] == "ProfilePage":
        webpage["mainEntity"] = {"@id": PERSON_ID}
    extra = {"films": films_schema, "gallery": gallery_schema, "projects": projects_schema}.get(page.get("entity"))
    if extra:
        webpage["mainEntity"] = extra()
    if page.get("entity_obj"):
        webpage["mainEntity"] = page["entity_obj"]
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
    links.append(f'<a href="/{RECRUITER_FILE}" class="nav-link nav-link--recruiter" data-testid="nav-link-recruiter">Recruiter view</a>')
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
                <a href="/{RECRUITER_FILE}" class="nav-cta" data-testid="nav-recruiter-cta">Recruiter view</a>
                <button class="nav-toggle" id="navToggle" aria-label="Toggle menu" aria-controls="navLinks" aria-expanded="false" data-testid="nav-toggle-btn">
                        <span></span><span></span><span></span>
                </button>
        </div>
</header>"""


def breadcrumb(page):
    sep = '<span aria-hidden="true">/</span>'
    parents = "".join(f'<a href="{h}" data-testid="breadcrumb-parent">{escape(n)}</a>{sep}'
                      for n, h in page.get("parents", []))
    return f"""<nav class="breadcrumb reveal" aria-label="Breadcrumb" data-testid="breadcrumb">
        <a href="/" data-testid="breadcrumb-home">Home</a>{sep}{parents}<span aria-current="page">{escape(page['crumb'])}</span>
</nav>"""


def pager(prev_href, prev_label, next_href, next_label):
    return f"""<nav class="page-pager" aria-label="More pages" data-testid="page-pager">
        <div class="container page-pager-inner">
                <a href="{prev_href}" class="pager-link pager-prev" data-testid="pager-prev"><span class="pager-k">Previous</span><span class="pager-v">{escape(prev_label)}</span></a>
                <a href="{next_href}" class="pager-link pager-next" data-testid="pager-next"><span class="pager-k">Next</span><span class="pager-v">{escape(next_label)}</span></a>
        </div>
</nav>"""


def next_links(page):
    idx = [p["file"] for p in PAGES].index(page["file"])
    nxt = PAGES[(idx + 1) % len(PAGES)]
    prev = PAGES[idx - 1]
    return pager(f"/{prev['file']}", prev["crumb"], f"/{nxt['file']}", nxt["crumb"])


def footer():
    links = "\n                        ".join(
        [f'<a href="{h}" data-testid="footer-link-{k}">{l}</a>' for h, l, k in NAV[1:]]
        + [f'<a href="/{RECRUITER_FILE}" data-testid="footer-link-recruiter">Recruiter summary</a>'])
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


def film_media(f, testid):
    w, h = img_size(f"assets/video/posters/{f['slug']}.jpg")
    alt = escape(f"{f['title']}: {f['desc']}")
    yt = f' data-youtube="{f["youtube"]}"' if f.get("youtube") else ""
    badge = "YouTube · click to play" if f.get("youtube") else "Muted preview · click for sound"
    return f"""<div class="film-media" data-slug="{f['slug']}"{yt} role="button" tabindex="0" aria-label="Play video: {escape(f['title'])}" data-testid="{testid}">
        <img class="film-poster" src="/assets/video/posters/{f['slug']}.jpg" width="{w}" height="{h}" alt="{alt}" loading="lazy" decoding="async" />
        <div class="film-play" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="rgba(255,255,255,0.95)"><circle cx="12" cy="12" r="11" fill="rgba(8,21,33,0.5)" stroke="rgba(255,255,255,0.85)" stroke-width="1"/><path d="M10 8l6 4-6 4V8z"/></svg>
        </div>
        <span class="film-badge">{badge}</span>
</div>"""


def films_html():
    cards = []
    for i, f in enumerate(DATA["films"]):
        cards.append(f"""<article class="film-card reveal" data-testid="film-card-{i}">
{indent(film_media(f, f"film-media-{i}"))}
        <div class="film-body">
                <div class="card-meta">{escape(f['meta'])}</div>
                <h2><a href="/{film_page_file(f)}" data-testid="film-page-link-{i}">{escape(f['title'])}</a></h2>
                <p>{escape(f['desc'])}</p>
        </div>
</article>""")
    return indent("\n".join(cards), 32)


def projects_html():
    cards = []
    for i, p in enumerate(DATA["projects"]):
        tags = "".join(f'<span class="tag-chip">{escape(t)}</span>' for t in p["tags"])
        cards.append(f"""<article class="project-card reveal" data-testid="project-card-{i}">
        <div class="card-meta">Personal Project · {p['date']}</div>
        <h2><a href="/{p['slug']}.html" data-testid="project-page-link-{i}">{escape(p['name'])}</a></h2>
        <p>{escape(p['card'])}</p>
        <div class="tag-row">{tags}</div>
        <a class="explore-go project-more" href="/{p['slug']}.html" aria-label="Read more about {escape(p['name'])}" data-testid="project-more-{i}">Read the full project <span aria-hidden="true">→</span></a>
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
    html = html.replace("{{PROJECTS}}", projects_html())
    html = re.sub(r'(<div class="container">)', r'\1\n' + indent(breadcrumb(page), 16), html, count=1)
    return html + "\n" + next_links(page)


def info_rows(rows):
    return "\n".join(f'<div class="about-info-row"><span class="k">{k}</span><span class="v">{v}</span></div>'
                     for k, v in rows)


def project_page(i, p):
    projects = DATA["projects"]
    prev, nxt = projects[i - 1], projects[(i + 1) % len(projects)]
    page = {"file": f"{p['slug']}.html", "nav": "projects", "crumb": p["short"], "type": "WebPage",
            "parents": [("Projects", "/projects.html")], "title": p["title"], "desc": p["metaDesc"],
            "entity_obj": project_object(p)}
    did = "\n".join(f"<li>{escape(d)}</li>" for d in p["did"])
    chips = "".join(f'<span class="tag-chip">{escape(t)}</span>' for t in p["threats"])
    tags = "".join(f'<span class="tag-chip">{escape(t)}</span>' for t in p["tags"])
    related = "\n".join(f'<li><a href="{h}">{escape(t)}</a></li>' for h, t in p["related"])
    facts = info_rows([("Type", "Personal project"), ("Date", p["date"]), ("Focus", escape(p["focus"])),
                       ("Skills", escape(" · ".join(p["tags"])))])
    main_html = f"""<article class="section page-first on-paper detail" id="project" data-testid="project-detail">
        <div class="container">
{indent(breadcrumb(page), 16)}
                <header class="sec-head sec-head--split reveal">
                        <span class="sec-index">0{i + 1}</span>
                        <h1>{escape(p['name'])}</h1>
                        <span class="sec-kicker">Personal Project · {p['date']}</span>
                </header>
                <div class="detail-grid">
                        <div class="detail-copy reveal">
                                <p class="lead">{escape(p['card'])}</p>
                                <h2>What I did</h2>
                                <ul class="detail-list">
{indent(did, 40)}
                                </ul>
                                <h2>{escape(p['threatsTitle'])}</h2>
                                <div class="tag-row">{chips}</div>
                                <h2>Skills applied</h2>
                                <div class="tag-row">{tags}</div>
                                <div class="detail-actions">
                                        <a href="https://github.com/Jackie-legit" target="_blank" rel="noopener" class="btn btn-ghost" data-testid="project-github-btn">View GitHub Profile</a>
                                        <a href="/contact.html" class="btn btn-rust" data-testid="project-contact-btn">Ask me about this project</a>
                                </div>
                        </div>
                        <aside class="about-info reveal" aria-label="Project facts">
{indent(facts, 32)}
                                <h2 class="detail-aside-title">Related</h2>
                                <ul class="detail-related">
{indent(related, 40)}
                                        <li><a href="/projects.html">All projects</a></li>
                                </ul>
                        </aside>
                </div>
        </div>
</article>
{pager(f"/{prev['slug']}.html", prev['short'], f"/{nxt['slug']}.html", nxt['short'])}"""
    return page, main_html


def film_page(i, f):
    films = DATA["films"]
    prev, nxt = films[i - 1], films[(i + 1) % len(films)]
    title = f"{f['title']} | Flight Training Video"
    desc = f"{f['desc']} Flight training video by Jacqueline Magawa · {f['meta']}."
    page = {"file": film_page_file(f), "nav": "films", "crumb": f["title"], "type": "WebPage",
            "parents": [("Training Films", "/training-films.html")],
            "title": title if len(title) <= 60 else f"{f['title']} | Training Video",
            "desc": desc if len(desc) <= 160 else f"{f['desc']} A flight training video by Jacqueline Magawa.",
            "entity_obj": video_object(f)}
    w, h = img_size(f"assets/video/posters/{f['slug']}.jpg")
    if f.get("youtube"):
        player = film_media(f, "film-page-media")
    else:
        player = f"""<video class="film-player" controls preload="none" playsinline width="{w}" height="{h}" poster="/assets/video/posters/{f['slug']}.jpg" data-testid="film-page-video">
        <source src="/assets/video/{f['slug']}.mp4" type="video/mp4" />
        Your browser can't play this video. <a href="/assets/video/{f['slug']}.mp4">Download it instead</a>.
</video>"""
    more = "\n".join(f"""<li><a href="/{film_page_file(o)}" data-testid="film-more-{j}"><img src="/assets/video/posters/{o['slug']}.jpg" alt="" width="160" height="90" loading="lazy" decoding="async" /><span><b>{escape(o['title'])}</b><small>{escape(o['meta'])}</small></span></a></li>"""
                     for j, o in enumerate(films) if o is not f)
    mins, secs = re.match(r"PT(\d+)M(\d+)S", f["duration"]).groups()
    facts = info_rows([("When &amp; where", escape(f["meta"])), ("Length", f"{int(mins)} min {int(secs)} s"),
                       ("Pilot in training", "Jacqueline Magawa")])
    main_html = f"""<article class="section page-first on-cream detail" id="film" data-testid="film-detail">
        <div class="container">
{indent(breadcrumb(page), 16)}
                <header class="sec-head sec-head--split reveal">
                        <span class="sec-index">{i + 1:02d}</span>
                        <h1>{escape(f['title'])}</h1>
                        <span class="sec-kicker">Training film</span>
                </header>
                <div class="film-feature reveal">
{indent(player, 24)}
                </div>
                <div class="detail-grid">
                        <div class="detail-copy reveal">
                                <p class="lead">{escape(f['desc'])}</p>
                                <p>Part of Jacqueline Magawa's flight log, the training journey that began with EAA Young Eagles flights and led to an FAA Student Pilot Certificate. See the full <a href="/flight-log.html">flight log timeline</a> or browse the <a href="/gallery.html">photo gallery</a>.</p>
                        </div>
                        <aside class="about-info reveal" aria-label="Film facts">
{indent(facts, 32)}
                        </aside>
                </div>
                <h2 class="detail-more-title">More training films</h2>
                <ul class="film-more">
{indent(more, 24)}
                </ul>
        </div>
</article>
{pager(f"/{film_page_file(prev)}", prev['title'], f"/{film_page_file(nxt)}", nxt['title'])}"""
    return page, main_html


def recruiter_main():
    projects = "\n".join(f"""<li><a href="/{p['slug']}.html"><b>{escape(p['name'])}</b></a><span>{escape(p['desc'])}</span></li>"""
                         for p in DATA["projects"])
    return f"""<article class="section page-first on-paper recruiter" id="recruiter" data-testid="recruiter-summary">
        <div class="container">
{indent(breadcrumb(RECRUITER), 16)}
                <header class="recruiter-head reveal">
                        <div>
                                <p class="eyebrow"><span class="dot"></span>Recruiter summary</p>
                                <h1>Jacqueline Magawa</h1>
                                <p class="recruiter-role">B.S. Computer Science, minor in Cybersecurity (University at Albany, 2027) · A.S. Aviation Management (2024)</p>
                        </div>
                        <div class="recruiter-actions no-print">
                                <button type="button" class="btn btn-rust" data-print data-testid="recruiter-print-btn">Print / Save as PDF</button>
                                <a href="/assets/resume-jacqueline-magawa.pdf" download class="btn btn-ghost" data-testid="recruiter-resume-btn">Download Résumé</a>
                        </div>
                </header>
                <div class="recruiter-grid">
                        <section class="recruiter-block reveal" aria-labelledby="rs-seeking">
                                <h2 id="rs-seeking">Seeking</h2>
                                <p>Internships and full-time roles in cybersecurity, IT, or aviation, anywhere the two intersect. Highly motivated to start as a Flight Attendant. Open to roles worldwide.</p>
                        </section>
                        <section class="recruiter-block reveal" aria-labelledby="rs-contact">
                                <h2 id="rs-contact">Contact</h2>
                                <ul class="recruiter-list">
                                        <li><a href="mailto:jacqmagawa.ernest@gmail.com" data-testid="recruiter-email">jacqmagawa.ernest@gmail.com</a></li>
                                        <li><a href="tel:+19176901977" data-testid="recruiter-phone">+1 (917) 690-1977</a></li>
                                        <li>Albany, NY, USA</li>
                                        <li><a href="https://www.linkedin.com/in/jacquelinem25/" target="_blank" rel="noopener">linkedin.com/in/jacquelinem25</a></li>
                                        <li><a href="https://github.com/Jackie-legit" target="_blank" rel="noopener">github.com/Jackie-legit</a></li>
                                        <li><a href="/">jacqmagawa.com</a></li>
                                </ul>
                        </section>
                        <section class="recruiter-block reveal" aria-labelledby="rs-education">
                                <h2 id="rs-education">Education</h2>
                                <ul class="recruiter-list">
                                        <li><b>University at Albany, SUNY</b><span>B.S. Computer Science, minor in Cybersecurity · 2024 – 2027</span></li>
                                        <li><b>Dutchess Community College</b><span>A.S. Aviation Science (Pilot) → Aviation Management · 2021 – 2024</span></li>
                                </ul>
                        </section>
                        <section class="recruiter-block reveal" aria-labelledby="rs-credentials">
                                <h2 id="rs-credentials">Credentials</h2>
                                <ul class="recruiter-list">
                                        <li><b>FAA Student Pilot Certificate</b><span>Issued 26 Aug 2021 · FAA Part 61</span></li>
                                        <li><b>EAA Young Eagles</b><span>Flights with certified instructors since 2011</span></li>
                                        <li><b>Presidential Education Award</b><span>Outstanding Academic Excellence</span></li>
                                </ul>
                        </section>
                        <section class="recruiter-block reveal" aria-labelledby="rs-tech">
                                <h2 id="rs-tech">Technical skills</h2>
                                <ul class="recruiter-list">
                                        <li><b>Languages &amp; tools</b><span>Java, C, Linux, GitHub, IntelliJ IDEA, Eclipse, Visual Studio Code</span></li>
                                        <li><b>Cybersecurity</b><span>Threat modeling, defense-in-depth, risk-based strategy, MITRE ATT&amp;CK</span></li>
                                        <li><b>Systems</b><span>Computer networking, operating systems, data structures</span></li>
                                        <li><b>IT support</b><span>Ticketing systems, help-desk workflows, troubleshooting for 100+ users a term</span></li>
                                        <li><b>Microsoft Excel</b><span>Formulas, sorting, and data handling</span></li>
                                </ul>
                        </section>
                        <section class="recruiter-block reveal" aria-labelledby="rs-service">
                                <h2 id="rs-service">Service &amp; communication</h2>
                                <ul class="recruiter-list">
                                        <li><b>Customer service</b><span>Puts people from every background at ease</span></li>
                                        <li><b>Bilingual</b><span>Fluent in English and Swahili</span></li>
                                        <li><b>Clear communication</b><span>Strong written and verbal skills under pressure</span></li>
                                        <li><b>Organization</b><span>Relied on daily for coursework and flight training</span></li>
                                </ul>
                        </section>
                        <section class="recruiter-block recruiter-wide reveal" aria-labelledby="rs-projects">
                                <h2 id="rs-projects">Projects</h2>
                                <ul class="recruiter-list">
{indent(projects, 40)}
                                </ul>
                        </section>
                        <section class="recruiter-block recruiter-wide reveal" aria-labelledby="rs-flight">
                                <h2 id="rs-flight">Flight training highlights</h2>
                                <ul class="recruiter-list">
                                        <li><b>2011</b><span>First flight with the EAA Young Eagles program, age 11</span></li>
                                        <li><b>2015</b><span>First front-seat flight, taxi and takeoff roll at Brookhaven Airport, Shirley, NY</span></li>
                                        <li><b>2019</b><span>Mid-air training at Republic Airport, Farmingdale, and a cross-country flight to Edgartown (Martha's Vineyard)</span></li>
                                        <li><b>2021</b><span>FAA Student Pilot Certificate · 4 training airports flown across New York</span></li>
                                </ul>
                        </section>
                </div>
                <p class="recruiter-foot">Full portfolio: <a href="/">jacqmagawa.com</a> · <a href="/projects.html">Projects</a> · <a href="/training-films.html">Training films</a></p>
        </div>
</article>"""


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
    for p in DATA["projects"]:
        entries.append(url(f"{SITE}/{p['slug']}.html", "0.7"))
    for f in DATA["films"]:
        mins, secs = re.match(r"PT(\d+)M(\d+)S", f["duration"]).groups()
        loc = (f"<video:player_loc>https://www.youtube.com/embed/{f['youtube']}</video:player_loc>" if f.get("youtube")
               else f"<video:content_loc>{SITE}/assets/video/{f['slug']}.mp4</video:content_loc>")
        entries.append(url(f"{SITE}/{film_page_file(f)}", "0.6", f"""
    <video:video>
      <video:thumbnail_loc>{SITE}/assets/video/posters/{f['slug']}.jpg</video:thumbnail_loc>
      <video:title>{escape(f['title'])}</video:title>
      <video:description>{escape(f['desc'] + ' ' + f['meta'])}</video:description>
      {loc}
      <video:duration>{int(mins) * 60 + int(secs)}</video:duration>
    </video:video>"""))
    entries.append(url(f"{SITE}/{RECRUITER_FILE}", "0.7"))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1" '
            'xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">\n' + "\n".join(entries) + "\n</urlset>\n")


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
    details = [project_page(i, p) for i, p in enumerate(DATA["projects"])]
    details += [film_page(i, f) for i, f in enumerate(DATA["films"])]
    for page, main_html in details:
        (ROOT / page["file"]).write_text(render(page, main_html))
    (ROOT / RECRUITER_FILE).write_text(render(RECRUITER, recruiter_main()))
    nf = render(NOT_FOUND, NOT_FOUND_MAIN).replace(
        '<meta name="robots" content="index, follow, max-image-preview:large" />',
        '<meta name="robots" content="noindex, follow" />')
    nf = re.sub(r'\s*<link rel="canonical"[^>]*>', "", nf)
    (ROOT / "404.html").write_text(nf)
    sm = sitemap()
    (ROOT / "sitemap.xml").write_text(sm)
    (ROOT / "backend" / "sitemap.xml").write_text(sm)
    (ROOT / "robots.txt").write_text(ROBOTS)
    print("Built", 3 + len(PAGES) + len(details), "pages + sitemap.xml + robots.txt")


if __name__ == "__main__":
    main()
