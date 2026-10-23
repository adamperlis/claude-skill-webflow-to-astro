# Templates

Copy into the new repo (paths are the repo's), then replace PROJECT (the
Pages project name), DOMAIN, SITE and the placeholders noted in each file.
Add a `.nvmrc` with the Node version (22.22 or later, as `engines` in
`package.json` says); AGENTS.md and the Pages build's `NODE_VERSION` use it.

| File | What it is |
|---|---|
| `package.json` | Astro 7, Tailwind 4, wrangler; `npm run deploy` deploys to classic Pages with `--force` |
| `astro.config.mjs` | `site`, `build.format: 'file'` + `trailingSlash: 'never'` (Webflow's URLs), dev toolbar off |
| `wrangler.jsonc` | the Pages project: `pages_build_output_dir`, the forms KV namespace, the mailer service binding |
| `gitignore` | rename to `.gitignore`: deny-by-default env files, `reference/assets/*` ignored, manifest kept |
| `AGENTS.md` | the repo's notes for future sessions (add `CLAUDE.md` with `@AGENTS.md`) |
| `src/styles/global.css` | tokens skeleton, base size on body (not html), `.wrap`, reveal CSS |
| `src/layouts/Layout.astro` | head parity, canonical (strips `/index`), analytics on the live host only, motion failsafe |
| `src/components/BgVideo.astro` | lazy background video: loads and plays near the viewport, poster under reduced motion; `eager` for a hero |
| `src/scripts/motion.ts` | Lenis smooth scroll + `[data-reveal]` IntersectionObserver |
| `src/components/forms/SiteForm.astro`, `Field.astro`, `src/scripts/forms.ts` | a form that posts to `/api/forms` and shows Webflow-style thank-you / error panels or follows `redirect`; WebMCP `toolname` on the form itself |
| `functions/api/forms.ts` | the Pages Function: per-form validation, honeypot + time check, KV, mailer, optional Slack and CRM webhooks (`SLACK_WEBHOOK_URL`, `CRM_WEBHOOK_URL`; a Zapier Catch Hook works as the CRM one) |
| `workers/forms-mail/` | the mailer Worker (send_email, no routes, no workers.dev); `FORMS_TO` secret, `FROM_EMAIL` var |
| `workers/rebuild-cron/` | the daily rebuild: a Cron Trigger that POSTs to the Pages deploy hook (`DEPLOY_HOOK_URL` secret); Git-connected projects only |
| `src/data/entity.ts`, `src/lib/schema.ts` | the organization defined once, and the normalizer Layout runs every page's JSON-LD through: one `@graph` (Organization, WebSite, WebPage, BreadcrumbList from `crumbs`, FAQPage from `faq`, extra `schema` nodes). Wire it in Layout: `pageGraph({ canonical, title, description, jsonLd, crumbs, faq, schema })`, none on noindex pages |
| `public/_headers`, `public/_redirects` | security + cache headers (add the pages.dev `X-Robots-Tag: noindex` rules); Webflow's 301s |
| `src/pages/sitemap.xml.ts` | the sitemap with Webflow's pages, order, format and lastmod |
| `scripts/inbox.mjs` | `npm run inbox`: the latest form entries from KV |

These came out of real rebuilds (marketing sites with several forms, video
heroes, a CMS and a load-in preloader), so they run as-is once the
placeholders are filled.
