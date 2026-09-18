# Test Credentials

This is a static portfolio site with a contact-form backend + a private analytics view.

## Resend (email)
- Provider: Resend (domain jacqmagawa.com verified per user — "done")
- Sender (SENDER_EMAIL): hello@jacqmagawa.com
- Recipient (RECIPIENT_EMAIL): jacqmagawa.ernest@gmail.com
- Auto-reply reply-to (AUTOREPLY_REPLY_TO): jacqmagawa.ernest@gmail.com
- Behavior: on contact submit, a notification email goes to RECIPIENT_EMAIL and a friendly auto-reply goes to the visitor's email.

## Private Analytics View
- URL: /admin.html (also excluded from search engines via noindex)
- Endpoint: GET /api/admin/messages?token=<ADMIN_TOKEN>
- ADMIN_TOKEN (in backend/.env): WY_gYP7OEtDYZ9xOaoYheA5BwunRN8y4
- Enter the token on /admin.html to view total messages, last-7-days count, per-day breakdown, and the message list.
