# Replacing Webflow's CMS

First get everything out: `scripts/export_cms.py <site_id> cms-export
--images` (a Webflow API token with cms:read), or the Webflow MCP's
`data_cms_tool`. Keep the export in the repo's `reference/cms/` as the record.
Then choose where each collection lives by who edits it and how it changes.

## Pick per collection

| The collection | Put it in | Why |
|---|---|---|
| A handful of items, edited rarely by a developer or Claude | **Astro content collections** (`src/content/<name>/*.md` or one JSON file, schema in `src/content.config.ts`, `z` from `astro/zod`) | No service, no account, in git, typed. |
| The same, but the owner wants a UI | **Keystatic** (git-based, free, edits commit to GitHub) | Still no hosted service. |
| Non-technical editors, frequent edits, or Zapier / API writes | **Sanity** (free plan: plenty for a marketing site; Studio hosted free at `<name>.sanity.studio`) | A proper editor, an HTTP API, webhooks, a Zapier integration. |
| Blog posts, newsletters | **The blogging platform the owner already uses** (Ghost, WordPress, Substack), or one of the options above | Purpose-built publishing. |
| Data owned by another system (ATS jobs, product catalogue, events) | **Read the source at build time** (Lever `api.lever.co/v0/postings/<account>?mode=json`, Ashby, Greenhouse job-board APIs); rebuild daily | Webflow only held a copy, synced by a connector. Don't keep a second one. |

## Sanity from zero (what actually happens)

1. **Sign in:** `npx sanity@latest login` is interactive (Google, GitHub or
   email), so run it in a terminal tab the owner can type into. It stores
   the token in `~/.config/sanity/config.json`; never print it.
2. **New account, no organization:** `sanity init -y` refuses to create a
   project without `--organization`, and a new account has none. Create the
   project through the management API instead. That makes a personal
   organization on the way.
   ```
   curl -X POST https://api.sanity.io/v2021-06-07/projects \
     -H "Authorization: Bearer $(token)" -H 'content-type: application/json' \
     --data '{"displayName":"Site name"}'
   ```
   Then `npx sanity@latest init -y --project <id> --dataset production
   --visibility public --output-path studio --template clean --typescript
   --package-manager npm`.
3. **The dataset:** `init` against an existing project does *not* create it.
   Run `npx sanity dataset create production --visibility public`. A public
   dataset lets the static build read without a token.
4. **The import:** `templates/studio/scripts/build-import.mjs` turns
   `reference/cms/*.json` into NDJSON:
   - Portable Text from Webflow HTML, through `htmlToBlocks` and jsdom,
     after stripping zero-width joiners, empty `<p>` and `id=""`.
   - Images as `_sanityAsset: "image@<webflow url>"`; Sanity fetches them.
   - Ids derived from the Webflow item ids, as `<type>-<webflowId>`. **Never
     put a dot in an id:** Sanity treats dotted ids (`testimonial.123`) as
     private, so a public dataset returns nothing for them without a token.

   Run it with `npx sanity exec scripts/build-import.mjs`: plain node can't
   import the schema's extensionless .ts files. Then
   `npx sanity dataset import <file>.ndjson production --replace`, which can
   be re-run safely.
5. **Deploy the Studio:** set `studioHost` in `sanity.cli.ts`, run
   `npx sanity deploy -y`, then pin the `deployment.appId` it prints.
   Editors sign in at `https://<host>.sanity.studio`.
6. **Hand off:** in manage.sanity.io → Members, the owner invites editors.
   Webhooks and the deploy hook come with the site's deploy (below).

## Sanity, wired for a static Astro site

- **Project:** `npm create sanity@latest` in `studio/` (or a separate repo).
  Define one schema type per collection, mirroring the Webflow fields:
  - PlainText → string
  - RichText → Portable Text (`block`)
  - Image → image
  - Reference / MultiReference → reference(s)
  - Option → string with options
  - Switch → boolean
  - Link → url
  - Number → number
  - Date → datetime
  Keep each item's Webflow slug as `slug.current`, so URLs don't change.
- **Import:** a one-off script reads `cms-export/<slug>/items.json`, uploads
  each image with `client.assets.upload`, converts rich-text HTML to
  Portable Text (`@portabletext/block-tools` `htmlToBlocks` + jsdom), and
  `createOrReplace`s documents with `_id: '<type>-<webflow-id>'` (idempotent
  re-runs). Resolve references by Webflow ID in a second pass.
- **Site:** `@sanity/client` in Astro frontmatter (or `@sanity/astro`),
  queried at build time with GROQ. Use `@sanity/image-url` for images (or
  `astro:assets` with remote patterns), and `astro-portabletext` for rich
  text. Template pages use `getStaticPaths` from the query, at Webflow's URL
  pattern (`/case-studies/[slug]`).
- **Publish → live:** the Pages project has to be Git-connected (step 10):
  deploy hooks exist only for those, and a direct-upload project can never
  be switched to Git, only replaced by a new project. Then:
  - **Deploy hook:** Pages project → Settings → Builds → Deploy hooks → Add
    (branch `main`). Anyone with its URL can start a build, so treat it as
    a secret: never in the repo or in chat.
  - **Sanity webhook:** sanity.io/manage → the project → API → Webhooks →
    Create. URL = the deploy hook, dataset `production`, trigger on create,
    update and delete, filter `_type in ["caseStudy", …]` (the site's
    types, so Studio-internal documents don't rebuild it), drafts off,
    method POST.
  - **Daily rebuild** for data read from another system (jobs from an ATS):
    `templates/workers/rebuild-cron`, a Worker whose Cron Trigger POSTs to
    the same hook (its URL is the Worker secret `DEPLOY_HOOK_URL`).
- **Tokens:** a read token only if the dataset is private (a public dataset
  needs none); a write token for Zapier, kept in Zapier. Never commit
  either; never print them.
- **Zapier:** use the Sanity app, or "Webhooks by Zapier" with a POST to
  `https://<project>.api.sanity.io/v2024-01-01/data/mutate/production`.

## Content collections, from the export

- **Convert the items:** turn `items.json` into one Markdown file per item
  (frontmatter from the fields, body from rich text via turndown), or one
  JSON array. Copy `files/` images to `src/assets/<collection>/` so
  `astro:assets` optimises them.

## Things that bite

- **Rich text:** Webflow's HTML carries `id=""` attributes,
  `<p>&nbsp;</p>` spacers, `<figure>` wrappers with `w-richtext-*` classes,
  and embeds. Clean them on import.
- **Images:** Webflow image URLs sit on `uploads-ssl.webflow.com` /
  `cdn.prod.website-files.com`. Download them all; don't hotlink.
- **Archived and draft items:** they come along in the export. Publish only
  what was live (`isDraft: false, isArchived: false`), but keep the rest in
  the CMS as drafts if the owner wants them.
- **Collection lists filtered in the Designer** (featured only, by type,
  sorted by an `order` field): reproduce the filter and sort in the query.
  Read them in the live HTML's order.
- **Sitemap:** CMS template pages must be in `sitemap.xml.ts` with their
  `lastUpdated` as lastmod.
- **Site search:** Webflow's `/search` relied on its index. Use Pagefind
  (`npx pagefind --site dist` after the build) for a static index.
