## Project

SITE's website. Astro 7 + Tailwind 4, built as a fully static site and served
by Cloudflare Pages (project `PROJECT`) at https://DOMAIN (and
PROJECT.pages.dev); deploy with `npm run deploy`. Rebuilt page for page from
the Webflow site on DATE; `docs/move.md` has how it's set up and what's left.
Never deploy the site as a Worker: that lands on the account's shared
workers.dev subdomain. (The forms' mailer, `workers/forms-mail`, is a Worker
with no public address, reached only through a service binding.)

- Node 22.22+ (`.nvmrc`). Run `nvm use` (or your version manager's
  equivalent) first.
- Design tokens live in `@theme` in `src/styles/global.css`. Use the token
  utilities rather than raw colours.
- Every page keeps its Webflow URL (no trailing slash: `build.format: 'file'`),
  title, description, OG image, canonical and JSON-LD.
  `src/pages/sitemap.xml.ts` lists the same pages as Webflow's sitemap.
- `reference/live/*.html` is each Webflow page as it was served at the move.
  Check a page against it before changing what it says.
- Forms post to `functions/api/forms.ts`: KV (`npm run inbox`) plus email
  through `workers/forms-mail`. No email address is on the site or in the repo.
- Cloudflare Pages refuses files over 25 MiB.
- Never commit `.env*` or `.dev.vars*` files other than `*.example`.

## Development

Start the dev server with `astro dev --background` (manage it with
`astro dev stop|status|logs`). Tailwind in the dev server doesn't see
classes in .astro files created after it started: `touch
src/styles/global.css` makes it rescan.
