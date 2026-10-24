---
name: webflow-to-astro
description: >
  Move a Webflow site off Webflow onto Astro + Tailwind, statically built and
  served by Cloudflare Pages, page for page: same URLs, titles, meta, OG,
  canonicals, JSON-LD, sitemap, robots, redirects and analytics, with forms,
  CMS content, video and the domain moved too, so the Webflow site plan can
  be cancelled. Use whenever someone wants to leave Webflow, cut Webflow
  costs, "export my Webflow site", rebuild a Webflow site in code, move a
  Webflow site to Cloudflare/Astro/static hosting, replace Webflow forms or
  CMS (with Astro content collections, Sanity or another headless CMS), or
  asks what breaks when you leave Webflow. Any kind of site: company or
  product sites, portfolios, shops (Webflow Ecommerce), restaurants and
  local businesses, nonprofits, publications, events, membership and
  multi-language sites. Also for Webflow-to-Next or other static stacks:
  the inventory, parity, forms, CMS and DNS steps are the same. With the
  seo-aeo-geo skill installed, the move also improves search and AI
  visibility.
---

# Webflow → Astro on Cloudflare Pages

A playbook for moving any Webflow site off Webflow: a company or product
site, a portfolio, a shop, a restaurant, a nonprofit, a publication. The
steps are the same for all of them. What the site is for changes the
details (`references/site-types.md`). It covers the whole move: inventory, backup, rebuild, forms,
CMS, video, parity checks, performance, deploy, domain switch, and what the
owner clicks at the end. Search and AI visibility improve at each step
along the way. The scripts in `scripts/` and templates in `templates/` are
the working parts; `references/` has the detail for each step.

The result: an Astro 7 + Tailwind 4 repo of its own, fully prerendered (only
gated pages, if any, render on request), on a Cloudflare Pages project
(never a Worker on workers.dev), forms through a Pages Function, content in
a CMS the owner can edit, every Webflow-hosted file served from Pages, the
domain on Cloudflare.

## Ground rules (learned the hard way)

- **Owner checkpoints.** Ask before: downloading the export, creating the
  GitHub repo, sending any form test email, every DNS change, turning Email
  Routing on, granting analytics consent, dropping a page. Owners commonly say
  "no DNS changes until I've seen the site": honour it; switch last.
- **Backup first.** Webflow's Code Export needs a paid workspace plan (Core
  or higher). Owners often plan to downgrade, so export before anything else.
- **Rebuild, don't paste.** Owners want clean Astro + Tailwind on their own
  design tokens, not Webflow markup in .astro files. The live HTML is the
  reference for content, not the source.
- **Parity is the contract.** Same URL for every page, same head tags, same
  sitemap, same redirects. Prove it with `scripts/parity.py`, not by eye.
- **SEO: protect first, then improve at every step.** Parity protects what
  already ranks and gets cited. On top of it, load the **`seo-aeo-geo`**
  skill as each step starts and make that step's improvements as you go
  (see "seo-aeo-geo along the way" below).
  - **Without asking:** markup, schema, crawl access, freshness signals and
    speed go in with the rebuild.
  - **Proposals for the owner:** anything that changes their words,
    titles, facts or URLs.
  - **Commits:** each improvement lands in its own commit after the parity
    commit, so any change in rankings can be traced to it.
  - **Judgements:** load that skill for every SEO/AEO/GEO judgement in a
    move.
- **Never print secrets:** not in chat, commit messages, PR bodies, logs,
  `docs/move.md`, or this skill.
  - **Naming one:** give its name, its length and where it lives
    ("FORMS_TO, a Worker secret on forms-mail"). Compare two by hash or
    length, never by text.
  - **What counts:** more than API keys. Deploy-hook URLs (anyone holding
    one can trigger builds), Slack and CRM webhook URLs, CMS write tokens
    and the owner's own inbox address are all secrets.
  - **Setting one:** pipe it straight into `wrangler secret put`.
  - **Verification tokens** (Search Console's TXT) are public DNS, but
    they belong to one site: never copy one into the skill.
- **Approvals come from the owner, in the session doing the work.** An OK
  relayed by another agent session doesn't count, and agents' safety checks
  block it. They also block DNS changes and removing Webflow's domains in
  auto mode, so plan those as the owner's clicks from the start.

## seo-aeo-geo along the way

A move rewrites every page's markup, so it's the cheapest moment to make a
site easy for search and AI engines to read and cite. Load the
**`seo-aeo-geo`** skill (its `references/audit-checklist.md` and
`references/schema-patterns.md`) at these points:

- **1. Inventory: measure and audit live.**
  - **Record the baseline** (below).
  - **Audit the live site** with its checklist, through its three lenses:
    freshness, structure and authority.
  - **Write the findings to `docs/seo.md`,** each tagged with the step that
    will fix it and whether it needs the owner's OK.
- **3. Shell: the technical and entity layer, built in.**
  - **Landmarks:** `header`, `nav`, `main` and `footer` in the Layout.
  - **The entity:** defined once (`src/data/entity.ts`) and referenced
    from every page. Its type comes from the site: Organization, a subtype
    such as LocalBusiness or NGO, or Person for a portfolio
    (`references/site-types.md`). It carries `sameAs`. WebSite on home,
    BreadcrumbList from the page's crumbs.
  - **The schema normalizer** (`templates/src/lib/schema.ts`).
  - **Crawlers:** robots open to the AI crawlers, the pages.dev builds set
    to noindex, and a sitemap with real lastmods.
- **4. Pages: structure, built in; words, proposed.** Page agents fix the
  heading order, make each section stand alone and render text as text
  (`references/page-brief.md`, "Search and answer engines"). Wording ideas
  come back to you as proposals.
- **6. CMS: freshness and item schema.**
  - **Dates:** `datePublished` and `dateModified` from the CMS.
  - **Posts:** Article/BlogPosting, with the author.
  - **Lists:** CollectionPage with an ItemList.
  - **Numbers:** anything the page shows is in the HTML at build time, not
    fetched in the browser.
- **7. Assets: speed and meaning.**
  - **LCP and lazy video:** a fast hero, with videos below the fold loaded
    lazily.
  - **Alt text** that says what the image shows.
  - **Video that carries content** (a demo, a talk) gets VideoObject.
- **8. Parity: the full audit, on pages.dev.** Re-run the checklist on the
  rebuild. Everything still open in `docs/seo.md` goes to the owner as one
  list of proposals.
- **9. Redirects: keep the equity.** Every redirect is a single hop, and
  every dropped or merged page goes to its nearest equivalent.
- **11. Switch: tell the engines.** Resubmit the sitemap in Search Console
  and Bing, turn on Crawler Hints (IndexNow), and watch coverage.
- **12. Hand back: measure, then look off-site.**
  - **Compare** against the baseline.
  - **Give the owner the skill's off-site plan:** the two or three channels
    AI engines cite most for this category. Most citations come from
    third-party sites, so the site alone can't win them.

`seo-aeo-geo` is a separate skill
([adamperlis/claude-skill-seo-aeo-geo](https://github.com/adamperlis/claude-skill-seo-aeo-geo)).
If it isn't installed, the move still works: make the improvements each
point above names from this skill's own notes (step 8's audit list,
`references/page-brief.md`, `references/site-types.md`), write the money
prompts yourself (the questions this site's audience asks an AI engine),
and tell the owner that the full audit and the off-site plan were skipped.

## The steps

### 1. Inventory (read-only, ~15 min)

Run `python3 -I scripts/inventory.py https://www.example.com > inventory.md`.
It reads the sitemap, robots, every page's head (title, description, OG,
canonical, JSON-LD types, noindex), CMS lists (`w-dyn-list`), forms,
third-party hosts, GA/GTM/Pixel IDs, background videos and their sizes, and
the apex/www/MX/NS records. Then, with the Webflow MCP tools if connected
(`data_sites_tool`, `data_cms_tool`, `data_forms_tool`, `data_webhook_tool`):

- **Collections:** list them and count the items in each (`list_collection_items` limit 1 → `pagination.total`).
- **Forms:** list them, ignoring Finsweet "Cookie Preferences" forms (one per page × domain).
- **Redirects and HSTS:** in the dashboard, Site settings → Publishing,
  export the 301 redirects as CSV and note "HSTS for subdomains".
- **Search and ownership:** how Search Console is verified (meta tag or DNS
  TXT), GA4/GTM (and any GTM triggers built on Webflow's markup), Bing, and
  other verification tags. The list is in `references/inventory.md`.
- **Domains:** the registrar, expiry, transfer lock, DNSSEC, and whether the
  domain was bought through Webflow (`references/domains.md`).
- **Pages off the sitemap:** Webflow serves pages the sitemap leaves out.
  Find them by diffing the export's HTML files against the live sitemap,
  then curl each one.
  - Success pages, such as a form's redirect target, need carrying over.
  - Leave out Ecommerce templates (/checkout, /order-confirmation) when
    the site doesn't sell, and password pages (401) when nothing is
    protected.
- **What kind of site it is:** what it's for, what a visitor should do
  there (buy, book, donate, subscribe, get in touch), and which Webflow
  features it leans on (Ecommerce, User Accounts, Localization, password
  pages, file uploads, RSS). `references/site-types.md` covers what each
  one changes: the entity's schema type, the conversions to keep counting,
  and the features that need their own plan.

Read `references/inventory.md` for what each finding means and the
questions to ask the owner (Zapier zaps, who edits content, analytics that
never worked).

**Record an SEO baseline before anything changes** (using the
`seo-aeo-geo` skill):
- **Search Console:** export Performance for the last 3 months (top pages
  and queries, plus AI Overviews impressions if shown) and the indexed-pages
  count.
- **Money prompts:** run its prompts in ChatGPT, Perplexity and Gemini,
  and note whether the site is cited. These are the questions this site's
  audience asks: shoppers, diners, donors, readers or clients.
  - **Run them from the audience's country.** AI engines answer by
    location, so a run made abroad isn't the audience's view. Use a VPN in
    their country if you have to.
  - **Record the location with the run,** and use the same one for the
    after half.

Keep it in `docs/move.md`. It's the before half of the comparison in
step 12. Then audit the live site with the same skill, into `docs/seo.md`
(see "seo-aeo-geo along the way").

### 2. Back up: export + mirror

- **Code Export** (Designer → ☰ → Export code → Prepare ZIP → Download).
  Ask the owner before downloading.
  - Unzip with `python3 -I scripts/unzip_webflow.py` (it repairs the
    non-UTF-8 file names that make `unzip` fail with "disk full?").
  - MISSING.txt lists videos that failed to export; the mirror fetches them
    from the CDN.
- **Mirror the live site:** `python3 -I scripts/mirror.py https://www.example.com reference/`
  saves each page's HTML to `reference/live/` and every file on Webflow's
  CDNs to `reference/assets/<kind>/`, with a manifest. Commit `reference/live/`
  (the record of what was live); git-ignore `reference/assets/`.
- **Screenshots:** `node scripts/shots.mjs https://www.example.com live`
  (desktop 1440 and phone 390). Webflow interactions hide elements until
  they scroll into view, so blank areas in full-page shots are usually
  unrevealed content: read the HTML.

### 3. Scaffold the shell (you, before any page work)

Copy `templates/` into the new repo (`templates/README.md` maps each file).
- **Config:** `astro.config.mjs` uses `build.format: 'file'` and
  `trailingSlash: 'never'`, because Webflow URLs have no trailing slash.
  The dev toolbar is off so screenshots match.
- **Tokens:** take them from the owner's design system if they have one;
  otherwise use the Webflow CSS `:root` variables and type scale.
- **Shared pieces:** Layout (head parity, analytics on the production
  hostname only), Nav, Footer, the CTA blocks pages share, the lazy
  `BgVideo`, and motion (reveals with a failsafe).
- **The search layer, from the start:**
  - **Landmarks** in the Layout.
  - **The entity, defined once** (`src/data/entity.ts`, with facts from
    the owner, not inferred from the old pages).
  - **The JSON-LD normalizer,** which every page's schema runs through.
  - **Crawlers and sitemap:** robots open to the AI crawlers, noindex on
    the pages.dev builds, and real lastmods in the sitemap.

  Pages built on this shell inherit all of it.
- **Measure first:** take live sizes with `scripts/measure.mjs` and build
  the shared pieces to them.

**Webflow behaviours to decide on:**
- **Page transitions:** many Webflow sites have a cover (`.transition` +
  `.transition-trigger` + a jQuery snippet that clicks the trigger on load
  and again on every internal link, then sets `window.location` after
  ~1s). Owners notice when it's gone and ask for it back. Rebuild it both
  ways in plain CSS + JS, off under reduced motion:
  - **Arriving:** the cover holds, then lifts away, with live's delays and
    easing (from the IX2 action lists in the export's `webflow.js`).
  - **Leaving:** a click on a same-site link (not `#`, not a new tab, not
    a modified click) brings the cover down over the page and only then
    navigates. Read the IX2 delays. A slide-in that waits 2s while the
    snippet leaves after 1s only ever shows a dead pause on live. Build
    what was meant (the cover down in about 0.8s), not the pause.
  - **Back:** on `pageshow` with `persisted`, put the cover away, or the
    page comes back from the history cache covered.
  - **Where it shows:** check the computed `display` on live at 375 and
    1440 (`scripts/measure.mjs`), not the CSS. A custom embed
    (`body .transition { display: block }`) can beat the site's own ≤767px
    `display: none`, so it shows on phones too.
- **Finsweet consent:** with Consent Mode v2, also push Finsweet's own
  dataLayer events (`<category>-activated`). GTM triggers built for
  Finsweet then keep firing.

**Two CSS traps that cost hours:**
- **Base size on body:** put Webflow's 10px base font size on `body`, never
  `html`. On `html`, 1rem becomes 10px and every Tailwind spacing and size
  renders at 62.5%.
- **No mixed breakpoints:** don't mix rem breakpoints (`md:`, `lg:`) with
  px ones (`min-[992px]:`) on the same property in one file; Tailwind 4 can
  order them wrongly. Use one kind per component.

### 4. Pages: in parallel, one agent per page group

Give each agent `references/page-brief.md` (fill in the repo path, port,
shared components, tokens) plus its page's route, head values and section
list from the inventory, with sections marked `hidden` skipped. Group small
pages together, give big ones their own agent, and keep the form pages and
the shared shell for yourself. Tell them:
- **Dev server:** one is already running; don't build, don't touch git.
- **New files:** after creating a new .astro file, run
  `touch src/styles/global.css`. Tailwind's dev server doesn't see classes
  in files created after it started.
- **Scratch files:** use their own unique scratch file names. Agents
  overwrite each other's `measure.mjs`.
- **Measure, don't eyeball:** compare positions with `scripts/measure.mjs`
  and screenshots with `scripts/shots.mjs`, desktop and phone.
- **Better structure, same words:** the brief's "Search and answer engines"
  section. They fix the heading order and the elements, and send any
  wording ideas back as SEO proposals for `docs/seo.md`.

When an agent reports a shared-file issue, fix it centrally and broadcast the
change to the others (with what to re-check).

**Generated data files become the source.** Page families extracted from the
live HTML (`src/data/<family>.ts`, "generated, don't edit") stop being
regenerated once the site moves: owner-approved copy and facts get edited
there. When you do, change the file's header to say so ("then edited:
…; re-running the script would undo that"), so nobody re-extracts over it.

**A Lottie hero with words in it.** Webflow heroes often write their headline
with a Lottie (`hero.json`, `hero-mobile.json`). Before touching one, read
its JSON: layer names, text layers (`t.d.k[0].s.t` and the font), and the
mask and position keyframes tell you the motion exactly (say, a line rising
out of a mask, letters sliding in and overshooting, small words fading up
0.15s apart).
- **Placing something over it** (a label above the words): the Lottie
  scales "meet" inside its box, so put the overlay in a box of the same
  size with `container-type: size` and compute the words' top from the
  viewBox ratio and where they start in the frame. Then check that it clears
  the nav on short laptop screens (1366×768) as well as at 1440.
- **Changing the words** means a new animation. Rebuild the motion in code
  rather than a new Lottie: the words become real, visible H1 text, sharp
  at any size, and editable in one line. It's a search win too: a headline
  drawn in a Lottie is invisible to crawlers and AI engines.

**Renaming nav links:** longer labels can run into a centred logo. Measure
the link row's right edge against the logo at 992, 1100, 1280 and 1440, on
the old nav and the new one. If the new one is worse, use short labels on
desktop and the full names in the phone menu.

### 5. Forms

Webflow forms stop working the moment the site leaves Webflow (its Turnstile
key and reCAPTCHA are verified by Webflow's servers). Use the templates:
- **The function:** `functions/api/forms.ts`, a Pages Function. One endpoint
  for every form, validated per form, with a honeypot and a minimum time on
  the form. Every entry goes to KV (`scripts/inbox.mjs` reads them).
- **The mailer:** `workers/forms-mail`, a Worker with no routes, no
  workers.dev address and no preview URLs. It's reached through a service
  binding (Pages Functions can't hold `send_email`) and emails the owner
  through Cloudflare Email Routing.
- **The client:** `forms.ts` posts with fetch and shows Webflow's thank-you
  and error panels, or follows `data-redirect`.
- **Keep Webflow's field names,** so entries match old exports.
- **Bring the old entries over.** Every past Webflow submission goes into
  the same KV store, so `npm run inbox` shows the site's whole history, not
  just what came in after the move. Use `scripts/forms_to_kv.py`:
  1. `export` pulls every form and submission through the Data API (a
     token with `forms:read`). Without a token, use `csv` with each form's
     CSV download from Site settings → Forms. Do this before the owner
     cancels the plan, because cancelling loses them.
  2. `map` lists each Webflow form with its count and a guessed `kind`.
     Match each kind to a key of `FORMS` in `functions/api/forms.ts`, and
     set cookie-preference widgets and test forms to `null`.
  3. `kv` writes the entries in exactly the shape the function stores, with
     the original date, `"source": "webflow"`, and keys built from
     Webflow's submission ids.
  4. Load them with `npx wrangler kv bulk put <file> --namespace-id <FORMS
     id> --remote`. This bypasses the function, so nobody is emailed,
     Slacked or added to the CRM for an old entry.
  5. Check the count per form against the map (`npx wrangler kv key list
     --prefix <kind>: …`), and read a few with `npm run inbox`.
  6. Run it again right before the domain switch to catch late
     submissions. The same keys overwrite, so nothing doubles.

  Every file holds people's details. The script refuses to write inside a
  git work tree. Delete the files once the counts match, and tell the owner
  how many came over per form.
- **Where entries go:** besides KV and email, the function can post to Slack
  (`SLACK_WEBHOOK_URL`) and a CRM (`CRM_WEBHOOK_URL`). Each is a secret,
  used only if set, and can never fail the form. That replaces Zapier zaps
  triggered by "Webflow: New Form Submission"; ask what each zap did, rebuild
  that directly, then turn the zap off.
- **Fill the destination the way the team uses it** (a CRM, a help desk,
  a mailing list, a spreadsheet):
  - **Copy a real record:** ask for a screenshot of one and map onto its
    fields (stage, status, source, dates, contact), not just a title and
    notes.
  - **Option ids:** read the custom fields and option ids from its API
    once, and keep them in a small table. Dropdowns take an option's id,
    not its name.
- **Confirm where the Slack webhook posts.** The channel is fixed when the
  webhook is made, and a test can land in a channel the team didn't
  expect. Ask the owner which channel before the test entry.
- **Route by what the entry is:** one contact form gets enquiries, support
  requests, applications, press and spam.
  - **When the team handles them differently,** add a first question
    ("What's this about?").
  - **Keep and email every entry,** but send each kind only where it
    belongs. A form's spec marks which entries go to Slack and the CRM
    (`lead`).
- **Forms that aren't messages:** newsletter signups, file uploads,
  bookings and donations each have their own route
  (`references/site-types.md`). An embed from the provider usually carries
  over as it is.
- **Spam: Turnstile, not reCAPTCHA** (free, no Google, usually invisible,
  managed mode). Its site key in the form, its secret as a Pages secret, and
  the function calls siteverify. The form must wait for the token before
  sending (an early send goes without it and is refused) and say plainly when
  Turnstile wants a tick. A browser driven by automation gets the tick box;
  don't click it, test with a preview deploy (which has no secret, so no
  check).
- **Test each outside call end to end from Cloudflare,** not from your
  machine: push a preview branch, post to its `/api/forms`, read
  `wrangler pages deployment tail <full deployment id>`, and look for the
  email the service sends. Ghost's members API (newsletter sign-ups)
  answered 406 to a Worker because a Worker's fetch sends no User-Agent;
  from a laptop it worked.
- **Don't count the wrong people as conversions:** if GTM fires an Ads
  conversion on the thank-you page, send only leads there; keep the others
  on the page with their own thank-you.
- **A visitor who isn't a lead shouldn't write to you:** when a contact
  form's first question sorts visitors ("buying or just browsing?"), the
  ones who aren't leads get what serves them (a page of resources and an
  in-place sign-up, just an email and "subscribe"), not a note box. Say
  exactly what they're joining, by the name its confirmation email uses
  ("<Name>, our free newsletter: …"). Hide and *disable* the
  other side's fields (disabled fields are neither validated nor sent). The
  function waits for the sign-up service and reports a failure, since
  there's no stored note to fall back on.
- **Per-form name and email:** each form names the fields that hold the
  person's name and email (`nameField`, `emailField`), since Webflow forms
  often end up with `name-2` and `Email-2`.

**Email Routing trap:** check the domain's MX first.
- **Google Workspace or another mail host:** turning Email Routing on for
  the apex replaces those MX and SPF records and breaks the owner's mail.
  Instead, send from a domain whose Email Routing is already on, or turn
  Email Routing on for a subdomain only (MX + SPF on, say, `forms.example.com`,
  nothing else touched).
- **Mail on Cloudflare already:** the apex is fine.
- **Any DNS change waits for the owner.**

**Test:** curl each form against a preview deploy with clearly marked test
data. Confirm the entry in KV and the mailer's 204 (`wrangler tail --config
workers/forms-mail/wrangler.jsonc`), then delete only the test entries.

### 6. CMS content

See `references/cms.md`. The short version:
- **Pull everything out first:** export each collection with
  `scripts/export_cms.py`, using the Webflow API via MCP or a token. Rich
  text, images, references, slugs and order all come along.
- **Few items, technical editors:** Astro content collections in the repo
  (Markdown/JSON + images), or Keystatic for a UI.
- **Non-technical editors, or Zapier/API writes:** Sanity (the free plan
  covers small sites). The site reads it at build time; a Sanity publish
  webhook triggers a Pages deploy hook to rebuild. Zapier has a Sanity
  integration, or uses the HTTP API.
- **Blog-style content:** the blogging platform the owner already uses
  (Ghost, WordPress, Substack), or one of the options above.
- **Search signals from the CMS** (`seo-aeo-geo`'s freshness and schema
  layers):
  - **Dates:** `datePublished` and `dateModified` come from the CMS's own
    timestamps, and the sitemap's lastmod from the same.
  - **Posts:** Article/BlogPosting with a real author.
  - **List pages:** CollectionPage with an ItemList.
  - **Real changes only:** a date moves when the content changes, not on
    every import.
- **Data from another system** (products from a store, events from a
  ticketing platform, listings from a feed, jobs from an ATS like Lever,
  Ashby or Greenhouse): don't copy it into a CMS. Read the source API at build time,
  plus a daily rebuild: `templates/workers/rebuild-cron`, a Cron Trigger
  that POSTs to the Pages deploy hook. It keeps the schedule in Cloudflare
  with the site, where a GitHub Actions schedule needs a repo secret and is
  switched off in a public repo after 60 days without commits.
- **Collection template pages** (`/blog/[slug]`, `/products/[slug]`,
  `/events/[slug]`) become `getStaticPaths` pages at the same URLs.
- **Numbers the CMS publishes** (prices, rates, salary ranges): check every
  one on import. Common slips:
  - a range entered backwards;
  - tiers that contradict each other (a cheaper tier costing more);
  - several items sharing one copied value.
  - **A refresh:** research it with sources. The new figures go to the owner
    as a before-and-after table, because they're published as the company's
    numbers. Write them to the CMS only after the owner says yes.
  - **Writing to Sanity from a script:** `npx sanity exec <script>
    --with-user-token`, with the script inside `studio/`. A script elsewhere
    can't resolve `sanity/cli`. Delete it afterwards.
  - **Don't show "Updated <month>"** until the figures really change.
    `_updatedAt` moves on any import or typo fix.
- **A feed that overwrites itself monthly** (an index or report the page
  shows): past editions disappear from the site, along with what they
  ranked for. They're usually in the producing
  repo's git history: `gh api "repos/<o>/<r>/commits?path=<file>"`, then
  `contents/<file>?ref=<sha>`. Seed a page per edition from that, then
  archive each new month as it comes.

### 7. Video and assets

- **Off Webflow's CDN:** every file (images, videos, fonts, Lottie JSON)
  moves to Pages. Nothing may load from `cdn.prod.website-files.com`,
  `uploads-ssl.webflow.com`, `assets.website-files.com` or
  `d3e54v103j8qbb.cloudfront.net`.
- **The 25 MiB cap:** Pages refuses files over 25 MiB. Webflow background
  videos list MP4 first, so browsers play the MP4: drop an oversized WebM
  rather than re-encode it.
- **"The big video" is often a small file played on every visit,** or one
  hidden in a `display:none` section that still downloads. Find the
  bandwidth culprit before deciding R2 versus Pages; Pages bandwidth is free.
- **Compress at the same look:** `scripts/compress_video.sh in.mp4` tries
  x264 CRF 26 and 28 and reports size and SSIM. Keep the version with
  SSIM ≥ 0.985.
- **`BgVideo` loads lazily** (preload none, plays near the viewport, pauses
  off it, poster under reduced motion). Pass `eager` only for a hero.
- **Rasters** go through `astro:assets` `<Image>`, from the largest
  original, not Webflow's `-p-500` variants.
- **Images and video for search:**
  - **Alt text** says what the image shows. Webflow sites often have
    empty or file-name alts.
  - **The hero** is the LCP element, so keep it fast: an eager poster, no
    reveal.
  - **A video that carries content** (a demo, a talk, a case film) gets
    VideoObject schema with a thumbnail and its length.

### 8. Parity, accessibility, performance

- `python3 -I scripts/parity.py reference/live dist` diffs every page's head
  (title, description, OG/Twitter, canonical, robots, JSON-LD types) and
  checks that every internal link and asset resolves, no Webflow host is
  referenced, and no file exceeds 25 MiB.
  - Expect one fix: with `format: 'file'`, home's path is `/index`, so the
    canonical must strip it.
- **User agents:** Cloudflare blocks Python's default user agent with a 403,
  so give every checking script its own UA (the skill's scripts do). Check
  status codes with curl before trusting a surprise.
- **Lighthouse:** run it in a clean headless Chrome
  (`scripts/lighthouse.sh https://<project>.pages.dev /about …`). Browser
  extensions inflate TBT and fail Best Practices. Usual fixes:
  - **LCP:** don't put a reveal on the LCP heading.
  - **Videos:** lazy-load any video below the fold.
  - **Contrast:** use a dark backdrop under hero videos (Lighthouse measures
    text against the section's background) and darker variants of light
    accent colours for small text.
  - **Headers:** add COOP `same-origin`.
  - Add `includeSubDomains` to HSTS only if every subdomain serves HTTPS.
- **Visual check:** shoot the deploy against live at 1440, 390 and one wide
  width (2000). At the wide width, check that hero content aligns with the
  nav's container.
- **SEO/AEO/GEO audit:** once parity passes, load the **`seo-aeo-geo`**
  skill and run its full audit (`references/audit-checklist.md`) on the
  pages.dev build. Most of it should already pass, since the shell and the
  pages built it in. What's left joins `docs/seo.md`.
  - **Crawl access:** robots must not block GPTBot, OAI-SearchBot,
    ClaudeBot or PerplexityBot. Keep the owner's own rules otherwise, and
    flag blocks that look accidental.
  - **Rendering:** content is server-rendered; Astro's static output
    passes.
  - **Canonicals and redirects:** single-hop redirects, real 404s.
  - **Schema** (its `references/schema-patterns.md`): the site's entity
    with `sameAs` on every page, WebSite on home, BreadcrumbList,
    `dateModified` from the CMS's updated time, and each page's own type
    (Product, Event, Article, Menu…; `references/site-types.md`).
  - **Extractability:** clear H2/H3 sections, an answer in the first lines.

  **What Webflow sites reliably get wrong** (check for every one):
  - **One organization, many nodes:** each page's hand-written JSON-LD
    declares its own copy of the Organization, often dozens across the
    site, with descriptions that disagree. Don't fix the generated page
    data. Define the entity once (`src/data/entity.ts`) and run each page's
    JSON-LD through a normalizer in Layout (`templates/src/lib/schema.ts`):
    - each copy becomes `{ "@id": ORG }`;
    - `serviceType` moves to a Service;
    - relative URLs become absolute;
    - a page's own WebPage merges into the base one;
    - hand-written FAQPage nodes are dropped.
  - **FAQ schema that doesn't match the page:** rebuild FAQPage from the
    items the page renders (Layout `faq` prop), never from copied schema.
  - **Data loaded in the browser** (a JSON feed the page fetches for its
    numbers or charts): crawlers and AI bots without JS see "Loading…". Fetch at build
    time, render the numbers into the HTML, hand the same object to the
    charts inline, and add Dataset schema. The daily rebuild keeps it fresh.
  - **The pages.dev builds are indexable:** add to `public/_headers`
    `https://:project.pages.dev/*` and `https://:version.:project.pages.dev/*`
    with `X-Robots-Tag: noindex` (they never match the custom domain).
  - **Frozen lastmods:** Webflow's sitemap dates never move. Take CMS
    `_updatedAt`, the newest ATS posting and a feed's own date instead.
    - **Pages kept in the repo:** use the newest commit that touches the
      page's own files (`git log -1 --format=%cI -- <the page, its
      write-up, its images>`), not the build time. A shared component
      changing shouldn't move every page's date.
    - **Building from `git archive`:** the archive has no history, so set
      `GIT_DIR` to the repo's `.git`, or the dates vanish. With no history,
      leave lastmod out rather than invent one.
  - **llms.txt in robots syntax:** rewrite it as Markdown (H1, summary,
    annotated links), with the owner's facts.
  - **Facts that conflict across pages** (opening hours, prices, team size,
    founding year, contact email): ask the owner for each one, then make
    every page agree.
  - **Giant decorative H1s** (a slogan like "Hello." or "Eat well", or a
    product name alone with what it is in a small eyebrow): keep the look
    and add the missing words inside the H1 as visually hidden text ("Eat
    well: a bakery in <City>"), with the eyebrow `aria-hidden` if it says
    the same thing.
  - **Source captions:** check a chart's "Source:" against the code that
    makes the data. A caption can credit one source while the pipeline
    uses another.
  - **Near-copies that Google skips:** location, service or product-variant
    pages cloned from one template, nearly word for word the same as a
    sibling, with nothing linking to them.
    - **Check Search Console's verdict** for each page.
    - **Then give each one its own section and links in from the site,**
      and fix any untidy slug.
    - **Timing:** Google judges them again only once the domain has moved.

  **A positioning shift** (the owner wants new words for what they do, often
  decided during the move):
  - **Research the words first,** in the owner's browser, read-only:
    - Google Trends (the audience's country, 5 years) for the direction
      of each term;
    - Keyword Planner for volume and competition. A cancelled Ads account
      still opens it but shows only ranges, and a search saves a draft plan
      in the account; tell the owner so they can delete it.
  - **Watch for ambiguous terms:** a new term may be searched mostly in
    another sense, from another field. Check Trends' related queries and
    ask the AI engines what it means. If they read it the other way, always
    pair it with a definition, and give the term a guide page of its own.
  - **Change labels, titles and copy, not URLs:** the URLs hold the
    rankings. For the new words, add short alias URLs that 301 to the
    existing pages (`/new-term` → `/old-term`).
  - **Merge overlapping pages** with 301s to the strongest page, then delete
    the merged pages' files and remove them from the sitemap and every
    internal link.

  Report the findings as proposals and apply them only with the owner's
  OK, in separate commits after the parity commit, so ranking changes can
  be traced. Respect its "what not to do" list: don't add `llms.txt` (carry
  over one that exists), and don't chunk or rewrite content for AI.

### 9. Redirects

`references/redirects.md` covers all five layers:
- **Edge:** http→https and www→apex.
- **Preview host:** pages.dev → the domain.
- **Paths:** Webflow's 301s, plus dropped pages and changed slugs.
- **Trailing slashes.**

Convert Webflow's CSV export with `scripts/redirects.py from-csv`, map
every dropped page to its nearest equivalent, and before the switch run
`scripts/redirects.py check public/_redirects https://<project>.pages.dev`.
It checks each rule's status and target and flags chains. For search, every
redirect is one hop to the closest page, never to home by default: a
redirect to an unrelated page is treated as a soft 404, and the old URL's
standing is lost.

### 10. Deploy

- **Git-connected or direct upload? Decide before creating the project:**
  a direct-upload project can never be connected to Git later, and only a
  Git-connected one has deploy hooks.
  - **The site has a CMS or reads another system at build time** (anything
    that changes without a commit): Git-connected. Push the repo first;
    then dashboard → Workers & Pages → Create → the small **"Looking to
    deploy Pages? Get started"** link at the bottom → Import an existing
    Git repository. (The big "Import a repository" makes a *Worker* with
    Workers Builds: its log ends `npx wrangler deploy`. Delete it and start
    again.) Install the Cloudflare Pages GitHub app on that one repo; preset Astro, build `npm run build`, output `dist`, env
    `NODE_VERSION` = the `.nvmrc` version. Before that, build a fresh clone
    (`git clone --depth 1 file://$PWD /tmp/x && cd /tmp/x && npm ci && npm
    run build`): the builder has none of the git-ignored `reference/`.
    The build log should say it read `wrangler.jsonc` (its bindings).
    Every push to `main` then deploys; `npm run deploy` still works for a
    one-off. Then the deploy hook, the CMS webhook and the daily rebuild
    (`references/cms.md`).
  - **Moving from direct upload to Git:** the new project
    gets a new pages.dev address. Once it builds, the owner deletes the old
    project. Stop deploying by hand, and update every doc, check script and
    note that named the old address.
  - **Everything is in the repo:** direct upload is simpler.
- **Create a direct-upload project:** `wrangler pages project create <name> --production-branch main`.
- **Deploy with `--force`:** `wrangler pages deploy --project-name <name>
  --branch main --commit-dirty=true --force`. Newer wranglers otherwise try
  the Workers-based Pages and land the site on the shared workers.dev
  subdomain.
- **Deploy a commit, not the working tree,** when other agents share the
  checkout:
  1. `git archive <sha> | tar -x -C /tmp/site-<sha>`.
  2. Symlink `node_modules` in, and build there, with
     `GIT_DIR=<repo>/.git` for anything the build reads from git (the
     sitemap's dates).
  3. Deploy with `--commit-hash <sha>`.

  Their uncommitted work never ships, and the deploy names exactly what's
  live. Before deploying, `git log <last deployed sha>..HEAD`, so you know
  what else goes out with yours.
- **Verify on the deploy's own address first** (`<hash>.<project>.pages.dev`).
  The custom domain can keep serving the previous deploy for a few seconds
  after "Deployment complete", so a check that runs at once can fail for
  no reason.
- **The share image:** a move usually changes it, since Webflow's lived on
  its CDN.
  - **Version its URL** (`/og.jpg?v=2`) and bump it with every new card. X
    and LinkedIn cache the image by its URL.
  - **Refresh a link already shared:** LinkedIn's Post Inspector re-fetches
    it.
  - **Check it at feed size,** about 500 px wide, where most people see it.
- **Preview branches** (`--branch forms-test`) are for form tests.
- **Bindings** (KV, services) go in `wrangler.jsonc` with `pages_build_output_dir`.
- **Commit by path,** after `git status --short | grep -E '(^|/)\.env'` comes
  back empty. Push to a private repo once the owner agrees.

### 11. Domain switch (after the owner has reviewed the pages.dev site)

See `references/domains.md` (nameserver moves and registrar transfers) and
`references/dns-and-email.md` (records, Pages custom domains, email).
- **Moving DNS:** if the zone isn't on Cloudflare (registrar DNS, e.g.
  Porkbun), add the zone to Cloudflare first. Copy every record, especially
  MX, TXT/SPF, DKIM and DMARC, and verify with dig before switching
  nameservers.
- **Custom domains:** add the apex and www to the Pages project. Replace
  only the Webflow records: the apex A `198.202.211.1` or CNAME to
  `proxy-ssl.webflow.com`, and www to `cdn.webflow.com`.
- **www redirect:** a Redirect Rule, 301, keeping the path and query.
- **Leave every other record alone:** app subdomains, the blog, MX and TXT.
  - **Verification TXTs:** Search Console's domain property and Bing stay
    verified through the switch only if their TXTs move with the zone.
- **The nameserver click:** in an automated browser, a registrar's save
  can hang behind a native confirm dialog (Porkbun's does). Reload, save
  again, and check that the editor lists the Cloudflare pair (usually the
  same pair as the account's other zones). Then `dig NS`.
- **Cloudflare's Email Address Obfuscation** (on by default on new zones)
  rewrites anything shaped like an address, and adds a
  `/cdn-cgi/l/email-protection` script. Package versions in code samples
  (`three@0.160.0`) and handles with dots after the @ become
  "[email protected]".
  - **Fix:** turn it off for the zone, or wrap the page in
    `<!--email_off-->` … `<!--/email_off-->` (Astro keeps HTML comments in
    its output).
- **Verify live:** every page returns 200 with the right canonical, the
  redirects are 301, the forms send, and the certificates are active.
- **Crawl the live site** after the switch: every page, and every internal
  link and asset in it. Search the HTML for "[email" too.
  - **Media:** use HEAD; GET on videos times out.
  - **Concurrency:** keep it to about 6 at a time, with retries. Dozens at
    once get "fetch failed" from Cloudflare.
- **Tell the engines** (`seo-aeo-geo`):
  - **Search Console and Bing:** resubmit the sitemap the same day.
  - **Submit this host's own sitemap:** a domain property can list other
    subdomains' sitemaps (an app, a blog) and never this site's.
    URL Inspection's "No referring sitemaps detected" is the sign.
  - **Run the live test** on the home page (URL Inspection → Test live
    URL). "Page can be indexed" from Google's own fetch proves its bot gets
    through Cloudflare. Its fetched HTML shows which build it got: look for
    the new framework's asset paths (`/_astro/`).
  - **Request indexing** for the home page and the top pages
    (`references/dns-and-email.md` has the pace).
  - **Expect an old crawl date for a few days:** the last crawl predates the
    switch, and that's normal.
  - **Read the counts by host:** a domain property's indexed and
    not-indexed totals cover every subdomain. A busy app on a subdomain can
    swamp the site's own numbers, so inspect the site's URLs themselves.
  - **Crawler Hints:** turn it on, so IndexNow engines hear about changes
    as they happen. It needs the owner to accept its terms.
  - **Watch:** pages and coverage, daily for the first week.

### 12. Hand back

Tell the owner exactly what's left for them to click, and write
`docs/move.md` in the repo: how it's set up, what was carried over or
dropped and why, and the forms, CMS, analytics and DNS details. Their clicks:
- **Webflow:** remove the custom domains (Site settings → Publishing), then
  cancel the site plan. Downgrade the workspace plan only after the export
  is safe.
- **Analytics:** any decisions you deferred, such as granting Meta Pixel
  consent or fixing tags that never worked.
- **Search Console and Bing:** resubmit the sitemap, and watch Pages and
  Coverage for new 404s for a week.
- **Measure against the baseline** 2–4 weeks after the switch, with the
  `seo-aeo-geo` skill's measurement section: Search Console clicks,
  impressions and AI Overviews for the same pages and queries, and the same
  money prompts in ChatGPT, Perplexity and Gemini, from the same country.
  Report what moved and why.
- **The off-site plan:** from the `seo-aeo-geo` skill. Most AI citations
  come from other sites, so name the two or three channels the engines cite
  most for this category, with the format for each and why. The site move
  can't do this part; the owner has to.
- **`docs/seo.md`:** what was improved during the move, what's still
  proposed, and when to re-measure.
- **The domain:** optionally transfer it to Cloudflare Registrar
  (at cost), especially if it was bought through Webflow. See
  `references/domains.md`.
- **Zapier:** repoint zaps to the new Catch Hook.
- **A privacy page that matches the new stack.** The Webflow one, if any,
  names Webflow as the host.
  - **What it lists:** Cloudflare hosting, where form entries are stored
    and mailed, analytics and how consent works, third-party embeds, and
    the browser storage keys the site sets.
  - **Its contact address:** one that forwards through Email Routing
    (`privacy@`), so the owner's own inbox stays off the page.
  - **An analytics switch:** a localStorage flag on the page, which the
    layout checks before loading the tag, along with Global Privacy
    Control.
  - **An Impressum** only if the owner runs the site from Germany. Ask.
- **DMARC:** if the domain has none, Cloudflare's DMARC Management adds a
  `p=none` monitoring record, with reports to Cloudflare. It's a DNS change,
  so it's the owner's click.
- **Tighten DMARC later.** `p=none` only reports. Once two to four weeks
  of Cloudflare's DMARC reports show only the owner's own senders passing,
  suggest `p=quarantine`, and later `reject`. It's the owner's click; put
  the date to look again in `docs/move.md`.
- **Retire senders that are gone.** List every `include:` in the apex SPF
  and every DKIM selector (`dig TXT`). Ask the owner which services still
  send mail as the domain: their mail host, a newsletter tool, a CRM,
  Webflow's own form mail. Remove only the ones they confirm are gone.
  - **Why it matters:** each dead include uses one of SPF's 10 DNS lookups.
    An old account still allowed to send is also a way to spoof the
    domain.
  - **Never guess:** removing a sender that's still in use breaks that
    service's mail.
- **Webflow billing:** plans bill yearly.
  - **Site plans** downgrade at the end of the term.
  - **Unused months of a workspace plan:** ask support, through the chat
    in the dashboard. Its bot hands a request for a goodwill prorated
    refund to a person, and the reply comes by email.
  - **Core** matters only for Code Export, and only while other sites in
    the workspace still need it.

## Files

- `scripts/`:
  - `inventory.py`, `unzip_webflow.py`, `mirror.py`, `export_cms.py`
  - `shots.mjs`, `measure.mjs`, `parity.py`, `redirects.py`, `compress_video.sh`, `lighthouse.sh`
- `templates/` (`README.md` maps them): Astro config, global.css skeleton,
  Layout, BgVideo, forms (function, mailer Worker, client), wrangler
  configs, `_headers`, `_redirects`, sitemap endpoint, inbox script,
  AGENTS.md, and `studio/scripts/build-import.mjs` (Webflow CMS JSON → Sanity).
- `references/`: `inventory.md`, `site-types.md`, `page-brief.md`, `cms.md`,
  `redirects.md`, `domains.md`, `dns-and-email.md`.
