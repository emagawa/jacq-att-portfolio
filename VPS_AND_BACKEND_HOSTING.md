# Hosting the FULL app (backend + database) — VPS or Render

Your portfolio has a **FastAPI backend + MongoDB** powering the contact form, private
dashboard (`/api/admin`), résumé analytics, and the weekly email digest.

To keep **all** of those features, you need somewhere that can run **Python** and **MongoDB**.

- **Option 2A — VPS (recommended for you):** run the entire app (frontend + backend + MongoDB)
  on one server, one domain. This is the closest to how it runs on Emergent.
- **Option 2B — Render.com + MongoDB Atlas (no server to manage):** host the backend on a
  managed platform, use a cloud database, and keep the static site wherever you like.

> ✅ Your instinct is correct: **a VPS with MongoDB + a Python runtime will run everything, exactly like Emergent.** If a Bluehost plan doesn't offer that, any VPS provider (DigitalOcean, Linode, Hetzner, Vultr, AWS Lightsail) works the same way.

---

## What the app needs (both options)

**Backend:** FastAPI app at `backend/server.py`, started with:
```
uvicorn server:app --host 127.0.0.1 --port 8001
```
Dependencies: `backend/requirements.txt`.

**Environment variables** (the backend reads these):
```
MONGO_URL=mongodb://localhost:27017     # or your Atlas connection string
DB_NAME=jacq_portfolio
RESEND_API_KEY=your_resend_key
SENDER_EMAIL=hello@jacqmagawa.com
RECIPIENT_EMAIL=jacqmagawa.ernest@gmail.com
AUTOREPLY_REPLY_TO=jacqmagawa.ernest@gmail.com
ADMIN_TOKEN=your_dashboard_token
```

**Frontend:** the static files (`index.html`, `css/`, `js/`, `assets/`) call the backend
using **relative `/api/...` paths**, so as long as the frontend and backend are served on the
**same domain** (a reverse proxy sends `/api` to the backend), you do **not** change `main.js` at all.

---

# OPTION 2A — Full app on a VPS (Ubuntu 22.04)

This puts everything on one box: MongoDB + FastAPI (via systemd) + Nginx serving the static
site and proxying `/api` to the backend. ~30–45 minutes.

### 1. Create the VPS
- Ubuntu 22.04 LTS, 1–2 GB RAM is plenty for a portfolio.
- SSH in: `ssh root@YOUR_SERVER_IP`

### 2. Install the essentials
```bash
apt update && apt upgrade -y
apt install -y python3-venv python3-pip nginx git gnupg curl
```

### 3. Install MongoDB (Community Edition)
```bash
curl -fsSL https://pgp.mongodb.com/server-7.0.asc | gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor
echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-7.0.list
apt update && apt install -y mongodb-org
systemctl enable --now mongod
systemctl status mongod        # should be "active (running)"
```

### 4. Get your code onto the server
```bash
cd /opt
git clone https://github.com/emagawa/jacq-att-portfolio.git jacq
cd jacq
```

### 5. Set up the Python backend
```bash
cd /opt/jacq/backend
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt
```

Create the backend env file `/opt/jacq/backend/.env`:
```bash
cat > /opt/jacq/backend/.env <<'EOF'
MONGO_URL=mongodb://localhost:27017
DB_NAME=jacq_portfolio
RESEND_API_KEY=PASTE_YOUR_RESEND_KEY
SENDER_EMAIL=hello@jacqmagawa.com
RECIPIENT_EMAIL=jacqmagawa.ernest@gmail.com
AUTOREPLY_REPLY_TO=jacqmagawa.ernest@gmail.com
ADMIN_TOKEN=PASTE_A_LONG_RANDOM_TOKEN
EOF
chmod 600 /opt/jacq/backend/.env
```

### 6. Run the backend as a service (systemd)
Create `/etc/systemd/system/jacq-api.service`:
```ini
[Unit]
Description=Jacqueline Magawa Portfolio API
After=network.target mongod.service

[Service]
WorkingDirectory=/opt/jacq/backend
ExecStart=/opt/jacq/backend/venv/bin/uvicorn server:app --host 127.0.0.1 --port 8001 --workers 1
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```
> Keep **`--workers 1`** so the weekly-digest scheduler runs in a single process (avoids duplicate emails; the code also guards per-week).

Start it:
```bash
systemctl daemon-reload
systemctl enable --now jacq-api
systemctl status jacq-api           # active (running)
curl -s http://127.0.0.1:8001/api/health   # {"status":"healthy"}
```

### 7. Serve the static site + proxy /api with Nginx
Put the static files where Nginx can serve them (the site files live at the repo root):
```bash
mkdir -p /var/www/jacqmagawa
cp -r /opt/jacq/index.html /opt/jacq/css /opt/jacq/js /opt/jacq/assets \
      /opt/jacq/sitemap.xml /opt/jacq/robots.txt \
      /opt/jacq/googlee2baf0cc1b65fae8.html /var/www/jacqmagawa/ 2>/dev/null
```

Create `/etc/nginx/sites-available/jacqmagawa`:
```nginx
server {
    listen 80;
    server_name jacqmagawa.com www.jacqmagawa.com;

    root /var/www/jacqmagawa;
    index index.html;

    # Send API calls to the FastAPI backend
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Everything else: serve the static site (real files first)
    location / {
        try_files $uri $uri/ /index.html;
    }

    client_max_body_size 200M;   # allows large videos/uploads
}
```
Enable + reload:
```bash
ln -s /etc/nginx/sites-available/jacqmagawa /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

### 8. Point DNS + enable HTTPS
- At your registrar, set an **A record** for `@` and `www` to `YOUR_SERVER_IP`.
- Once DNS resolves, get a free SSL cert:
```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d jacqmagawa.com -d www.jacqmagawa.com
```
Certbot auto-configures HTTPS + redirects.

### 9. Verify everything
- `https://jacqmagawa.com` → site loads (images/videos play)
- Contact form → email + auto-reply received
- `https://jacqmagawa.com/api/admin` → dashboard (log in with `ADMIN_TOKEN`)
- Résumé preview/download → counts appear in the dashboard
- `https://jacqmagawa.com/sitemap.xml` → real XML (submit this in GSC)
- Weekly digest emails every Monday 8 AM (America/New_York)

### Updating later
```bash
cd /opt/jacq && git pull
# if backend deps changed:
./backend/venv/bin/pip install -r backend/requirements.txt
systemctl restart jacq-api
# if static changed, re-copy to /var/www/jacqmagawa and: systemctl reload nginx
```

> ⚠️ On a VPS **you** own security/updates. Basic hardening: create a non-root sudo user,
> enable a firewall (`ufw allow OpenSSH; ufw allow 'Nginx Full'; ufw enable`), keep the OS patched,
> and never expose MongoDB to the internet (it stays on `localhost`).

---

# OPTION 2B — Backend on Render.com + MongoDB Atlas (no server to manage)

Use this if you'd rather not run a VPS. Static site stays on Bluehost (or anywhere);
the backend runs on Render's free/cheap tier with a free Atlas database.

### 1. Create a free MongoDB Atlas database
1. Sign up at **https://www.mongodb.com/cloud/atlas** → create a **free M0** cluster.
2. **Database Access** → add a user (username + password).
3. **Network Access** → allow `0.0.0.0/0` (or Render's IPs).
4. **Connect → Drivers** → copy the connection string, e.g.
   `mongodb+srv://USER:PASS@cluster0.xxxx.mongodb.net/?retryWrites=true&w=majority`

### 2. Deploy the backend on Render
1. Sign up at **https://render.com** → **New → Web Service** → connect your GitHub repo
   `emagawa/jacq-att-portfolio`.
2. Settings:
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn server:app --host 0.0.0.0 --port $PORT --workers 1`
3. **Environment** → add the variables:
   ```
   MONGO_URL   = your Atlas connection string
   DB_NAME     = jacq_portfolio
   RESEND_API_KEY = your key
   SENDER_EMAIL = hello@jacqmagawa.com
   RECIPIENT_EMAIL = jacqmagawa.ernest@gmail.com
   AUTOREPLY_REPLY_TO = jacqmagawa.ernest@gmail.com
   ADMIN_TOKEN = a long random token
   ```
4. Deploy. You'll get a URL like `https://jacq-api.onrender.com`.
   - Test: `https://jacq-api.onrender.com/api/health`
   - Dashboard: `https://jacq-api.onrender.com/api/admin`

### 3. Point the static site's API calls at Render
Because the backend is now on a **different domain**, edit your Bluehost `js/main.js` so the
API base is the Render URL. At the top of `main.js` add:
```js
const API_BASE = "https://jacq-api.onrender.com";
```
then change the calls:
```js
fetch(API_BASE + "/api/contact", { ... })
navigator.sendBeacon(API_BASE + "/api/track/resume", ...)   // and the fetch fallback
```
(These are near the contact-submit handler and the `trackResume()` function.)

> On Render's **free** tier the service may "sleep" after inactivity, so the first request after
> a quiet period can take ~30–60s to wake. A paid tier ($7/mo) keeps it always-on.

---

## Which should you pick?

| | VPS (2A) | Render + Atlas (2B) |
|---|---|---|
| Full app (dashboard, analytics, digest) | ✅ | ✅ |
| One domain, no code changes to `main.js` | ✅ | ✖ (needs API_BASE edit) |
| You manage OS/security/updates | Yes | No |
| Always-on | Yes | Free tier sleeps; paid always-on |
| Cost | one VPS bill | free tier or ~$7/mo + free DB |

**For you:** since you're already looking at VPS with MongoDB + Python, **Option 2A** gives you
the complete app on your own domain with zero feature loss — exactly what you want. Use the
static-only Bluehost guide (`BLUEHOST_HOSTING.md`) only if you decide to keep it simple without
the dashboard/analytics.

---

## One-command deploy / update (`deploy.sh`)

A ready-made script is in the repo root: **`deploy.sh`**. After the first VPS setup, updating
your live site is a single command:

```bash
sudo bash /opt/jacq/deploy.sh
```

It will: pull the latest code from GitHub → install any new backend dependencies → sync the
static files to the web root → restart the backend service → reload Nginx → run a health check.
If your paths differ from the guide, override them inline, e.g.:
```bash
sudo APP_DIR=/srv/jacq WEB_ROOT=/var/www/site SERVICE=my-api bash /srv/jacq/deploy.sh
```

Tip: make it executable once (`chmod +x /opt/jacq/deploy.sh`) and then just run
`sudo /opt/jacq/deploy.sh`.

---

## A note on "keep MongoDB on localhost"

MongoDB can listen either only on the server itself (`127.0.0.1`) or on all network interfaces
(`0.0.0.0`, i.e. the public internet).

- ✅ **Keep it on localhost.** Your FastAPI backend runs on the *same* VPS and connects via
  `mongodb://localhost:27017`, so the database never needs to be public.
- ⚠️ **Never bind it to `0.0.0.0`.** A default MongoDB has **no password**; bots constantly scan
  the internet for open port `27017` and will wipe/ransom exposed databases within hours.

The default `/etc/mongod.conf` already has `bindIp: 127.0.0.1` — leave it that way, and let the
firewall block `27017` from outside:
```bash
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw enable
# do NOT run: ufw allow 27017   (that would expose the database)
```
If you use **Atlas (Option 2B)** instead of a local MongoDB, this doesn't apply — Atlas is a
managed cloud database with its own authentication; you just use a username/password in the
connection string.

---

## Custom domain email (send & receive @jacqmagawa.com)

There are two separate things — don't confuse them:

**1. Sending mail from the site (already working):** your contact-form notifications and
auto-replies are sent through **Resend** using `hello@jacqmagawa.com`, on your verified domain.
Nothing to change — this works on Bluehost, VPS, or Render.

**2. Receiving mail at a real inbox like `jacq@jacqmagawa.com`:** this needs an **email host**
(a mailbox + MX DNS records). Pick one:

- **Bluehost email (easiest if you stay with Bluehost):** cPanel → **Email Accounts** →
  **Create** → e.g. `jacq@jacqmagawa.com`. Bluehost sets the MX records automatically when the
  domain is on their DNS. Read it via webmail or add to Gmail/Outlook.
- **Zoho Mail (free, works on a VPS):** sign up at zoho.com/mail, add `jacqmagawa.com`, verify
  it, and add the **MX records** Zoho gives you at your DNS provider:
  ```
  MX  @  mx.zoho.com       (priority 10)
  MX  @  mx2.zoho.com      (priority 20)
  MX  @  mx3.zoho.com      (priority 50)
  ```
  Then create `jacq@jacqmagawa.com` in Zoho.
- **Google Workspace (paid, most polished):** business Gmail at your domain (~$6/user/mo);
  add Google's MX records during setup.

> ⚠️ **Don't run your own mail server on the VPS.** Self-hosted email is hard to keep out of spam
> folders and easy to misconfigure. Use a hosted mailbox (above) for receiving, and keep Resend
> for sending from the site.

**Optional — make the site email match a real inbox:** if you create `jacq@jacqmagawa.com`, you
can set `AUTOREPLY_REPLY_TO=jacq@jacqmagawa.com` and `RECIPIENT_EMAIL=jacq@jacqmagawa.com` in the
backend `.env` (or in `contact.php`) so replies and notifications land in your branded inbox.

**Deliverability tip:** for best inbox placement, make sure your domain has **SPF**, **DKIM**,
and **DMARC** records. Resend shows the SPF/DKIM records to add when you verify your domain;
a simple DMARC record is:
```
TXT  _dmarc  v=DMARC1; p=none; rua=mailto:jacq@jacqmagawa.com
```

