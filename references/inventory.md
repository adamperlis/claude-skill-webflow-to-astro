# Inventory: what to find, and what it means

Run `scripts/inventory.py`, then fill the gaps below. Write it all down in
the repo's `docs/move.md` as you go; it becomes the owner's handover.

## Pages

- **Sitemap pages:** these are the contract. Each keeps its URL, title,
  description, OG/Twitter, canonical and JSON-LD.
- **Pages the sitemap leaves out:** find them by diffing the Code Export's
  HTML files against the sitemap, then curl each one.
  - Carry over the ones that return 200 and are reachable: form success
    pages (`/success`, `/…-success`), utility pages linked from the site.
  - Leave out Ecommerce templates (`/checkout`, `/order-confirmation`,
    `/paypal-checkout`) when Ecommerce isn't used.
  - Leave out password-protected pages (401 / `/401`), plus Webflow
    template pages (`/template/style-guide`, `/licenses`, `/changelog`)
    unless linked.
- **Hidden sections:** sections with a `hidden` class aren't shown. Leave
  them out, unless a combo class in the CSS un-hides them.
- **404:** Webflow's has a canonical of `/404` and no description. Pages
  serves `dist/404.html` with a 404 status, and noindex is fine to add.

## Redirects, HSTS, domains

- **301s:** Webflow dashboard → Site settings → Publishing → 301 redirects
  (also exportable as CSV). They become `public/_redirects`.
- **HSTS:** "Enable HSTS for subdomains" there tells you whether
  `includeSubDomains` was on. Leave it off unless every subdomain is HTTPS.
- **Domains:** Webflow's custom domains list shows which host is the
  default (apex or www). Keep the same one canonical.
- **www:** often misconfigured on Webflow sites (a proxied www with no
  Webflow domain gives a 525). The move fixes it with a redirect rule.

## CMS

For each collection: its item count (published versus draft/archived), its
template page URL pattern, which pages list it, and whether something
outside writes into it.
- **"This is a field created for your Lever Connection"** (or Greenhouse,
  Ashby, Airtable, Whalesync) in the field help text means an integration
  syncs into the collection. Read from the source instead (see `cms.md`).
- **Zapier:** Webflow's API only lists webhooks your own token created, so
  zaps don't show. Ask the owner what each zap does: "Webflow: New Form
  Submission → …" and "… → Webflow: Create Item" are the common ones.

**Integrations that died quietly:** compare the CMS with its source. A job
sync can stop for years without anyone noticing: the job board says "no
openings" while the ATS has several. Reading the source directly fixes
that, and is worth telling the owner.

## Forms

- **Real forms:** list them, skipping Finsweet "Cookie Preferences" forms
  (one per page × domain in the API).
- **Per form, note:** its field names (keep them), redirect, success and
  error text, any `toolname`/`tooldescription` (WebMCP) attributes, and
  where the owner wants entries to go.
- **Webflow's spam checks don't survive the move:** its Turnstile sitekey
  and reCAPTCHA script were verified by Webflow's servers.

## Analytics and third parties

- **Verify each tag on live**, in the console and the network tab:
  - **Meta Pixel:** Webflow's integration often adds
    `fbq('consent','revoke')` and nothing grants it back, so the pixel
    loads but sends nothing.
  - **Copy-pasted snippets:** sometimes broken (made-up SRI hashes, a
    `window.x` never set). Say what you found, and ask before "fixing" what
    never worked.
  - **GTM containers:** carry the container over as is; its tags live in
    GTM, not the site. Check its triggers, though. Ones built on Webflow
    (form submission listeners, `.w-form-done` visibility, Webflow class
    names) need re-pointing at the new markup or a `dataLayer.push` from the
    new form script.
- **Cookie consent:** Finsweet `fs-cc` and similar need replacing if the
  site is in the EU or UK. Consent mode with GA4 (no analytics cookies in
  the EEA) avoids a banner. A setup that works:
  - **The existing property:** keep its GA4 property and stream, so the
    history carries on.
  - **Production only:** load the tag on the production hostname alone.
  - **Two consent defaults:** `analytics_storage: 'denied'` with
    `region` set to the EEA, UK and CH codes, then `'granted'` without a
    region for everywhere else.
  - **No ads:** `ad_storage`, `ad_user_data` and `ad_personalization`
    are denied everywhere.
  - **The result:** Google models EEA visits from cookieless pings, and
    there's no banner.
  - **The form:** a successful send fires the property's existing key
    event, so conversions continue.
  - **Opting out:** skip the tag entirely when the browser sends Global
    Privacy Control, or when the privacy page's switch is off.
- **Adobe Fonts / Typekit:** current web projects have no domain list
  ("embed this project on any website you manage"), so the kit works on
  pages.dev and the custom domain as is. Check it loads
  (`document.fonts` shows the families "loaded"); only a very old kit with
  an allowlist needs the new domains added.
- **Webflow site search (`/search`):** needs a replacement, e.g. Pagefind,
  built at build time.
- **WebMCP scripts** (`navigator.modelContext`): carry them over verbatim,
  with `toolname`/`tooldescription` on the `<form>` itself.

## Search, SEO and ownership: everything that has to move

The `seo-aeo-geo` skill owns the SEO/AEO/GEO side, at every step of the
move (SKILL.md, "seo-aeo-geo along the way"). It starts here: the baseline,
and an audit of the live site into `docs/seo.md`. Its
`references/audit-checklist.md` is the checklist for the rebuild. This list
covers only what has to *carry over* untouched.

Check each one on live and again on the rebuild:
- **Every page:** title, description, OG/Twitter (`scripts/parity.py`).
- **Canonical host:** apex versus www. Keep the same one canonical.
- **JSON-LD:** every block, with the Webflow CDN URLs swapped.
- **The site files:** favicons and the apple-touch icon, `robots.txt` (keep
  any per-bot rules exactly), `sitemap.xml`, and Webflow's 301s.
- **Search Console:** find out how it's verified, by a
  `google-site-verification` meta tag (keep it in the Layout) or a DNS TXT
  record (keep it in the zone). After the switch, resubmit the sitemap and
  watch Coverage for a week. Do the same in Bing Webmaster Tools.
- **Analytics:** GA4 directly or through GTM. Gate it to the production
  hostname so previews don't count.
- **Other ownership verifications:** Meta and Facebook domain
  verification, Pinterest, Apple Pay, Ahrefs. They're meta tags or TXT
  records; grep the live head and the TXT records.
- **hreflang and alternate links,** if the site is localised.

## Assets and bandwidth

- **Videos:** list the background videos, their sizes and pages. The
  Webflow bandwidth culprit is usually a modest video played on every visit
  of a busy page, or one in a hidden section that still downloads, not one
  giant file.
- **The 25 MiB cap:** files over it can't go on Pages. Re-encode them, drop
  a redundant WebM, or use R2 on a custom subdomain.
- **Fonts:** the Webflow CSS may load fonts it never renders. Check
  `document.fonts` on live for what's actually used.

## DNS and mail

- **Where DNS lives:** `dig NS` shows whether the zone is already on
  Cloudflare or at the registrar.
- **MX and SPF:** if the domain's mail is Google Workspace or Microsoft
  365, Email Routing must not take the apex. See `dns-and-email.md`.
- **Records to preserve:** every other host's (app., blog., status. and the
  like), DKIM, DMARC and verification TXTs.

## The machine

- **Disk space:** run `df -h` first. A mirror, a 100 MB+ export, node_modules
  and npx downloads (the Sanity CLI alone is about 1 GB) can fill a nearly
  full disk mid-run. With the owner's OK, clear caches that rebuild
  themselves (npm/npx and the like).
- **Chromium browsers can hold downloads:** Chrome, Brave or Edge may keep
  a downloaded ZIP as `Unconfirmed NNN.crdownload` until the user clicks
  Keep. Check its size matches, and ask them to keep it.

## Questions for the owner (ask once, together)

1. What is the site for, and what should a visitor do there (buy, book,
   donate, subscribe, get in touch)? This decides the conversions to keep
   counting (`site-types.md`).
2. May I download the Webflow export to ~/Downloads? (Give its name, source
   and size.)
3. Who edits content, and how often? This decides the CMS.
4. What do your Zapier zaps (or other integrations) do with this site?
5. Where should form entries go (which inbox), and from which sender domain?
6. GitHub: a private repo for this?
7. DNS: switch only after you've reviewed the pages.dev site. OK?
