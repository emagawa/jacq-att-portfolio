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
