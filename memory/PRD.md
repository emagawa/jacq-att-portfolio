# PRD — Jacqueline Magawa Portfolio (jacq-att-portfolio)

## Problem statement
Finish and polish the existing static portfolio for Jacqueline Magawa (aviation + cybersecurity). Make it production-ready, restyle to the aesthetic of https://cathemagawa.com, add a real email-sending contact form, straighten the gallery grid, and redesign the Flight Log as a vertical "Experience"-style timeline. Preview only for now (no deploy).

## Tech / architecture
- Static site (HTML/CSS/vanilla JS) at repo root: `index.html`, `css/style.css`, `js/main.js`, `assets/`.
- Served on port 3000 by a small Node static server: `/app/frontend/server.js` (supervisor `frontend`).
- FastAPI backend on 8001 (`/app/backend/server.py`), routes prefixed `/api`.
  - `GET /api/health`
  - `POST /api/contact` → stores message in Mongo (`db.contact_messages`) + sends email via Resend. Honeypot field `website`.
- Email: Resend (`onboarding@resend.dev` sender). Recipient env-driven.

## Design system (matches reference)
- Palette: cream `#f3f1ea`, deep navy `#13293b`, terracotta `#c0503c`, teal `#2f7d6b`, gold `#d99a3a`.
- Fonts: Sora (display), Hanken Grotesk (body), JetBrains Mono (labels/section numbers).
- Elements: numbered sections (01–07), dark scrolling marquee, arched dashed-frame portrait, flowing SVG connector line, grain texture, reduced-motion fallback.

## Implemented (2026-06)
- Full aesthetic redesign across all sections.
- Flight Log → vertical timeline (date / tag / title / org / description; milestone markers).
- Gallery → uniform straight 4-col grid (responsive 3/2 cols) + lightbox.
- Marquee band, hero with two-tone name + arched portrait.
- Contact form → real backend email via Resend (+ Mongo storage, honeypot spam guard, loading/success/error states).
- Reduced-motion accessibility fallback.
- Tested: backend 100% (7 pytest cases), frontend 100% (all sections, nav, timeline, gallery+lightbox, film play, contact e2e).

## Known limitation
- Resend is in TEST MODE: emails deliver only to the account owner (`jacqmagawa.ernest@gmail.com`). To deliver to `jacq.magawa@gmail.com` in production, verify a domain at resend.com/domains, then set a domain sender in `SENDER_EMAIL` and update `RECIPIENT_EMAIL`.

## Backlog / next
- P1: Verify Resend domain → route contact emails to jacq.magawa@gmail.com and set a branded sender.
- P2: Deploy to production when ready.
- P2: Optional CV/résumé preview, SEO/OpenGraph meta + social share image.

## Update (2026-06) — feature additions
- Résumé Preview: inline PDF modal opened from hero ('Preview Résumé') and About ('Preview Résumé'); download available in-modal, in About, and in nav. (tested 100%)
- Social Share Card: generated on-brand 1200x630 image at assets/img/og-image.jpg + full Open Graph & Twitter meta tags in index.html. (tested 100%)
- Deployment readiness: PASS (deployment_agent) — only cosmetic note that OG/canonical URLs point to preview domain; update to production domain after go-live.

## Go-live notes
- Deploy via Emergent Deploy button (50 credits/mo). After deploy, update og:url / og:image / canonical in index.html <head> to the production domain.
- Resend still in test mode (delivers to account owner only); verify a domain to deliver to jacq.magawa@gmail.com.

## Update (2026-06) — home differentiation + résumé thumbnail
- Résumé buttons upgraded to a "résumé chip" showing a real cover thumbnail (assets/img/resume-thumb.png, rendered from PDF page 1) in hero + About. (tested 100%)
- Per user feedback (make it less similar to cathemagawa.com): portrait changed to a SQUARE framed photo with a terracotta offset-outline accent (removed the arched shape), removed the hero curved SVG line, removed the vertical "STUDENT PILOT · ALBANY, NY" portrait label, and removed the scrolling marquee bar.
- Fixed entrance animation to animate transform only (opacity always 1) so hero content is never left invisible; deep-navy name now renders correctly.
- PENDING: user will deploy and paste the Emergent deploy URL; then update og:url / og:image / twitter:image / canonical in index.html to that domain.

## Update (2026-06) — contact cards + favicons
- Left-justified the 3rd ("Connect with me") and 4th ("Open to opportunities") contact cards: added `.c-connect, .c-open { flex-direction: column; align-items: flex-start; text-align: left; }` in style.css so their content stacks flush-left. (verified via computed styles + screenshot)
- Regenerated favicon.png (48), favicon-32.png (32) and apple-touch-icon.png (180) from the circular portrait logo (assets/img/logo-fa.png) to match site branding.
- Still pending (P2): update og:url / og:image / twitter:image / canonical to production domain after deploy (user has no final domain yet).

## Update (2026-06) — sections split
- Split the combined timeline into two sections: Flight Log (02, 7 aviation entries) and a new Education (03, 8 study/work/projects/now entries).
- Renumbered following sections: Checklist 04, Projects 05, Training Films 06, Gallery 07, Contact 08; alternated section backgrounds; added Education nav link.


## Update (2026-06) — mobile responsiveness + iterative polish
- Fixed mobile bugs (verified by testing_agent, iteration_6, 100%): (1) removed horizontal overflow caused by footer `white-space:nowrap`; (2) hamburger close-X now cream (`.nav-toggle.open span { background: var(--cream) }`) so it's visible on the dark slide-in menu; (3) footer centered on mobile (`.footer-inner` column + center); (4) reveal observer hardened (threshold 0.01, rootMargin, plus window-load safety fallback) so no `.reveal` tile stays invisible.
- Layout/typography tweaks per reference cathemagawa.com: container max-width 1536px + 80px side padding (responsive 40/22px); nav links 14px/500/1.68px; footer copyright 15px + tagline (IBM Plex Sans style 14px/500, rgb(174,184,192)); back-to-top orange button (#f5842a, 46px circle) added.
- Contact card: added "Preview Résumé" button (rust) next to "Download Résumé" (both 182x49, equal size); removed Résumé row from About.
- Content edits: Education degrees, hero stat labels, footer text (current: "© 2026 Jacqueline. All rights reserved." + "Jacqueline Magawa — CS in Cybersecurity, Class of 2027"). Removed Aug 2021 FAA Student Pilot Flight Log entry.

## Update (2026-09) — later iteration polish
- Custom cursor: single smooth blue dot (#1e6fe6, 9px) cloned from magawa.website — transform translate3d + translate(-50%,-50%), opacity-only transition, rAF lerp factor 0.1 (trails at a distance, settles on stop). Hides on hover over links/buttons. Hidden on touch.
- Mobile/tablet nav (<=1024px): changed from dark right slide-in to cathemagawa-style CREAM full-width TOP dropdown, dark navy left-aligned links, anchored below the 95px nav. Verified 100% (iteration_9).
- Training Films: multiple clips added/replaced with self-hosted MP4s (faststart) + generated posters; many clips had audio replaced/sequenced/crossfaded with uploaded royalty-free tracks; first-flight clip has music segments at 0:35 / 4:40 / 8:38 / end with original cockpit audio hard-muted during music and full in gaps.
- Numerous copy edits across About/Education/Flight Log/Gallery captions.
