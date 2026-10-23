# Redirects

Every URL that worked on Webflow must still work after the move: as the
same page, or as a 301 to where it went. Search rankings, backlinks, email
links and bookmarks depend on it. Five layers, outermost first:

| Layer | What | Where it lives |
|---|---|---|
| 1. Protocol | http → https | Cloudflare: SSL/TLS → Edge Certificates → Always Use HTTPS |
| 2. Host | www → apex (or the reverse), keeping path + query | Cloudflare Redirect Rule (Rules → Redirect Rules → "Redirect from WWW to root"), 301 |
| 3. Preview host | `<project>.pages.dev` → the domain (optional) | Cloudflare Bulk Redirects (account level), 301, preserving path + query; canonicals already name the domain |
| 4. Paths | Webflow's 301s, changed slugs, dropped pages | `public/_redirects` (Pages: up to 2,000 static + 100 dynamic rules) |
| 5. Trailing slash, `.html` | `/about/` → `/about`, `/about.html` → `/about` | Pages does it (308) when the build writes `about.html` (`build.format: 'file'`) |

## Layer 4: building `_redirects`

1. **Webflow's own 301s:** Site settings → Publishing → 301 redirects →
   **Export** (a CSV of old,new). Convert it with
   `python3 -I scripts/redirects.py from-csv redirects.csv >> public/_redirects`.
   It converts Webflow's syntax:
   - Wildcards: Webflow `/blog/(.*)` → `/posts/%1` becomes Pages
     `/blog/* /posts/:splat 301`. A capture in the middle of a path becomes
     `:name` placeholders.
   - Webflow matches case-insensitively and ignores a trailing slash; Pages
     matches exactly. The script lowercases the source and adds the
     trailing-slash variant when the old path has none.
   - Absolute targets (`https://other.site/…`) stay absolute.
2. **Pages the rebuild drops:** for each page in the inventory not being
   carried over, 301 it to its nearest equivalent (a merged page, the
   section index, home). Leave a 404 only if nothing fits. For Webflow
   Ecommerce templates, password pages and template pages
   (`/checkout`, `/401`, `/style-guide`), redirect them only if they were
   ever linked or indexed (check Search Console → Pages).
3. **Changed slugs:** if a CMS item's slug changes in the new CMS, add
   `/collection/old-slug /collection/new-slug 301`. Better: keep Webflow's
   slugs.
4. **Collection path changes:** if `/blog/*` moves to another host (Ghost,
   WordPress), use `/blog/* https://blog.example.com/:splat 301`.
5. **Order:** Pages applies the first match, so put specific rules before
   wildcards. Keep 301 (permanent) for moves; use 302 only for temporary
   ones.

## Test them

- **Before the switch:**
  `python3 -I scripts/redirects.py check public/_redirects https://<project>.pages.dev`
  requests every source path and checks the status and `Location` against
  the rule. Wildcard rules are tested with a sample path.
- **After the switch:** run it again against the domain, plus:
  - `curl -sI http://example.com/x` gives a 301 to `https://example.com/x`;
  - `curl -sI https://www.example.com/x?y=1` gives a 301 to
    `https://example.com/x?y=1`;
  - every sitemap URL returns 200;
  - Search Console → Pages shows no new 404s over the following week.
- **Chains:** a redirect should land in one hop. `check` flags any
  target that itself redirects.
