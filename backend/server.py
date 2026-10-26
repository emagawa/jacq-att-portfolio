import os
import asyncio
import hmac
import logging
import time
import html as html_lib
from collections import defaultdict, deque
from datetime import datetime, timezone, timedelta

import resend
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from motor.motor_asyncio import AsyncIOMotorClient
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("jacq-portfolio")

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME")
RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL")
AUTOREPLY_REPLY_TO = os.environ.get("AUTOREPLY_REPLY_TO")
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN")

resend.api_key = RESEND_API_KEY

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

ADMIN_DASHBOARD_HTML = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="robots" content="noindex, nofollow" />
    <title>Jacqueline Magawa | Aviation Enthusiast &amp; Cybersecurity / CS Student</title>
    <link rel="icon" type="image/png" href="/assets/img/favicon-32.png" />
    <link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png" />
    <style>
      :root { --cream:#f3f1ea; --ink:#13293b; --rust:#c0503c; --muted:#8a8577; --line:#e3ded2; }
      * { box-sizing: border-box; }
      body { margin:0; background:var(--cream); color:var(--ink); font-family:"Outfit",system-ui,-apple-system,sans-serif; padding:40px 22px 80px; }
      .wrap { max-width:900px; margin:0 auto; }
      h1 { font-size:28px; font-weight:600; margin:0 0 4px; }
      .sub { color:var(--muted); font-size:14px; margin:0 0 28px; }
      .gate { background:#fff; border:1px solid var(--line); border-radius:14px; padding:26px; max-width:420px; }
      .gate label { display:block; font-size:13px; color:var(--muted); margin-bottom:8px; text-transform:uppercase; letter-spacing:1px; }
      input[type="password"] { width:100%; padding:12px 14px; border:1px solid var(--line); border-radius:10px; font-size:15px; margin-bottom:14px; font-family:inherit; }
      button { background:var(--ink); color:var(--cream); border:0; border-radius:999px; padding:12px 24px; font-size:15px; cursor:pointer; font-family:inherit; transition:background-color .2s ease; }
      button:hover { background:var(--rust); }
      .err { color:var(--rust); font-size:14px; margin-top:10px; min-height:18px; }
      .stats { display:flex; gap:16px; flex-wrap:wrap; margin-bottom:16px; }
      .stat { background:#fff; border:1px solid var(--line); border-radius:14px; padding:20px 24px; flex:1; min-width:150px; }
      .stat .num { font-size:40px; font-weight:700; line-height:1; color:var(--rust); }
      .stat .lbl { font-size:13px; color:var(--muted); margin-top:8px; text-transform:uppercase; letter-spacing:1px; }
      .card { background:#fff; border:1px solid var(--line); border-radius:14px; overflow:hidden; margin:24px 0; }
      .card h2 { font-size:15px; margin:0; padding:16px 20px; border-bottom:1px solid var(--line); text-transform:uppercase; letter-spacing:1px; color:var(--muted); font-weight:600; }
      table { width:100%; border-collapse:collapse; font-size:14px; }
      th, td { text-align:left; padding:12px 20px; border-bottom:1px solid var(--line); vertical-align:top; }
      th { font-size:12px; text-transform:uppercase; letter-spacing:1px; color:var(--muted); }
      tr:last-child td { border-bottom:0; }
      .msg { color:#2c3e50; white-space:pre-wrap; }
      .empty { padding:40px 20px; text-align:center; color:var(--muted); }
      .hidden { display:none; }
      .when { color:var(--muted); white-space:nowrap; }
      .day-row { display:flex; justify-content:space-between; padding:10px 20px; border-bottom:1px solid var(--line); font-size:14px; }
      .day-row:last-child { border-bottom:0; }
      .day-row .counts span { margin-left:16px; color:var(--muted); }
      .day-row .counts strong { color:var(--ink); }
      .topbar { display:flex; justify-content:space-between; align-items:center; margin-bottom:26px; }
      .backlink { color:var(--ink); text-decoration:none; font-size:12px; text-transform:uppercase; letter-spacing:2px; font-family:ui-monospace,"JetBrains Mono",monospace; transition:color .2s ease; }
      .backlink:hover { color:var(--rust); }
      .signout { background:transparent; color:var(--muted); border:1px solid var(--line); border-radius:999px; padding:8px 18px; font-size:12px; text-transform:uppercase; letter-spacing:2px; cursor:pointer; font-family:ui-monospace,"JetBrains Mono",monospace; transition:all .2s ease; }
      .signout:hover { background:var(--ink); color:var(--cream); border-color:var(--ink); }
      .digestbar { display:flex; align-items:center; gap:16px; flex-wrap:wrap; margin:8px 0 20px; }
      .digestbtn { background:var(--rust); color:#fff; border:0; border-radius:999px; padding:12px 26px; font-size:14px; cursor:pointer; font-family:inherit; transition:opacity .2s ease; }
      .digestbtn:hover { opacity:0.88; }
      .digestbtn:disabled { opacity:0.5; cursor:default; }
      .digestmsg { font-size:14px; }
    </style>
  </head>
  <body>
    <div class="wrap">
      <div class="topbar">
        <a class="backlink" href="/">&larr; Back to site</a>
        <button id="signOut" type="button" class="signout hidden">Sign out</button>
      </div>
      <h1>Contact Messages</h1>
      <p class="sub">Private dashboard · jacqmagawa.com</p>
      <div id="gate" class="gate">
        <label for="token">Access token</label>
        <input id="token" type="password" placeholder="Enter admin token" />
        <button id="loginBtn">View dashboard</button>
        <div id="err" class="err"></div>
      </div>
      <div id="dash" class="hidden">
        <div class="stats">
          <div class="stat"><div class="num" id="total">0</div><div class="lbl">Total messages</div></div>
          <div class="stat"><div class="num" id="last7">0</div><div class="lbl">Messages · last 7 days</div></div>
        </div>
        <div class="stats">
          <div class="stat"><div class="num" id="resPreview">0</div><div class="lbl">Résumé previews</div></div>
          <div class="stat"><div class="num" id="resDownload">0</div><div class="lbl">Résumé downloads</div></div>
        </div>
        <div class="card"><h2>Top résumé days</h2><div id="topResDays"></div></div>
        <div class="card"><h2>Résumé activity by day</h2><div id="resByday"></div></div>
        <div class="card"><h2>Messages by day</h2><div id="byday"></div></div>
        <div class="card"><h2>Recent messages</h2><div id="tableWrap"></div></div>
        <div class="digestbar">
          <button id="digestBtn" type="button" class="digestbtn">Send weekly digest now</button>
          <span id="digestMsg" class="digestmsg"></span>
        </div>
      </div>
    </div>
    <script>
      var API = "/api/admin/messages";
      var gate = document.getElementById("gate");
      var dash = document.getElementById("dash");
      var err = document.getElementById("err");
      function fmt(iso){ if(!iso) return ""; var d=new Date(iso); if(isNaN(d)) return iso; return d.toLocaleString(undefined,{month:"short",day:"numeric",year:"numeric",hour:"numeric",minute:"2-digit"}); }
      function esc(s){ var div=document.createElement("div"); div.textContent = s==null?"":String(s); return div.innerHTML; }
      async function load(){
        var token = document.getElementById("token").value.trim();
        err.textContent="";
        if(!token){ err.textContent="Please enter your token."; return; }
        var res;
        try { res = await fetch(API + "?token=" + encodeURIComponent(token)); }
        catch(e){ err.textContent="Network error. Please try again."; return; }
        if(res.status===401){ err.textContent="Invalid token."; return; }
        if(!res.ok){ err.textContent="Something went wrong ("+res.status+")."; return; }
        render(await res.json());
      }
      function render(data){
        gate.classList.add("hidden"); dash.classList.remove("hidden");
        document.getElementById("signOut").classList.remove("hidden");
        document.getElementById("total").textContent = data.total;
        var weekAgo = Date.now() - 7*24*60*60*1000;
        var last7 = (data.messages||[]).filter(function(m){ var t=new Date(m.created_at).getTime(); return !isNaN(t) && t>=weekAgo; }).length;
        document.getElementById("last7").textContent = last7;
        var r = data.resume || {preview_total:0, download_total:0, by_day:[]};
        document.getElementById("resPreview").textContent = r.preview_total || 0;
        document.getElementById("resDownload").textContent = r.download_total || 0;
        var resByday = document.getElementById("resByday");
        if(!r.by_day || !r.by_day.length){ resByday.innerHTML='<div class="empty">No résumé activity yet.</div>'; }
        else { resByday.innerHTML = r.by_day.map(function(d){ return '<div class="day-row"><span>'+esc(d.date)+'</span><span class="counts"><span>previews <strong>'+d.preview+'</strong></span><span>downloads <strong>'+d.download+'</strong></span></span></div>'; }).join(""); }
        var topEl = document.getElementById("topResDays");
        var ranked = (r.by_day || []).map(function(d){ return {date:d.date, total:(d.preview||0)+(d.download||0), preview:d.preview||0, download:d.download||0}; })
          .filter(function(d){ return d.total>0; })
          .sort(function(a,b){ return b.total-a.total; })
          .slice(0,5);
        if(!ranked.length){ topEl.innerHTML='<div class="empty">No résumé activity yet.</div>'; }
        else { topEl.innerHTML = ranked.map(function(d,i){ return '<div class="day-row"><span>'+(i===0?'🔥 ':'')+esc(d.date)+'</span><span class="counts"><strong>'+d.total+'</strong> views <span>('+d.preview+' prev · '+d.download+' dl)</span></span></div>'; }).join(""); }
        var byday = document.getElementById("byday");
        if(!data.by_day || !data.by_day.length){ byday.innerHTML='<div class="empty">No messages yet.</div>'; }
        else { byday.innerHTML = data.by_day.map(function(d){ return '<div class="day-row"><span>'+esc(d.date)+'</span><strong>'+d.count+'</strong></div>'; }).join(""); }
        var wrap = document.getElementById("tableWrap");
        if(!data.messages || !data.messages.length){ wrap.innerHTML='<div class="empty">No messages yet.</div>'; return; }
        var rows = data.messages.map(function(m){
          return "<tr><td class='when'>"+esc(fmt(m.created_at))+"</td><td><strong>"+esc(m.name)+"</strong><br><span style='color:#8a8577'>"+esc(m.email)+"</span></td><td>"+esc(m.subject||"(no subject)")+"<br><span class='msg'>"+esc(m.message)+"</span></td></tr>";
        }).join("");
        wrap.innerHTML = "<table><thead><tr><th>When</th><th>From</th><th>Subject / Message</th></tr></thead><tbody>"+rows+"</tbody></table>";
      }
      document.getElementById("loginBtn").addEventListener("click", load);
      document.getElementById("token").addEventListener("keydown", function(e){ if(e.key==="Enter") load(); });
      document.getElementById("digestBtn").addEventListener("click", async function(){
        var token = document.getElementById("token").value.trim();
        var msg = document.getElementById("digestMsg");
        var btn = document.getElementById("digestBtn");
        btn.disabled = true; msg.textContent = "Sending…"; msg.style.color = "#8a8577";
        try {
          var res = await fetch("/api/admin/send-digest?token=" + encodeURIComponent(token), { method: "POST" });
          var data = await res.json();
          if(res.ok && data.status === "sent"){ msg.textContent = "✓ Digest emailed (" + data.stats.messages + " messages, " + (data.stats.previews + data.stats.downloads) + " résumé views)"; msg.style.color = "#2e7d32"; }
          else if(data.status === "error"){ msg.textContent = "Failed to send: " + (data.detail || "error"); msg.style.color = "#c0503c"; }
          else { msg.textContent = "Could not send (" + res.status + ")"; msg.style.color = "#c0503c"; }
        } catch(e){ msg.textContent = "Network error."; msg.style.color = "#c0503c"; }
        btn.disabled = false;
      });
      document.getElementById("signOut").addEventListener("click", function(){
        document.getElementById("token").value = "";
        dash.classList.add("hidden");
        gate.classList.remove("hidden");
        document.getElementById("signOut").classList.add("hidden");
        err.textContent = "";
      });
    </script>
  </body>
</html>"""

app = FastAPI(title="Jacqueline Magawa Portfolio API")
api = APIRouter(prefix="/api")


class ContactRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr
    subject: str = Field(default="", max_length=200)
    message: str = Field(..., min_length=1, max_length=5000)
    website: str = Field(default="")  # honeypot


# Simple in-memory per-IP rate limiter for the public contact endpoint.
RATE_LIMIT_MAX = 5          # allowed requests
RATE_LIMIT_WINDOW = 600     # per 600 seconds (10 minutes)
_rate_hits: dict[str, deque] = defaultdict(deque)


def check_rate_limit(ip: str) -> bool:
    now = time.monotonic()
    hits = _rate_hits[ip]
    while hits and now - hits[0] > RATE_LIMIT_WINDOW:
        hits.popleft()
    if len(hits) >= RATE_LIMIT_MAX:
        return False
    hits.append(now)
    return True


def build_email_html(name: str, email: str, subject: str, message: str) -> str:
    safe_name = html_lib.escape(name)
    safe_email = html_lib.escape(email)
    safe_subject = html_lib.escape(subject or "(no subject)")
    safe_message = html_lib.escape(message).replace("\n", "<br>")
    return f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="background:#f3f1ea;padding:28px 0;font-family:Arial,Helvetica,sans-serif;">
      <tr><td align="center">
        <table width="560" cellpadding="0" cellspacing="0" style="background:#ffffff;border:1px solid #e3ded2;border-radius:14px;overflow:hidden;">
          <tr><td style="background:#12283a;padding:22px 30px;">
            <div style="color:#e9c46a;font-size:12px;letter-spacing:2px;text-transform:uppercase;">New Portfolio Message</div>
            <div style="color:#f3f1ea;font-size:20px;font-weight:700;margin-top:6px;">jacqmagawa.com — Contact Form</div>
          </td></tr>
          <tr><td style="padding:28px 30px;color:#12283a;">
            <p style="margin:0 0 6px;font-size:13px;color:#9a6b3f;text-transform:uppercase;letter-spacing:1px;">From</p>
            <p style="margin:0 0 18px;font-size:16px;"><b>{safe_name}</b> &lt;{safe_email}&gt;</p>
            <p style="margin:0 0 6px;font-size:13px;color:#9a6b3f;text-transform:uppercase;letter-spacing:1px;">Subject</p>
            <p style="margin:0 0 18px;font-size:16px;">{safe_subject}</p>
            <p style="margin:0 0 6px;font-size:13px;color:#9a6b3f;text-transform:uppercase;letter-spacing:1px;">Message</p>
            <div style="margin:0;font-size:15px;line-height:1.6;color:#2c3e50;background:#f7f5ee;border-left:3px solid #c0503c;padding:14px 16px;border-radius:6px;">{safe_message}</div>
          </td></tr>
          <tr><td style="background:#f7f5ee;padding:16px 30px;color:#8a8577;font-size:12px;">
            Sent from the contact form on jacqmagawa.com
          </td></tr>
        </table>
      </td></tr>
    </table>
    """


def build_autoreply_html(name: str) -> str:
    safe_name = html_lib.escape(name.strip().split(" ")[0] or "there")
    return f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="background:#f3f1ea;padding:28px 0;font-family:Arial,Helvetica,sans-serif;">
      <tr><td align="center">
        <table width="560" cellpadding="0" cellspacing="0" style="background:#ffffff;border:1px solid #e3ded2;border-radius:14px;overflow:hidden;">
          <tr><td style="background:#12283a;padding:24px 30px;">
            <div style="color:#e9c46a;font-size:12px;letter-spacing:2px;text-transform:uppercase;">Message Received</div>
            <div style="color:#f3f1ea;font-size:22px;font-weight:700;margin-top:6px;">Thanks for reaching out!</div>
          </td></tr>
          <tr><td style="padding:30px;color:#12283a;font-size:16px;line-height:1.7;">
            <p style="margin:0 0 16px;">Hi {safe_name},</p>
            <p style="margin:0 0 16px;">Thanks so much for your message — it landed safely in my inbox and I'll get back to you personally as soon as I can, usually within a day or two.</p>
            <p style="margin:0 0 16px;">In the meantime, feel free to explore my flight log, projects, and training films on the site.</p>
            <p style="margin:0 0 4px;">Warmly,</p>
            <p style="margin:0;font-weight:700;color:#c0503c;">Jacqueline Magawa</p>
            <p style="margin:2px 0 0;font-size:13px;color:#8a8577;">Aviation &amp; Cybersecurity · jacqmagawa.com</p>
          </td></tr>
          <tr><td style="background:#f7f5ee;padding:14px 30px;color:#8a8577;font-size:12px;">
            This is an automated confirmation from jacqmagawa.com — please don't reply directly.
          </td></tr>
        </table>
      </td></tr>
    </table>
    """


@api.get("/")
async def root():
    return {"status": "ok", "service": "jacqueline-magawa-portfolio"}


@api.get("/health")
async def health():
    return {"status": "healthy"}


@api.post("/contact")
async def contact(payload: ContactRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Too many messages. Please try again in a little while.",
        )

    # Honeypot: silently accept bots without sending
    if payload.website.strip():
        return {"status": "success", "message": "Thanks — your message has been sent."}

    record = {
        "name": payload.name,
        "email": payload.email,
        "subject": payload.subject,
        "message": payload.message,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        await db.contact_messages.insert_one(dict(record))
    except Exception as e:
        logger.error(f"Failed to store contact message: {e}")

    params = {
        "from": f"Jacqueline Magawa Portfolio <{SENDER_EMAIL}>",
        "to": [RECIPIENT_EMAIL],
        "reply_to": payload.email,
        "subject": f"[Portfolio] {payload.subject or 'New message from ' + payload.name}",
        "html": build_email_html(payload.name, payload.email, payload.subject, payload.message),
    }
    try:
        email = await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Contact email sent: {email}")
    except Exception as e:
        logger.error(f"Failed to send contact email: {e}")
        raise HTTPException(status_code=502, detail="Could not send your message right now. Please email jacqmagawa.ernest@gmail.com directly.")

    # Friendly auto-reply confirmation to the visitor (best-effort).
    autoreply = {
        "from": f"Jacqueline Magawa <{SENDER_EMAIL}>",
        "to": [payload.email],
        "reply_to": AUTOREPLY_REPLY_TO,
        "subject": "Thanks for reaching out — Jacqueline Magawa",
        "html": build_autoreply_html(payload.name),
    }
    try:
        await asyncio.to_thread(resend.Emails.send, autoreply)
    except Exception as e:
        logger.error(f"Failed to send auto-reply: {e}")

    return {"status": "success", "message": "Thanks — your message has been sent."}


SITEMAP_PATH = os.path.join(ROOT_DIR, "sitemap.xml")


@api.get("/sitemap.xml")
async def sitemap():
    with open(SITEMAP_PATH, encoding="utf-8") as f:
        return Response(content=f.read(), media_type="application/xml")


@api.get("/admin", response_class=HTMLResponse)
async def admin_dashboard():
    return ADMIN_DASHBOARD_HTML


@api.get("/admin/messages")
async def admin_messages(token: str = ""):
    if not ADMIN_TOKEN or not hmac.compare_digest(token, ADMIN_TOKEN):
        raise HTTPException(status_code=401, detail="Unauthorized")

    cursor = db.contact_messages.find({}, {"_id": 0}).sort("created_at", -1)
    docs = await cursor.to_list(length=1000)

    by_day: dict[str, int] = defaultdict(int)
    for d in docs:
        day = (d.get("created_at") or "")[:10]
        if day:
            by_day[day] += 1

    resume_docs = await db.resume_events.find({}, {"_id": 0}).to_list(length=100000)
    preview_total = sum(1 for d in resume_docs if d.get("event") == "preview")
    download_total = sum(1 for d in resume_docs if d.get("event") == "download")
    resume_by_day: dict[str, dict] = defaultdict(lambda: {"preview": 0, "download": 0})
    for d in resume_docs:
        day = (d.get("created_at") or "")[:10]
        ev = d.get("event")
        if day and ev in ("preview", "download"):
            resume_by_day[day][ev] += 1

    return {
        "total": len(docs),
        "by_day": [{"date": k, "count": v} for k, v in sorted(by_day.items(), reverse=True)],
        "messages": docs,
        "resume": {
            "preview_total": preview_total,
            "download_total": download_total,
            "by_day": [
                {"date": k, "preview": v["preview"], "download": v["download"]}
                for k, v in sorted(resume_by_day.items(), reverse=True)
            ],
        },
    }


@api.delete("/admin/messages")
async def admin_clear_messages(token: str = ""):
    if not ADMIN_TOKEN or not hmac.compare_digest(token, ADMIN_TOKEN):
        raise HTTPException(status_code=401, detail="Unauthorized")
    result = await db.contact_messages.delete_many({})
    return {"status": "cleared", "deleted": result.deleted_count}


class TrackEvent(BaseModel):
    event: str


@api.post("/track/resume")
async def track_resume(payload: TrackEvent):
    if payload.event not in ("preview", "download"):
        raise HTTPException(status_code=422, detail="Invalid event")
    await db.resume_events.insert_one(
        {"event": payload.event, "created_at": datetime.now(timezone.utc).isoformat()}
    )
    return {"status": "ok"}


async def compute_digest_stats():
    since = datetime.now(timezone.utc) - timedelta(days=7)
    since_iso = since.isoformat()
    messages = await db.contact_messages.find(
        {"created_at": {"$gte": since_iso}}, {"_id": 0}
    ).sort("created_at", -1).to_list(length=1000)
    resume_docs = await db.resume_events.find(
        {"created_at": {"$gte": since_iso}}, {"_id": 0}
    ).to_list(length=100000)
    previews = sum(1 for d in resume_docs if d.get("event") == "preview")
    downloads = sum(1 for d in resume_docs if d.get("event") == "download")
    by_day: dict[str, int] = defaultdict(int)
    for d in resume_docs:
        day = (d.get("created_at") or "")[:10]
        if day and d.get("event") in ("preview", "download"):
            by_day[day] += 1
    top_days = sorted(by_day.items(), key=lambda kv: kv[1], reverse=True)[:3]
    return {
        "messages": messages,
        "message_count": len(messages),
        "previews": previews,
        "downloads": downloads,
        "resume_total": previews + downloads,
        "top_days": [{"date": k, "count": v} for k, v in top_days],
    }


def build_digest_html(stats: dict) -> str:
    period_end = datetime.now(timezone.utc).strftime("%b %d, %Y")
    period_start = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%b %d")
    top_rows = "".join(
        f'<tr><td style="padding:6px 0;color:#12283a;">{html_lib.escape(d["date"])}</td>'
        f'<td style="padding:6px 0;text-align:right;color:#c0503c;font-weight:700;">{d["count"]}</td></tr>'
        for d in stats["top_days"]
    ) or '<tr><td style="padding:6px 0;color:#8a8577;" colspan="2">No résumé activity this week.</td></tr>'
    msg_rows = "".join(
        f'<tr><td style="padding:8px 0;border-top:1px solid #eee;">'
        f'<strong style="color:#12283a;">{html_lib.escape(m.get("name",""))}</strong> '
        f'<span style="color:#8a8577;">&lt;{html_lib.escape(m.get("email",""))}&gt;</span><br>'
        f'<span style="color:#555;">{html_lib.escape((m.get("subject") or "(no subject)"))}</span></td></tr>'
        for m in stats["messages"][:8]
    ) or '<tr><td style="padding:8px 0;color:#8a8577;">No new messages this week.</td></tr>'
    return f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="background:#f3f1ea;padding:28px 0;font-family:Arial,Helvetica,sans-serif;">
      <tr><td align="center">
        <table width="580" cellpadding="0" cellspacing="0" style="background:#ffffff;border:1px solid #e3ded2;border-radius:14px;overflow:hidden;">
          <tr><td style="background:#12283a;padding:24px 30px;">
            <div style="color:#e9c46a;font-size:12px;letter-spacing:2px;text-transform:uppercase;">Weekly Digest</div>
            <div style="color:#f3f1ea;font-size:22px;font-weight:700;margin-top:6px;">Your portfolio this week</div>
            <div style="color:#9fb3c4;font-size:13px;margin-top:4px;">{period_start} – {period_end}</div>
          </td></tr>
          <tr><td style="padding:26px 30px 8px;">
            <table width="100%" cellpadding="0" cellspacing="0"><tr>
              <td style="text-align:center;padding:10px;"><div style="font-size:34px;font-weight:700;color:#c0503c;">{stats['message_count']}</div><div style="font-size:12px;color:#8a8577;text-transform:uppercase;letter-spacing:1px;">Messages</div></td>
              <td style="text-align:center;padding:10px;"><div style="font-size:34px;font-weight:700;color:#c0503c;">{stats['previews']}</div><div style="font-size:12px;color:#8a8577;text-transform:uppercase;letter-spacing:1px;">Résumé previews</div></td>
              <td style="text-align:center;padding:10px;"><div style="font-size:34px;font-weight:700;color:#c0503c;">{stats['downloads']}</div><div style="font-size:12px;color:#8a8577;text-transform:uppercase;letter-spacing:1px;">Résumé downloads</div></td>
            </tr></table>
          </td></tr>
          <tr><td style="padding:14px 30px;">
            <div style="font-size:13px;text-transform:uppercase;letter-spacing:1px;color:#8a8577;margin-bottom:6px;">Top résumé days</div>
            <table width="100%" cellpadding="0" cellspacing="0">{top_rows}</table>
          </td></tr>
          <tr><td style="padding:14px 30px 8px;">
            <div style="font-size:13px;text-transform:uppercase;letter-spacing:1px;color:#8a8577;margin-bottom:6px;">Recent messages</div>
            <table width="100%" cellpadding="0" cellspacing="0">{msg_rows}</table>
          </td></tr>
          <tr><td style="padding:18px 30px;">
            <a href="https://jacqmagawa.com/api/admin" style="display:inline-block;background:#12283a;color:#f3f1ea;text-decoration:none;padding:10px 22px;border-radius:999px;font-size:14px;">Open dashboard</a>
          </td></tr>
          <tr><td style="background:#f7f5ee;padding:14px 30px;color:#8a8577;font-size:12px;">
            Automated weekly summary from jacqmagawa.com
          </td></tr>
        </table>
      </td></tr>
    </table>
    """


async def send_weekly_digest(force: bool = False) -> dict:
    now = datetime.now(timezone.utc)
    week_key = f"{now.isocalendar().year}-W{now.isocalendar().week:02d}"
    if not force:
        already = await db.digest_log.find_one({"week": week_key})
        if already:
            logger.info(f"Weekly digest already sent for {week_key}, skipping.")
            return {"status": "skipped", "week": week_key}

    stats = await compute_digest_stats()
    params = {
        "from": f"Jacqueline Magawa Portfolio <{SENDER_EMAIL}>",
        "to": [RECIPIENT_EMAIL],
        "subject": f"Your weekly portfolio digest — {stats['message_count']} messages, {stats['resume_total']} résumé views",
        "html": build_digest_html(stats),
    }
    try:
        await asyncio.to_thread(resend.Emails.send, params)
        await db.digest_log.update_one(
            {"week": week_key},
            {"$set": {"week": week_key, "sent_at": now.isoformat(), "stats": {
                "messages": stats["message_count"],
                "previews": stats["previews"],
                "downloads": stats["downloads"],
            }}},
            upsert=True,
        )
        logger.info(f"Weekly digest sent for {week_key}.")
        return {"status": "sent", "week": week_key, "stats": {
            "messages": stats["message_count"],
            "previews": stats["previews"],
            "downloads": stats["downloads"],
        }}
    except Exception as e:
        logger.error(f"Failed to send weekly digest: {e}")
        return {"status": "error", "detail": str(e)}


@api.post("/admin/send-digest")
async def admin_send_digest(token: str = ""):
    if not ADMIN_TOKEN or not hmac.compare_digest(token, ADMIN_TOKEN):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return await send_weekly_digest(force=True)


scheduler = AsyncIOScheduler(timezone="America/New_York")


@app.on_event("startup")
async def start_scheduler():
    scheduler.add_job(
        send_weekly_digest,
        CronTrigger(day_of_week="mon", hour=8, minute=0, timezone="America/New_York"),
        id="weekly_digest",
        replace_existing=True,
    )
    if not scheduler.running:
        scheduler.start()
    logger.info("Weekly digest scheduler started (Mondays 08:00 America/New_York).")


app.include_router(api)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)
