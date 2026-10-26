# DNS switch and email

Every change here is the owner's to approve, after they've reviewed the
pages.dev site. A switch that breaks mail is worse than no switch.

## Before anything: record what's there

- `dig` every name you know of: apex, www, MX, TXT, `_dmarc`, and the common
  DKIM selectors (`google._domainkey`, `selector1._domainkey`,
  `k1._domainkey`, `cf2024-1._domainkey`).
- If the zone is already on Cloudflare, export it:
  - Dashboard → DNS → Export.
  - Or the API. Wrangler's OAuth token can't read DNS records (it has
    `zone:read`, not `dns_records:read`).
- Note which records are Webflow's:
  - **apex:** A `198.202.211.1` (Webflow's current IP; older sites have
    `75.2.70.75` + `99.83.190.102`), or a CNAME/ALIAS to
    `proxy-ssl.webflow.com`.
  - **www:** CNAME `cdn.webflow.com` or `proxy-ssl.webflow.com`.
  - **verification:** TXT `_webflow` (one-time, removable after).

- **A scan isn't the list.** Third-party services hide records under names
  nobody guesses: a Ghost(Pro) newsletter domain is `ghost.blog`,
  `email.ghost.blog`, `<selector>._domainkey.ghost.blog` and `_dmarc.blog`. Read
  the registrar's own record list. At Porkbun the DNS page holds them in a
  script as `recordTracker['<TYPE><host><value>']` (the table may render
  empty). Certificate logs (`crt.sh/?q=%25.<domain>`) show past hostnames.
- **If `dig` can't reach port 53** (a VPN), use DNS over HTTPS:
  `https://cloudflare-dns.com/dns-query?name=…&type=…` with
  `accept: application/dns-json`.

## If DNS lives at the registrar (Porkbun, GoDaddy, Namecheap…)

Either:

- **A. Move the zone to Cloudflare (recommended).**
  1. Write the full list as a BIND zone file and add the site in
     Cloudflare (Free plan) with "Upload a DNS zone file", not the scan.
     Turn off "Bot Preference Sync" there if the site ships its own
     robots.txt.
  2. **The import proxies every A and CNAME,** zone file or not. Set them
     all to DNS only (grey cloud) before activating: proxying a Ghost,
     Mailgun or Webflow CNAME breaks its certificate or its mail.
  3. Check the copy before switching: read the records back (dashboard API,
     `/api/v4/zones/<id>/dns_records`) and compare each value with what the
     registrar serves (hash both; DKIM keys are long).
  4. Check DNSSEC is off (no `DS` record) or turn it off first.
  5. Switch the nameservers at the registrar. Porkbun asks with a native
     confirm dialog that browser automation can't click: the owner clicks
     OK. The registry (RDAP: `rdap.verisign.com/com/v1/domain/<domain>`)
     shows the change at once; resolvers keep the old nameservers up to two
     days, harmless when both serve the same records. Then "Check
     nameservers" (`PUT /zones/<id>/activation_check`): active in minutes.
  6. Zone settings: Email Address Obfuscation off, Always Use HTTPS, TLS
     1.2 minimum.
  7. Then do the Pages custom-domain step.

  Mail keeps flowing throughout, as long as the MX/TXT records were copied
  exactly.

- **B. Keep registrar DNS.**
  1. Add the custom domains in the Pages project. It shows the CNAME target
     (`<project>.pages.dev`).
  2. Set www as a CNAME at the registrar. The apex needs ALIAS/ANAME/CNAME
     flattening, which some registrars support (Porkbun does, as ALIAS).
  3. Verify the TXT records Pages asks for.

## Pages custom domains (zone on Cloudflare)

1. **Add the domains:** the canonical host as a custom domain of the Pages
   project (dashboard, or `POST /accounts/{id}/pages/projects/{name}/domains`),
   then point its record at `<project>.pages.dev` (proxied CNAME).
   - **Just after a nameserver change**, Pages may validate through a
     resolver still holding the old answer and mark the domain
     "deactivated". Retry once the record is in place:
     `PATCH …/domains/<name>` (it went active within minutes).
   - **The host that only redirects** (the apex when www is canonical)
     needn't be a Pages domain: a proxied record plus the Redirect Rule is
     enough, and Cloudflare's own certificate covers it. Added to Pages, its
     certificate check gets redirected too and errors.
2. **Remove only the Webflow records,** and nothing else.
3. **www → apex:** a Redirect Rule (Rules → Redirect Rules → template
   "Redirect from WWW to root"), 301, preserving the path and query. Keep a
   proxied www record (CNAME to the apex) so the rule has something to run
   on. Flip it if www is the canonical host.
4. **HTTPS:** turn on Always Use HTTPS and set minimum TLS 1.2. HSTS comes
   from `_headers`, without `includeSubDomains` unless every subdomain
   serves HTTPS.
5. **Verify:**
   - `curl -sI https://apex/`: Cloudflare, no `x-wf-*` headers.
   - Every sitemap URL returns 200 with its canonical.
   - The redirects return 301.
   - www redirects with its path.
   - The certificate is active.
   - The forms send.
6. **Afterwards:**
   - Resubmit the sitemap in Search Console and Bing Webmaster Tools, and
     request indexing (URL inspection) for the home page and the top pages
     from the baseline: about ten a day. New pages show "Discovered,
     currently not indexed"; request those too.
   - Check analytics on the live host after accepting cookies in a test
     browser: `/g/collect` requests to the GA4 id, one `page_view` per page
     (not two: GA4 in GTM and in the page would double count).
   - Turn on Crawler Hints (IndexNow), if the owner agrees: Caching →
     Configuration (the API refuses a session cookie for it).
   - DMARC: Email → DMARC Management adds Cloudflare's report address to
     the existing record and keeps the policy.
   - Optionally, redirect `<project>.pages.dev` to the domain with a Bulk
     Redirect. The canonical tags already name the domain.
   - Check for Email Address Obfuscation's damage. It's on by default and
     rewrites anything shaped like `name@x.y`, package versions included,
     to "[email protected]". Turn it off, or use `<!--email_off-->`; see
     SKILL.md step 11.
   - If there's no DMARC record, offer Cloudflare's DMARC Management: a
     `p=none` monitoring record, with reports to Cloudflare. It's the
     owner's click.

## Email to anyone (auto-replies)

Email Routing's `send_email` only reaches verified destinations. To write
to whoever filled in the form (an auto-reply), use Cloudflare Email Sending
(beta, same `send_email` binding, `send({ from, to, bcc, replyTo, subject,
text, html })`). It needs **Workers Paid** for arbitrary recipients, the
sending domain on Cloudflare DNS, and the domain onboarded (Compute → Email
Service → Email Sending → Onboard Domain: MX/SPF/DKIM on `cf-bounce`, and a
DMARC record: keep the existing one). Send at most once per address (a KV
key with a TTL) and never echo the visitor's text in it.

The owner's apps (sign-up, password resets, receipts) moving off Resend or
MailerSend onto the same account: `transactional-email.md`.

## Email for the forms

Cloudflare Email Routing's `send_email` binding sends free to addresses
verified as destinations in the account. The sender must be on a domain
whose Email Routing is enabled. Check the domain's MX first:

| MX | What to do |
|---|---|
| none, or already `route*.mx.cloudflare.net` | Turn Email Routing on for the apex. Its MX + SPF + DKIM records are added and locked. |
| Google Workspace (`*.google.com`), Microsoft 365, Fastmail, etc. | **Don't** turn it on for the apex: it replaces the MX and SPF and stops the owner's mail. Instead: **(a)** Email Routing on a subdomain only (API `POST /zones/{id}/email/routing/dns` `{"name":"forms.example.com"}`, or dashboard → Email Routing → Settings → Subdomains), which adds MX + SPF on that name and touches nothing else; send from `forms@forms.example.com`. Or **(b)** send from another domain of the owner's whose Routing already runs. |

- **Recommend (a), and ask.** With (b), the form emails arrive from another
  of the owner's brands. Tell the owner the benefit of (a), that the emails
  come from their own name and are less likely to land in spam, and that
  their mailboxes aren't touched. Set it up only on a yes.
- **DMARC:** a `p=quarantine`/`reject` DMARC on the apex still passes for a
  subdomain sender with relaxed alignment (the default).
- **After the move:** offer to tighten a `p=none` DMARC once its reports
  are clean, and to retire SPF includes and DKIM selectors for services
  that no longer send. Explain the benefit and ask before each change (see
  SKILL.md's handback items).
- **Destination:** the owner's inbox must be a verified destination in the
  account (Email Routing → Destination addresses). Set it as the mailer's
  secret by piping it in, never printing it:
  `… | npx wrangler secret put FORMS_TO --config workers/forms-mail/wrangler.jsonc`.
- **Logs:** `npx wrangler tail --config workers/forms-mail/wrangler.jsonc`.
  Run it from the worker's config: in the Pages repo, plain `wrangler tail`
  picks up the Pages config and errors.
- **Proof of delivery:** a 204 from the mailer means Email Routing accepted
  the message. To prove delivery, have the owner look for the test subject
  in their inbox. A mailbox connected to the session, if any, may be a
  different account.

## Webflow side (the owner's clicks, after the switch is verified)

0. Export the form submissions first, because cancelling the plan loses
   them. Use `scripts/forms_to_kv.py export` (Data API, `forms:read`), or
   the Webflow MCP's `list_site_form_submissions`. Without either, use each
   form's CSV download in Site settings → Forms. Then import them into the
   site's KV store (SKILL.md step 5, "Bring the old entries over"), so the
   history lives with the new site. Keep the export outside the repo
   (people's details), skip the cookie-preference widgets Webflow counts as
   forms, and delete it once the counts match.
1. Site settings → Publishing → custom domains: remove the apex and www.
2. Cancel the site plan (Billing). The site stays on the free Starter plan
   at `<slug>.webflow.io`.
3. Downgrade the workspace plan only once the Code Export is saved; Code
   Export needs Core or higher.
