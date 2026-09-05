import os
import asyncio
import hmac
import logging
import time
import html as html_lib
from collections import defaultdict, deque
from datetime import datetime, timezone

import resend
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from motor.motor_asyncio import AsyncIOMotorClient

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
        raise HTTPException(status_code=502, detail="Could not send your message right now. Please email jacq.magawa@gmail.com directly.")

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

    return {
        "total": len(docs),
        "by_day": [{"date": k, "count": v} for k, v in sorted(by_day.items(), reverse=True)],
        "messages": docs,
    }


app.include_router(api)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)
