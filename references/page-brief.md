# Page-agent brief (template)

Fill in the <PLACEHOLDERS>, save it to a scratch file, and give each page
agent its path plus its own task (route, head values, section list). Write the
shared shell (Layout, Nav, Footer, shared CTA, tokens) and measure it against
live *before* spawning agents; they build on it and mustn't edit it.

---

# Rebuilding a <SITE> page in Astro: brief for page agents

<SITE> is on Webflow today and is being rebuilt, page for page, as an Astro 7
+ Tailwind 4 static site on Cloudflare Pages. Your job: rebuild the page(s)
named in your task so they look and behave like the live Webflow page, at
desktop and on phones, as clean Astro + Tailwind, not pasted Webflow markup.

## The repo: <REPO>

- **Node:** use the repo's `.nvmrc` version (`nvm use`, or your version
  manager's equivalent) before node/npx.
- **Dev server:** one is already running at http://localhost:<PORT> with
  HMR. Don't stop it; if it's down: `npx astro dev --background --port <PORT>`.
- **After you create any new .astro file, run `touch src/styles/global.css`**
  (touch only, never edit it). Tailwind's dev server doesn't see classes in
  files created after it started, so new markup renders unstyled until it
  rescans.
- **Don't run `astro build`**: other agents share the checkout and dist/.
- **Don't touch git.** The lead commits.
- **Other agents work in this checkout too.** Only create or edit the files
  your task owns.
- **Scratch files:** use names unique to you (e.g. `measure-<page>.mjs`).
  Shared scratch scripts get overwritten.

## What already exists (shared: don't edit; report changes you need)

- `src/layouts/Layout.astro`: head, analytics, nav, footer, motion. Props:
  <LIST THE PROPS>.
- `src/components/`: <LIST: Nav, Footer, the shared CTA, Button variants,
  Eyebrow/pill, BgVideo (lazy; `eager` for a hero), Logo, icons/>.
- `src/styles/global.css` tokens: <LIST colours, fonts, text-h1…, text-body,
  .wrap, .label>.
  - 1rem = 16px, so Tailwind's spacing scale is standard (p-4 = 16px).
  - The site's base text size is set on `body`; set sizes explicitly.
- `src/scripts/motion.ts`: elements with `data-reveal` fade and slide up as
  they scroll into view, staggered with `style="--reveal-delay:150"` (ms).
  gsap is installed for more (marquees, scrubs, pins); honour
  `prefers-reduced-motion`. Never put a reveal on the page's main heading:
  it's usually the LCP element.
- The owner's design system, if any: <PATH>.

## The reference

- `reference/live/<page>.html`: the live page's HTML exactly as Webflow
  served it. It's your source of truth for text (copy it verbatim), links
  (same hrefs, same target=_blank), structure and order.
- `https://<DOMAIN>/<page>`: the live page. Look at it at 1440 and 390 wide
  for hover states, sliders and reveals. Webflow interactions hide elements
  until they scroll into view, so full-page screenshots miss things.
- `reference/shots/live/<page>.desktop.png` and `.phone.png`: blank areas are
  usually unrevealed content, not empty space.
- `reference/assets/css/*.css`: Webflow's CSS, for exact sizes, colours,
  spacing and breakpoints (991/767/479px).
- `reference/assets/{images,videos,fonts}/` and `manifest.json`: every file
  the live pages load.
- **Skip any element whose class list includes `hidden`,** but check the
  CSS first: Webflow combo classes sometimes un-hide it
  (`.foo.hidden { display: block }`).
- Skip Webflow template leftovers that don't show on live, and say so.

## How to build

- **Files:** the page goes in `src/pages/<route>.astro`, page-only components
  in `src/components/<page>/`, and new icons in `src/components/icons/` (new
  files only).
- **Rasters:** copy the ones you use into `src/assets/<page>/` with clean
  kebab-case names, from the largest original (not Webflow's `-p-500`
  variants). Render them with `<Image>`/`<Picture>` from `astro:assets`, and
  set `widths`/`sizes` for big ones. Write real alt text.
- **SVGs:** inline small ones; put the rest in `public/images/<page>/`.
- **Videos:** use `public/videos/<clean-name>.mp4` plus its poster, under
  25 MiB (Cloudflare Pages refuses bigger files). The MP4 is what browsers
  play, so skip a WebM that's over the cap.
- **Breakpoints:** use one kind per component, either Tailwind's (`md:`,
  `lg:`) or px (`min-[992px]:`), never both on the same property. Tailwind 4
  can order mixed rem and px variants wrongly. Best of all, define
  Webflow's own as theme breakpoints in global.css and write desktop styles
  unprefixed, then `max-lg:` (≤991), `max-md:` (≤767) and `max-sm:` (≤479),
  the same direction as Webflow's CSS.
- **Webflow's base styles are part of the look.** Copy the ones a section
  relies on:
  - `h1`–`h6` margins and paddings;
  - a bare `p` (padding-top 1em, line height, letter spacing);
  - `.w-form`'s 15px bottom margin;
  - `.w-container`'s 940px width (728 at ≤991);
  - `.w-richtext` spacing.

  They live in the Webflow CSS before the site's own classes.
- **Fluid sites:** many Webflow sites set the body to `1vw` and size
  everything in `em`. Keep that; don't convert to fixed px.
- **Layout:** align content with the nav's container (`.wrap`) at every
  width, including very wide screens (check 2000px).
- **Head:** pass the live page's exact title, description, OG image and
  JSON-LD to Layout. In JSON-LD, swap any Webflow CDN URL for the site's own.
- **Nothing may load from Webflow's hosts** (`cdn.prod.website-files.com`,
  `uploads-ssl.webflow.com`, `d3e54v103j8qbb.cloudfront.net`). Third-party
  embeds the live page uses on purpose are fine.
- **Accessibility:** real headings in order, buttons that are buttons,
  visible focus, AA contrast. For small text in a light accent colour, use a
  darker variant and say so.

## Search and answer engines: better structure, same words

The rebuild is the cheapest moment to make a page easy for search and AI
engines to read (the `seo-aeo-geo` skill's "Structure" lens). Improve the
markup freely, but **don't change the words**: wording is the owner's call.

- **Headings:**
  - One `h1` that says what the page is.
  - `h2`/`h3` in order, never skipping a level.
  - Where Webflow styled a `div` to look like a heading, use the real tag
    with the same look. Where it used an `h2` purely for size, use a `p`
    with that style.
- **Sections:** each `<section>` starts with its heading, so it makes sense
  on its own when an engine lifts it out.
- **Elements for what they are:** lists as `ul`/`ol`, dates in
  `<time datetime>`, tabular data as a `table`, and quotes in `blockquote`
  with their source.
- **FAQs:** questions as headings or `summary`, answers as plain text
  beneath. Pass the items to Layout's `faq` prop; the FAQPage schema is
  built from it.
- **Text, not pictures of text:** anything Webflow drew as an image, or
  filled in with JavaScript (counters, feeds, tabs), is rendered as HTML
  text, with the image kept as decoration if it matters to the look.
- **Alt text:** say what the image shows. Use `alt=""` for decoration.
- **Ideas that would change words** go in your report as SEO proposals, not
  in the page. For example: the page never says plainly what it offers in
  its first lines, a heading is vague, the H1 is a slogan, or two pages say
  nearly the same thing.

## Check your work

Compare with live, section by section, desktop and phone:
- **Screenshots:** `node <SKILL>/scripts/shots.mjs http://localhost:<PORT> local reference/shots /<route>`.
  Read them with the Read tool (crop tall ones with
  `ffmpeg -i in.png -vf "crop=1440:1800:0:0,scale=720:-1" out.jpg`).
- **Measurements:** `node <SKILL>/scripts/measure.mjs <url> <w> <h> '<expr>'`
  on live and local, matching element positions to within a few px.
- **No console errors,** and no requests to Webflow hosts.
- **Motion in headless Chrome** (Playwright, as `scripts/shots.mjs` uses):
  sample positions over time there. A hidden browser pane runs as a
  background page, and its transitions don't advance.
- **Details owners caught on their phones** (check these yourself first):
  - a small number or arrow beside big text with a tall line height
    (menus): align it to the word's cap height, not the top of the line
    box;
  - an icon beside a heading (LinkedIn): make the row `flex items-center`,
    because an inline `<img>` sits on a text line of its own and hangs low;
  - footer and nav logos: Webflow sites often have two different files,
    one of them an old trace; use the nav's SVG in both;
  - fixed-height chart or canvas boxes (`h-[800px]` around a square
    canvas): `h-auto` on phones, or the panel is a screenful of empty space.

## When you're done

Reply with:
- the files you created;
- the assets you copied (path and size);
- anything on live you left out or changed, and why;
- anything you needed from a shared file (and didn't edit);
- the markup you improved for search, and your SEO proposals.

Keep it short.
