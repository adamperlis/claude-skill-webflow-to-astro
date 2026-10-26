# webflow-to-astro-cloudflare — a Claude skill for leaving Webflow

A [Claude Code](https://claude.com/claude-code) skill that moves a Webflow site to **Astro +
Tailwind**, statically built and served by **Cloudflare Pages**, page for page: the same URLs,
titles, meta, Open Graph, canonicals, JSON-LD, sitemap, robots and redirects, with the forms,
CMS content, video, DNS and email moved too, so the Webflow site plan can be cancelled.

It was built while moving real sites off Webflow (company sites with several forms, a CMS,
video heroes and page transitions), and it carries what those moves taught: the traps that
cost hours, the order that keeps mail and rankings intact, and the clicks that have to stay
with the owner.

## What it does

The skill runs the move in twelve steps, with a script or template for each working part:

1. **Inventory** the live site: every page's head, CMS lists, forms, analytics IDs, videos
   and their sizes, DNS and mail records.
2. **Back up**: unzip the Code Export (repairing Webflow's broken file names), mirror the
   live HTML and every CDN file, take desktop and phone screenshots.
3. **Scaffold** an Astro 7 + Tailwind 4 repo from the templates: head parity, a single
   site entity in JSON-LD, analytics on the live host only, lazy background video.
4. **Rebuild the pages** in parallel, one subagent per page group, measured against live
   rather than eyeballed.
5. **Forms**: one Pages Function for every form (honeypot, time check, KV storage), email
   through Cloudflare Email Routing, optional Slack and CRM webhooks. Every past Webflow
   submission is exported and imported into the same store, with its original date, so the
   history moves with the site.
6. **CMS**: export every collection, then Astro content collections, Keystatic or Sanity,
   depending on who edits it.
7. **Assets**: everything off Webflow's CDN, videos under Pages' 25 MiB cap.
8. **Parity**: a script diffs every page's head against the original and checks every
   link and asset; then accessibility and Lighthouse.
9. **Redirects**: Webflow's 301 export converted to `_redirects`, and checked for chains.
10. **Deploy** to Cloudflare Pages (Git-connected when there's a CMS).
11. **Switch the domain**: zone, records and email moved without breaking mail.
12. **Hand back**: what's left for the owner to click, written up in the repo.

Search and AI visibility improve along the way: the rebuild fixes heading order, schema,
crawler access and lastmods, and anything that would change the owner's words comes back
as a proposal instead.

## Install

**Easiest — as a plugin, right inside Claude Code:**

```
/plugin marketplace add adamperlis/claude-skill-webflow-to-astro
/plugin install webflow-to-astro@webflow-to-astro
```

Then start a new session. To pull future improvements:
`claude plugin update webflow-to-astro@webflow-to-astro`.

**Alternative — clone into your skills folder (plain git, updatable with `git pull`):**

```bash
git clone https://github.com/adamperlis/claude-skill-webflow-to-astro ~/.claude/skills/webflow-to-astro
```

Either way, the skill triggers when you talk about leaving Webflow, or invoke it with
`/webflow-to-astro`.

## Use

```
/webflow-to-astro move https://www.example.com off Webflow
```

It starts read-only (the inventory) and asks before anything that downloads, creates a
repo, sends an email or touches DNS.

## What you need

- **Claude Code.**
- **The Webflow site,** with dashboard access. Code Export needs a paid Webflow workspace
  plan (Core or higher), so export before downgrading anything.
- **A Cloudflare account.** The free plan covers Pages, DNS, KV and Email Routing.
  Auto-replies to visitors need Workers Paid.
- **Node 22.22+ and npm.** The templates install Astro, Tailwind, wrangler and
  playwright-core; Lighthouse runs through `npx`.
- **Python 3.9+.** The Python scripts use the standard library only.
- **Google Chrome,** or Playwright's Chromium (`npx playwright install chromium`), for
  screenshots, measurements and Lighthouse.
- **ffmpeg and ffprobe** (with libx264), to compress background videos.
- **`dig`, `whois` and `curl`,** for the DNS and redirect checks (preinstalled on macOS;
  `dnsutils` or `bind-utils` on Linux). The two shell scripts need `bash`.
- **git and a GitHub account,** for a Git-connected Pages project.

Optional:

- **The [Webflow MCP server](https://developers.webflow.com/mcp/reference/overview),** for collections, forms
  and form submissions. Without it, `scripts/export_cms.py` and `scripts/forms_to_kv.py` use
  a Webflow API token with `cms:read` and `forms:read`. With no token at all, form submissions
  come from each form's CSV download in the dashboard.
- **A Sanity account,** if the CMS moves to Sanity.
- **The `gh` CLI,** for recovering past editions of a data feed from git history.
- **The [`seo-aeo-geo`](https://github.com/adamperlis/claude-skill-seo-aeo-geo) skill,** for
  the full SEO/AEO/GEO audit, the before-and-after baseline and the off-site plan. The move
  works without it.

The scripts make requests only to the site you point them at (and whatever its pages load
in the browser), Webflow's CDN and API, Cloudflare (through wrangler) and npm (for `npx`).
They send no telemetry.

## What it doesn't do

- **It rebuilds; it doesn't convert.** Claude rewrites each page as clean Astro +
  Tailwind, using the live HTML as the reference. That takes real time and tokens on a big
  site, and someone should look at the result before the domain moves.
- **It doesn't make the owner's clicks.** DNS changes, the nameserver switch, removing
  Webflow's domains, cancelling plans and accepting terms are listed for the owner, not
  done for them.
- **Webflow Ecommerce, User Accounts, Logic, Optimize and Analyze don't move as they
  are.** The skill plans a replacement for each (Stripe, Shopify, Memberstack, Cloudflare
  Access and the like); setting those up is still work.
- **Interactions are rebuilt, not exported.** Reveals and page transitions become plain
  CSS and JS, timed from Webflow's own settings.
- **It targets Cloudflare Pages.** The inventory, parity and redirect scripts work for any
  static host, but the forms function, mailer and headers are Cloudflare's.
- **Tested on macOS.** Linux should work; Windows hasn't been tried.

## Files

| File | What it is |
|---|---|
| `SKILL.md` | The skill itself: ground rules, the twelve steps, and the SEO work along the way |
| `references/inventory.md` | What to find on the live site, what it means, and the questions for the owner |
| `references/site-types.md` | What changes by kind of site: schema type, conversions, Webflow features that need a plan |
| `references/page-brief.md` | The brief each page-building subagent gets |
| `references/cms.md` | Replacing Webflow's CMS: content collections, Keystatic, Sanity from zero |
| `references/redirects.md` | The five redirect layers and how to test them |
| `references/domains.md` | Nameserver moves and registrar transfers |
| `references/dns-and-email.md` | Records, Pages custom domains, Email Routing without breaking mail |
| `references/transactional-email.md` | Moving an app's own email off Resend or MailerSend onto Cloudflare Email Sending: cost, DMARC, the token, REST and SMTP, a one-variable switch |
| `scripts/` | Inventory, unzip, mirror, CMS export, form-submission export and import, screenshots, measurements, parity, redirects, video compression, Lighthouse |
| `templates/` | The new repo's starting files: Astro config, Layout, forms, mailer and rebuild Workers, headers, sitemap (`templates/README.md` maps them) |

## License

MIT © Adam Perlis. See [LICENSE](LICENSE).
