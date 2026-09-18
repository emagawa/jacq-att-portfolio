# Hosting jacqmagawa.com on Bluehost — Complete Guide

This guide moves your portfolio off Emergent and onto your existing **Bluehost** plan.
Read **Section 0** first — it explains what transfers cleanly and what needs a small change.

---

## 0. Understand your site (read this first)

Your project has **two parts**:

| Part | What it is | Moves to Bluehost? |
|------|------------|--------------------|
| **Static site** | `index.html`, `css/`, `js/`, `assets/` (images + videos), `sitemap.xml`, `robots.txt`, favicon | ✅ Yes — simple file upload |
| **Backend (API)** | Contact form, private dashboard (`/api/admin`), résumé analytics, weekly email digest | ⚠️ Needs Python + MongoDB — **not** a file copy |

**What this means:**
- The visible website (everything a visitor sees) will work perfectly on Bluehost.
- The **contact form** needs a tiny replacement on Bluehost — this guide gives you a ready-made `contact.php` so it keeps sending email (Section 6).
- The **private dashboard / résumé analytics / weekly digest** rely on a database + a running Python program. Shared Bluehost can't run those as-is. Section 7 gives you 3 clear options (from "drop them" to "keep them running elsewhere").

Good news: On Bluehost (normal Apache hosting) the "homepage catch-all" problem you hit on Emergent **goes away**, so your **`sitemap.xml` and `robots.txt` at the root will finally work normally** (Section 8).

---

## 1. Download your website files from GitHub

Your code is already saved to **`emagawa/jacq-att-portfolio`**. Two ways to get it:

### Option A — Download as ZIP (easiest, no tools)
1. Go to `https://github.com/emagawa/jacq-att-portfolio`
2. Click the green **`< > Code`** button → **Download ZIP**
3. Unzip it on your computer. You now have a folder `jacq-att-portfolio/`.

### Option B — Clone with Git (if you have Git installed)
```bash
git clone https://github.com/emagawa/jacq-att-portfolio.git
cd jacq-att-portfolio
```

---

## 2. Pick ONLY the files you upload to Bluehost

From the downloaded folder, you will upload **these** to Bluehost:

```
index.html
css/            (whole folder)
js/             (whole folder)
assets/         (whole folder — images + videos + resume PDF)
sitemap.xml
robots.txt
googlee2baf0cc1b65fae8.html   (Google verification file)
contact.php     (you'll create this from Section 6)
```

**Do NOT upload these** (they're backend/dev files and some contain secrets):
```
backend/        ← Python API + secrets, not used on Bluehost
frontend/       ← the Node dev server, not needed
memory/         ← internal notes
test_reports/   ← internal
.git/  .emergent/  node_modules/
*.env  (any file named .env — these hold your private API keys!)
BLUEHOST_HOSTING.md  (this guide — optional)
```

> ⚠️ **Never upload any `.env` file** or `backend/server.py` to public hosting — they can contain your Resend API key and admin token.

---

## 3. Log in to Bluehost & open File Manager

1. Log in at **https://www.bluehost.com** → **Hosting** → **cPanel** (or **Advanced**).
2. Open **File Manager**.
3. Navigate to **`public_html`** — this is your website's root folder.
   - If `jacqmagawa.com` is your **primary** domain, files go directly in `public_html`.
   - If it's an **add-on/secondary** domain, files go in `public_html/jacqmagawa.com` (Bluehost tells you the exact folder when you add the domain).

---

## 4. Upload the static site

### Fast method (recommended): upload a ZIP and extract
1. On your computer, select `index.html`, `css/`, `js/`, `assets/`, `sitemap.xml`, `robots.txt`, and the Google file, and compress them into a single `site.zip`.
2. In File Manager, make sure you're inside `public_html`, click **Upload**, choose `site.zip`.
3. Back in File Manager, right-click `site.zip` → **Extract** → extract into `public_html`.
4. Delete `site.zip` afterward.

### Alternative: FTP
- Host: `ftp.jacqmagawa.com` (or the server name Bluehost shows)
- Username / password: create an FTP account in cPanel → **FTP Accounts**
- Use **FileZilla** (free) → drag the files into `public_html`.

> 📁 Keep the folder structure exactly the same (`css/`, `js/`, `assets/` must sit next to `index.html`). Your site uses relative paths, so structure matters.

**Test:** visit `https://jacqmagawa.com` — the site should load. (If images/videos are missing, the folder structure got flattened — re-check `assets/` is intact.)

---

## 5. Point your domain to Bluehost

Since you no longer want Emergent to route the domain, point `jacqmagawa.com` at Bluehost:

- **If you bought the domain through Bluehost:** nothing to do — it already points there.
- **If the domain is at another registrar (or was pointed at Emergent):**
  1. In Bluehost cPanel, find your account's **nameservers** (usually `ns1.bluehost.com`, `ns2.bluehost.com`), **or** your server's **A record IP** (cPanel → shows "Shared IP Address").
  2. At your domain registrar, either:
     - Set the **nameservers** to Bluehost's, **or**
     - Set an **A record** for `@` (and `www`) to Bluehost's IP.
  3. Remove any old records pointing to Emergent.
- DNS changes take **a few minutes to 48 hours** to propagate.

> Do this step **after** you've uploaded files and confirmed the site works via a temporary Bluehost URL, so there's no downtime.

---

## 6. Make the contact form work on Bluehost (`contact.php`)

Your form currently posts to `/api/contact` (the Python backend). On Bluehost we replace that with a small PHP file that sends the same emails through **Resend** (keeps your verified domain + good deliverability). No Python, no database.

### Step 6a — Create `contact.php`
A ready-to-use version is included in this repo at **`bluehost/contact.php`**. Upload it into `public_html` (next to `index.html`).

Then open it in File Manager (right-click → Edit) and fill in your real values at the top:
```php
$RESEND_API_KEY   = 'PASTE_YOUR_RESEND_API_KEY_HERE';   // from resend.com/api-keys
$SENDER_EMAIL     = 'hello@jacqmagawa.com';
$RECIPIENT_EMAIL  = 'jacq.magawa@gmail.com';
$AUTOREPLY_REPLY  = 'jacqmagawa.ernest@gmail.com';
```
> 🔒 Because this is server-side PHP, your key is **not** exposed to visitors. Just never paste it into a public GitHub file.

### Step 6b — Point the form at `contact.php`
In your downloaded copy, open **`js/main.js`**, find this line (there's one occurrence):
```js
const res = await fetch("/api/contact", {
```
change it to:
```js
const res = await fetch("/contact.php", {
```
Save, then upload the updated `js/main.js` (overwrite the one on Bluehost).

**Test:** submit the form on your live Bluehost site → you should receive the email + the visitor gets the auto-reply.

---

## 7. The dashboard, résumé analytics & weekly digest

These three features need a **database (MongoDB)** and a **running Python program** — shared Bluehost can't do that. Choose one:

**Option 1 — Drop them (simplest).**
Just don't upload `admin.html`; skip the analytics/digest. Your public site + contact form still work 100%. Best if you don't need visitor stats.

**Option 2 — Keep the Python backend running for free elsewhere, point to it.**
- Deploy the `backend/` folder to a free/cheap Python host (e.g., **Render.com**, **Railway**, **Fly.io**) and use **MongoDB Atlas** (free tier) for the database.
- Then in your Bluehost `js/main.js`, set the API calls to the full backend URL (e.g., `https://your-api.onrender.com/api/...`) instead of relative paths.
- You'd visit the dashboard at `https://your-api.onrender.com/api/admin`.
- This keeps everything working, but it's a second service to manage.

**Option 3 — Use a form service instead of the whole backend.**
Replace `contact.php` with a free form provider like **Formspree** or **Web3Forms** (no code/server). You lose the dashboard/analytics/digest but gain zero maintenance. (Section 6's `contact.php` is usually the better middle ground.)

> Recommendation for a portfolio on Bluehost: **Option 1 + `contact.php`** — everything visitors touch works, with nothing extra to maintain.

---

## 8. Sitemap & robots on Bluehost (this gets EASIER)

On Bluehost, root files serve normally, so:
1. Make sure `sitemap.xml` and `robots.txt` are in `public_html`.
2. Edit `robots.txt` so the Sitemap line reads:
   ```
   Sitemap: https://jacqmagawa.com/sitemap.xml
   ```
3. In **Google Search Console → Sitemaps**, remove the old `api/sitemap.xml` entry and submit **`sitemap.xml`**. It will read correctly now.
4. Your Google verification still works via the meta tag already in `index.html` (nothing to change).

---

## 9. Enable HTTPS (SSL)

1. cPanel → **SSL/TLS Status** (or **Security → SSL**).
2. Bluehost provides **free AutoSSL (Let's Encrypt)** — click **Run AutoSSL** for `jacqmagawa.com`.
3. Force HTTPS: cPanel → **Domains** → toggle **Force HTTPS Redirect** (or add a redirect rule).

---

## 10. Go-live checklist

- [ ] Static files uploaded to `public_html` (structure intact)
- [ ] `https://jacqmagawa.com` loads with images + videos
- [ ] `contact.php` uploaded and filled with your real values
- [ ] `js/main.js` updated to post to `/contact.php`
- [ ] Test contact form → email received + auto-reply received
- [ ] `sitemap.xml` + `robots.txt` present; sitemap resubmitted in GSC
- [ ] SSL active (padlock shows) + HTTPS forced
- [ ] Domain DNS pointed to Bluehost (do last)
- [ ] Decide on dashboard/analytics (Option 1/2/3 in Section 7)

---

## Notes & tips

- **Videos are large** (~40 MB+ each). They'll work on Bluehost but use bandwidth; if pages feel slow, consider hosting videos on YouTube/Vimeo and embedding.
- **Keep a copy** of your GitHub repo as your backup/source of truth.
- **Your Resend account is unchanged** — the same verified `jacqmagawa.com` domain and API key work from `contact.php`.
- If you ever want the full dashboard back without managing a server, that's when Option 2 (Render + Atlas) makes sense.

Questions on any step? Bluehost 24/7 support can help with cPanel/File Manager/DNS specifics for your exact plan.
