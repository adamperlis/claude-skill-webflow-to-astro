# Domains: nameservers and registrar transfers

Two separate moves, often confused:

- **DNS hosting** (nameservers) decides who answers for the zone. The site
  needs this on Cloudflare, or at least the apex and www records pointed
  at Pages.
- **Registration** (the registrar) decides who you pay each year. It's
  optional, and done after the site is live. Cloudflare Registrar sells at
  cost, with no markup and free WHOIS privacy.

Do them in that order, one at a time. Never move DNS and transfer the
registration on the same day.

## 1. Find out where things are

- `whois example.com | grep -iE 'registrar:|expir|status'`: the registrar,
  the expiry date, and any `clientTransferProhibited` lock.
- `dig +short NS example.com`: who hosts DNS. For `*.ns.cloudflare.com`
  it's already done; a registrar's own nameservers (Porkbun, GoDaddy,
  Namecheap, Squarespace) mean step 2.
- **A domain bought through Webflow** is registered with Webflow's partner,
  Name.com (Webflow → Workspace → Domains). Once the site moves off Webflow
  it's worth transferring out (step 3). Webflow gives the auth code under
  the domain's settings.
- `dig +short DS example.com`: DNSSEC. If records come back, it must be
  turned off at the registrar before nameservers change, and re-enabled on
  Cloudflare afterwards. A mismatch takes the domain offline.

## 2. Move DNS hosting to Cloudflare (needed for Pages custom domains on the apex)

1. **Add the domain:** Cloudflare dashboard → Add a domain → Free plan. It
   scans and imports the existing records.
2. **Check every imported record** against `dig` on the old nameservers,
   especially MX, the SPF/DKIM/DMARC TXTs, verification TXTs and every
   subdomain (app., blog., status., mail tracking hosts).
   - Add anything missing. A scan misses records it can't guess: DKIM
     selectors, `_dmarc`, odd subdomains.
   - Keep mail and third-party records DNS-only (grey cloud).
3. **Lower TTLs** at the old host a day ahead, if you can.
4. **Switch the nameservers** at the registrar to the two Cloudflare gives.
   That's the owner's click in the registrar's dashboard.
5. **Wait for "Active"** (minutes to a few hours), then do the Pages custom
   domains and redirects (`dns-and-email.md`, `redirects.md`).
6. **Turn DNSSEC back on** in Cloudflare and add the DS record it gives at
   the registrar.

Mail keeps flowing throughout, as long as the MX/TXT records were copied
exactly. Check after the switch with `dig MX` and by sending a test email
to the domain.

## 3. Transfer the registration to Cloudflare Registrar (optional, later)

**Prerequisites:**
- The zone is already active on Cloudflare (step 2).
- The domain is more than 60 days past registration or its last transfer
  (an ICANN rule).
- It isn't expired or in redemption.
- The TLD is one Cloudflare supports (most gTLDs and many ccTLDs; `.ai` is
  supported, but check the list).

**Steps:**
1. **At the old registrar:** remove the transfer lock, turn off any
   domain-privacy "auto-renew lock" add-ons, and get the **auth / EPP
   code**.
2. **In Cloudflare:** Domain Registration → Transfer Domains → select the
   domain → enter the auth code → confirm the contact details → pay for
   one year. The year is added to the current expiry; nothing is lost.
3. **Approve at the old registrar:** many email a confirmation, so the
   owner clicks approve to finish in minutes. Otherwise it completes by
   itself in up to 5 days.
4. **After the transfer:** auto-renew is on by default in Cloudflare.
   Check the expiry date and the contacts, then cancel any renewal
   subscription left at the old registrar (Webflow's domain plan, for
   example).

The site doesn't go down during a registrar transfer: the nameservers
don't change. Tell the owner the cost (one year at Cloudflare's at-cost
price) and the timing before starting. Every step that pays or approves is
theirs.

## Webflow-specific cleanup (the owner's clicks)

1. **Remove the custom domains:** Site settings → Publishing. Do this only
   after Cloudflare serves the site, or Webflow may keep issuing its own
   certificate for the hostname.
2. **Cancel the site plan:** the site falls back to `<slug>.webflow.io`,
   which you can keep as an archive or delete.
3. **A domain bought through Webflow:** transfer it out (step 3) before
   cancelling anything that bills for it.
4. **The workspace plan:** downgrade it last, after the Code Export is
   safely saved (Code Export needs Core or higher).
