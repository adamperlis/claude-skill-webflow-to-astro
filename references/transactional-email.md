# App email on Cloudflare (off Resend or MailerSend)

For an owner whose apps send their own mail (sign-up confirmations, password
resets, receipts, waitlist replies) through Resend, MailerSend or a similar
service, and who wants it on the Cloudflare account the site now lives in.
It's optional, and it changes how their domain's mail is sent: explain it,
give the cost, and do it only on a yes.

The forms on the site are a different, free case: Email Routing's
`send_email` binding to verified destinations (`dns-and-email.md`).

## What it costs (it isn't free)

- **Sending to anyone needs Workers Paid**, at $5 a month. That includes
  3,000 emails a month, then $0.35 per 1,000. Without it, Email Sending only
  reaches the account's verified addresses.
- **A new account starts on a daily quota** (1,000 a day on one checked in
  October 2026), shown on each domain's Email Sending page. It grows with
  good sending.
- **Say it to the owner like this:** *"Your apps' email moves to the same
  Cloudflare account as your site, for $5 a month including 3,000 emails.
  Each app switches with one setting and can switch back the same way."*

## What should stay where it is

- **Scheduled and bulk sends.** Cloudflare has no "send later" (no
  `send_at`). A newsletter that relies on its provider holding a scheduled
  send stays there, or gets a Worker on a cron trigger to do the sending.
  Big lists also wait until the daily quota has grown.
- **Mail from customers' own domains.** A multi-tenant app that sends as
  each customer's domain can't move: every sending domain has to be a zone
  in this account.
- **Mail from a domain that isn't on Cloudflare DNS.** Move the zone first
  (`domains.md`), or send from another of the owner's domains that is.

## The plan, one app at a time

1. **Onboard each sending domain** (below).
2. **Create one token** for all the apps (below) and store it once.
3. **Ship the code switch** with the old provider still the default, so
   merging changes nothing (below).
4. **Flip one app:** set `EMAIL_PROVIDER=cloudflare`, redeploy, and trigger
   a real email to an address the owner can check, such as a password
   reset or a waitlist sign-up. Check the sender, the reply-to, and that it
   didn't land in spam.
5. **Move back** by unsetting the variable. Keep the old provider's key
   until every app has run on Cloudflare for a while.
6. **Close the old provider** only after nothing has gone through it for a
   week, and after any scheduled sends it holds have gone out. Then offer
   to remove its SPF `include:` and DKIM records (`SKILL.md`, step 12's
   mail clean-up). Ask first.

## Onboard a domain

Compute → Email Service → Email Sending → Onboard Domain. Pick the zone, and
leave Subdomain blank to send as the apex (`hello@example.com`).

- **The records Cloudflare adds:** three MX, an SPF TXT, and a DKIM TXT,
  all on `cf-bounce` (`cf-bounce.example.com` and
  `cf-bounce._domainkey.example.com`). The apex MX and SPF aren't touched,
  so the owner's mailboxes (Google Workspace, Microsoft 365) keep working.
- **DMARC:** an existing `_dmarc` record is kept as it is. With none, the
  onboarding adds `v=DMARC1; p=reject;`, which rejects any mail claiming to
  be from the domain that isn't signed for it.
  - **Before activating a domain without DMARC,** list who sends as it:
    every `_domainkey` record and every SPF `include:`. A sender that signs
    with DKIM on the domain passes. An unsigned one (a CRM, an old mailer)
    would start bouncing. If there is one, tell the owner and ask.
  - **Check the records in the dashboard** (DNS → Records, searching
    `TXT`, `MX`, `domainkey`), not with a local lookup. A resolver that
    fails can return nothing, which reads as "no records".
- **Onboarded the wrong name?** Settings → Disable removes the records
  Cloudflare manages. The DMARC record it added is unlocked and stays:
  delete that one by hand, and only that one.

## The token

My Profile → API Tokens → Create Token → Custom token:

- **Permission:** Account / Email Sending / Edit.
- **Account resources:** include only the owner's one account.
- **Expiry:** as the owner prefers.

Cloudflare shows the value once. Have the owner click Copy and run a script
that saves it to their keychain and sets it on each app's host as a
**sensitive** variable (`CLOUDFLARE_EMAIL_TOKEN`, with `CLOUDFLARE_ACCOUNT_ID`
beside it). It is never printed, pasted into chat or put on a command line.
Lost before it was copied? On that token's row, ⋯ → Roll gives a new value.

## The REST API

`POST https://api.cloudflare.com/client/v4/accounts/{account_id}/email/sending/send`
with `Authorization: Bearer <token>`.

```json
{
  "from": { "address": "hello@example.com", "name": "Example" },
  "to": "person@example.org",
  "bcc": ["support@example.com"],
  "reply_to": "support@example.com",
  "subject": "Reset your password",
  "text": "…",
  "html": "<p>…</p>"
}
```

- **Named addresses are `{ address, name }`.** `{ email, name }` is the
  Workers binding's shape, and REST rejects it. Every address field takes a
  plain string too.
- **`reply_to` is a field of its own.** A `Reply-To` among `headers` is
  rejected.
- **`to`, `cc` and `bcc` together hold at most 50 addresses.** Send one
  message per recipient for anything user-facing, so nobody sees the
  others.
- **Size:** the whole message, attachments included, must be 5 MiB or
  less. Attachments are base64 `content`, `filename`, `type` and
  `disposition`.
- **Headers:** only those on Cloudflare's allowed list. For
  `List-Unsubscribe`, the URL goes in angle brackets, with
  `List-Unsubscribe-Post: List-Unsubscribe=One-Click`.
- **Read the answer, not just the status.** A 200 carries `success` and,
  per recipient, `delivered`, `queued` or `permanent_bounces`. A permanent
  bounce comes back as a 200 and has to count as a failure.
- **Retry only 5xx and 429,** with a timeout on every call. Any other 4xx
  is a bad token, an unonboarded sender or a malformed message, and fails
  the same way again. Error `10103` means the key is the wrong kind of
  token, not an Email Sending one.

## SMTP, for auth services that only take SMTP

Supabase Auth and similar services send sign-up, reset and magic-link mail
through whatever SMTP server they're given:

- **Host** `smtp.mx.cloudflare.net`, **port** 465 (implicit TLS).
- **User** `api_token`, **password** the token.
- **Sender** an address on an onboarded domain.

It's live the moment it's saved. Before changing it, save the current
settings so it can be put back, and test with a password reset to the owner.

## The code switch

Keep the provider in one module that every send goes through, chosen by one
variable:

- **`EMAIL_PROVIDER`:** unset or blank means the old provider; `cloudflare`
  means Cloudflare; anything else fails loudly before sending.
- **Missing configuration names the variable** (`CLOUDFLARE_EMAIL_TOKEN is
  not set`), rather than failing as "couldn't send".
- **The sender address can depend on the provider.** MailerSend and Resend
  send only from domains verified with them. While an app can still fall
  back to the old provider, it keeps the address that provider has
  verified, and switches to the new one (say, a product's own domain) only
  on Cloudflare.
- **Test the exact request body** against the documented shape, field by
  field, for both providers. Tests that mock `fetch` pass whatever is sent,
  so a misnamed field (`email` for `address`) only shows up on the first
  real send.
- **A sign-up or a payment never fails because its email did.** Log it and
  carry on, unless the email is the point of the request, like a sign-in
  link.
