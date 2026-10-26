# SEO Playbook for jacqmagawa.com

## Part 1: Google Search Console (do this once, after the site is live)

Your domain is already verified with the meta tag on the homepage. Keep that tag. If you delete it, verification breaks.

1. Open https://search.google.com/search-console and pick the **jacqmagawa.com** property.
2. **Sitemaps** (left menu): remove the old `api/sitemap.xml` entry, then type `sitemap.xml` and click **Submit**. It should say "Success" and list **9 discovered pages**.
3. **URL Inspection** (search bar at the top): paste each URL below, click **Request indexing**, and wait for the confirmation before you move on to the next one.
   - https://jacqmagawa.com/
   - https://jacqmagawa.com/about.html
   - https://jacqmagawa.com/flight-log.html
   - https://jacqmagawa.com/education.html
   - https://jacqmagawa.com/skills.html
   - https://jacqmagawa.com/projects.html
   - https://jacqmagawa.com/training-films.html
   - https://jacqmagawa.com/gallery.html
   - https://jacqmagawa.com/contact.html
4. Check back in 3 to 14 days under **Pages → Indexed**. For any page marked "Discovered – currently not indexed", request indexing one more time. Backlinks (Part 2) are what fix this for good.
5. Also check these once a month: **Core Web Vitals** (should be "Good"), **Enhancements** (Breadcrumbs, Videos and Profile page should show as valid), and **Links** (to watch new backlinks come in).

Optional: add the site to **Bing Webmaster Tools** (https://www.bing.com/webmasters) with "Import from Google Search Console". It takes 2 minutes and also covers DuckDuckGo and Yahoo.

---

## Part 2: Backlink strategy (step by step)

A backlink is another website linking to yours. Google trusts a new site faster when real, relevant sites link to it. For a personal portfolio, **10 to 20 quality links** make a big difference. Never buy links: Google can penalise paid links.

Always link to your full address, **https://jacqmagawa.com**. When a site lets you choose, link straight to the best page for it (for example `/projects.html` from GitHub).

### Week 1: Profiles you already own (the easiest, strongest links)
| # | Where | What to do | Link to |
|---|-------|-----------|---------|
| 1 | **LinkedIn** | Profile → Edit intro → *Website* field. Also add it to **Contact info**, and as a **Featured** link. | `/` |
| 2 | **GitHub** (github.com/Jackie-legit) | Profile → Edit profile → *Website*. Also create a repo named `Jackie-legit` with a README that links to your site. | `/projects.html` |
| 3 | **GitHub project repos** | Add a "Portfolio: https://jacqmagawa.com/projects.html" line to each README (interpreter, SolarWinds case study). | `/projects.html` |
| 4 | **Handshake** (UAlbany career platform) | Profile → *Links / Portfolio*. | `/` |
| 5 | **Email signature** | Add the site to your Gmail signature (more people find it, though Google doesn't count this as a backlink). | `/` |
| 6 | **Résumé PDF** | Make sure the PDF shows https://jacqmagawa.com as a clickable link. | `/` |

### Week 2: School and aviation communities
| # | Where | What to do | Link to |
|---|-------|-----------|---------|
| 7 | **University at Albany**: CS department, Cybersecurity minor or student club pages (e.g. a cyber or ACM club) | Ask the club officer or department advisor whether there's a "student projects" or "member spotlight" page that can feature your portfolio. `.edu` links are especially valuable. | `/projects.html` |
| 8 | **Dutchess Community College**: Aviation program or alumni office | Email the aviation program coordinator: share your journey (A.S. 2024 → UAlbany CS) and ask to be listed as an alumni story. | `/about.html` |
| 9 | **EAA Young Eagles / local EAA chapter** | Many chapters post member stories. Offer a short "From Young Eagle to cybersecurity" story with your photos. | `/flight-log.html` |
| 10 | **Brookhaven Aviation / Brooklyn Flying Club** (their Facebook or website) | Ask whether they'd share your training films or link to your story. | `/training-films.html` |

### Weeks 3 and 4: Content that earns links
| # | Where | What to do | Link to |
|---|-------|-----------|---------|
| 11 | **Medium** or **dev.to** | Publish your SolarWinds case study as an article (2 to 4 minute read) and link back to the full project. | `/projects.html` |
| 12 | **Hashnode** or **dev.to** | Write "How I built an interpreter in Java" and link back. | `/projects.html` |
| 13 | **YouTube** | Upload 1 or 2 training films (e.g. the Farmingdale takeoff). Put `https://jacqmagawa.com/training-films.html` in the first line of the description and in your channel's About links. | `/training-films.html` |
| 14 | **Reddit** (r/flying, r/StudentPilot, r/cybersecurity, r/ITCareerQuestions) | Answer questions helpfully and only mention the site when it's relevant. Links in your Reddit profile are fine. | `/` |
| 15 | **Women in Aviation International** or **Women in CyberSecurity (WiCyS)** | Join (student rates are low), complete your member profile with your website, and apply to student spotlight features. | `/about.html` |

### Ongoing (about 15 minutes a month)
- Every new project gets its own GitHub repo with a link back to `/projects.html`.
- Every conference, hackathon, CTF or event you attend: add your site to your attendee or Devpost profile.
- When you're featured anywhere (news, club newsletter, scholarship page), ask them to include your link.
- In Search Console → **Links**, check which sites link to you and thank them. Ask happy contacts to link too.

### Avoid
- Paid link packages, "1,000 backlinks for $5", and link farms.
- Spamming the same link in comments or forums.
- Directory sites that aren't related to you.

---

## Part 3: What the site already does for SEO (for reference)
- Every section has its own page (with a title, description, canonical link, one H1 and breadcrumbs) and they all link to each other.
- `sitemap.xml` (with image entries) and `robots.txt` are at the root of the site.
- Structured data: Person, WebSite, ProfilePage, BreadcrumbList, VideoObject (training films), ImageGallery and the projects list.
- An OG image (1200 × 630) for LinkedIn, Facebook and X previews.
- Compressed images, an optimised portrait for faster loading, lazy-loaded gallery and video posters, and a deferred script.
- HTTPS is enforced, and `www.` redirects to `https://jacqmagawa.com`.
- To edit content: change `src/sections/*.html` or `src/data.json`, then run `python3 scripts/build_site.py`.
