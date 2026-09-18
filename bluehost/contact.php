<?php
/**
 * Bluehost contact-form handler for jacqmagawa.com
 * Drop this file in public_html (next to index.html) and fill in the 4 values below.
 * It sends a notification to you + a friendly auto-reply to the visitor, via Resend.
 * No database, no Python needed.
 */

// ---- FILL THESE IN (do NOT commit this file to a public repo after adding the key) ----
$RESEND_API_KEY  = 'PASTE_YOUR_RESEND_API_KEY_HERE';   // from https://resend.com/api-keys
$SENDER_EMAIL    = 'hello@jacqmagawa.com';             // must be on your verified Resend domain
$RECIPIENT_EMAIL = 'jacqmagawa.ernest@gmail.com';            // where you receive messages
$AUTOREPLY_REPLY = 'jacqmagawa.ernest@gmail.com';      // reply-to on the visitor's confirmation
// ---------------------------------------------------------------------------------------

header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['status' => 'error', 'message' => 'Method not allowed']);
    exit;
}

// Accept JSON body (the site posts JSON) or normal form POST.
$raw = file_get_contents('php://input');
$data = json_decode($raw, true);
if (!is_array($data)) { $data = $_POST; }

$name    = trim($data['name']    ?? '');
$email   = trim($data['email']   ?? '');
$subject = trim($data['subject'] ?? '');
$message = trim($data['message'] ?? '');
$website = trim($data['website'] ?? ''); // honeypot

// Honeypot: silently accept bots without sending.
if ($website !== '') {
    echo json_encode(['status' => 'success', 'message' => 'Thanks — your message has been sent.']);
    exit;
}

// Basic validation.
if ($name === '' || $message === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    http_response_code(422);
    echo json_encode(['status' => 'error', 'message' => 'Please provide your name, a valid email, and a message.']);
    exit;
}

// Trim overly long input.
$name    = mb_substr($name, 0, 120);
$subject = mb_substr($subject, 0, 200);
$message = mb_substr($message, 0, 5000);

function esc($s) { return htmlspecialchars($s, ENT_QUOTES, 'UTF-8'); }

function resend_send($apiKey, $payload) {
    $ch = curl_init('https://api.resend.com/emails');
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST           => true,
        CURLOPT_HTTPHEADER     => [
            'Authorization: Bearer ' . $apiKey,
            'Content-Type: application/json',
        ],
        CURLOPT_POSTFIELDS     => json_encode($payload),
        CURLOPT_TIMEOUT        => 20,
    ]);
    $resp = curl_exec($ch);
    $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    return [$code, $resp];
}

// 1) Notification to you.
$notifyHtml =
    '<div style="font-family:Arial,sans-serif;color:#12283a;">'
    . '<h2 style="color:#c0503c;">New message from jacqmagawa.com</h2>'
    . '<p><strong>Name:</strong> ' . esc($name) . '</p>'
    . '<p><strong>Email:</strong> ' . esc($email) . '</p>'
    . '<p><strong>Subject:</strong> ' . esc($subject !== '' ? $subject : '(none)') . '</p>'
    . '<p><strong>Message:</strong><br>' . nl2br(esc($message)) . '</p>'
    . '</div>';

list($code, $resp) = resend_send($RESEND_API_KEY, [
    'from'     => 'Jacqueline Magawa Portfolio <' . $SENDER_EMAIL . '>',
    'to'       => [$RECIPIENT_EMAIL],
    'reply_to' => $email,
    'subject'  => '[Portfolio] ' . ($subject !== '' ? $subject : 'New message from ' . $name),
    'html'     => $notifyHtml,
]);

if ($code < 200 || $code >= 300) {
    http_response_code(502);
    echo json_encode(['status' => 'error', 'message' => 'Could not send your message right now. Please email ' . $RECIPIENT_EMAIL . ' directly.']);
    exit;
}

// 2) Friendly auto-reply to the visitor (best-effort).
$firstName = esc(explode(' ', $name)[0] ?: 'there');
$replyHtml =
    '<div style="font-family:Arial,sans-serif;color:#12283a;line-height:1.7;">'
    . '<p>Hi ' . $firstName . ',</p>'
    . '<p>Thanks so much for your message — it landed safely in my inbox and I\'ll get back to you personally as soon as I can.</p>'
    . '<p>In the meantime, feel free to explore my flight log, projects, and training films on the site.</p>'
    . '<p>Warmly,<br><strong style="color:#c0503c;">Jacqueline Magawa</strong><br>'
    . '<span style="font-size:13px;color:#8a8577;">Aviation &amp; Cybersecurity · jacqmagawa.com</span></p>'
    . '</div>';

resend_send($RESEND_API_KEY, [
    'from'     => 'Jacqueline Magawa <' . $SENDER_EMAIL . '>',
    'to'       => [$email],
    'reply_to' => $AUTOREPLY_REPLY,
    'subject'  => 'Thanks for reaching out — Jacqueline Magawa',
    'html'     => $replyHtml,
]);

echo json_encode(['status' => 'success', 'message' => 'Thanks — your message has been sent.']);
