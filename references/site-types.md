# Site types: what changes with the kind of site

Every Webflow site moves the same way: inventory, backup, rebuild, parity,
deploy, switch. What it's *for* changes the details: what counts as a
conversion, which schema describes it, which Webflow features it leans on,
and where search and AI engines find it. Settle this in the inventory and
write it at the top of `docs/move.md`.

## Find the type

Ask the owner what the site is for and what a visitor should do there.
Confirm it from the inventory:
- **CMS collections:** products, posts, events, menu items, listings.
- **Forms:** contact, quote, booking, newsletter, application, donation.
- **Embeds:** a booking widget, a shop, a donation form, a podcast player.
- **Webflow features:** Ecommerce, User Accounts, Localization, password
  pages.

A site can be more than one kind: a studio with a shop, a restaurant with
a blog. Take each part on its own.

## By type

| Type | Entity (`src/data/entity.ts`) | What counts as a conversion | Watch for | Search and AI (with `seo-aeo-geo`) |
|---|---|---|---|---|
| **Company, studio, SaaS** | Organization (or Corporation, ProfessionalService); SoftwareApplication for a product | contact, demo or quote request; signup | form routing to sales, CRM, Slack; pricing pages | comparison and "best X for Y" prompts; reviews on third-party directories |
| **Portfolio, personal site** | Person, with `sameAs` to their profiles; ProfilePage for the about page | contact, booking a call | case-study pages, image weight, video | the person as one entity across their profiles; talks, interviews, podcasts |
| **Shop** | Organization or OnlineStore; Product + Offer on product pages | purchase | Webflow Ecommerce (below) | Product schema with price and availability; Google Merchant Center free listings |
| **Restaurant, local business** | LocalBusiness or a subtype (Restaurant, Store, Dentist…) with address, geo, hours; `hasMenu` | reservation, call, directions, order | booking and ordering embeds; hours and prices in many places | Google Business Profile with the same name, address and phone as the site; local "near me" prompts |
| **Nonprofit** | NGO (or Organization) | donation, volunteer signup, newsletter | donation embeds (they carry over), campaign pages | the cause and the organization tied together; news and partner coverage |
| **Publication, blog, newsletter** | Organization or Person as publisher; Article/BlogPosting with author on posts | subscription | RSS, author pages, archives, comments | freshness (real `dateModified`), author pages, Article schema; Perplexity favours recent pieces |
| **Events, courses, community** | Organization; Event or Course on each page | registration, ticket, enrollment | ticketing embeds; past events kept as pages, not deleted | Event schema with dates and location; past events stay up |

These are starting points. The `seo-aeo-geo` skill decides the details for
the site's own category: which engines matter and which third-party sites
they cite for it. The money prompts in the baseline are the questions *this*
audience asks: buyers, diners, donors, readers, students.

## Webflow features that need their own plan

- **Ecommerce** (products, cart, checkout, orders, through Stripe or
  PayPal). The cart and checkout don't come with the export.
  - **Get it all out first:** export products (with variants, SKUs,
    prices, inventory, images) and orders, as CSV from the dashboard or
    through the Webflow API's ecommerce endpoints.
  - **Pick the replacement by size:**
    - **A handful of products:** Stripe Payment Links or Checkout. The
      product pages stay static.
    - **A real catalogue:** Shopify (Buy Button or a headless storefront),
      Snipcart, or Lemon Squeezy for digital goods.
  - **Keep each product's URL;** move the cart and checkout to the new
    provider's.
  - **Payments:** Stripe data stays in Stripe. Only the connection
    changes.
  - **Test a real purchase** in the provider's test mode.
  - **Transactional emails** (order confirmations) move to the provider.
    Recreate them before the switch.
- **User Accounts and gated content** (logins, members-only pages). A
  static site can't check a login.
  - **Third-party membership scripts** already on the site (Memberstack,
    Outseta and the like) usually carry over as they are. Add the new
    domains to their allowed list.
  - **Webflow's own accounts** need a replacement: one of those services,
    or an auth provider plus on-request rendering for the gated routes
    only (Astro's Cloudflare adapter).
  - **Staff-only pages:** Cloudflare Access is enough.
  - **Members:** export them, and tell them before the switch, because
    they'll need to sign in again.
- **Localization** (locales such as `/fr/…`):
  - **URLs:** keep every locale's URLs, using Astro's i18n routing.
  - **Alternates:** `hreflang` on every page, both ways, plus `x-default`.
  - **The sitemap** lists the alternates.
  - **Parity:** check every locale, not just the default.
- **Password-protected pages and folders:** don't let them become public
  static pages. Put them behind Cloudflare Access, or a small Function that
  checks a password, or ask the owner whether they're still needed.
- **File-upload fields:** a Pages Function can take the multipart post and
  store the file in R2 (size-limited, with an allowed list of types). Email
  the owner a link, never the file.
- **Newsletter signups:**
  - **Embeds:** an embed from the mail platform (Mailchimp, Kit, Beehiiv,
    Substack) carries over as it is.
  - **Native forms:** a Webflow form that fed the list through Zapier
    posts straight to the platform's API from the form function.
- **RSS:** if a collection had a feed (look for
  `<link rel="alternate" type="application/rss+xml">`), keep it at the
  same URL with `@astrojs/rss`, or subscribers and aggregators lose it.
- **Site search:** Pagefind, built after the site builds.
- **Logic flows, Optimize tests, Analyze:** these don't move.
  - **Logic flows:** rebuild what a flow did in the form function, or in a
    Worker.
  - **Analytics:** GA4 or Cloudflare Web Analytics replace Analyze.
  - **A/B tests** need another tool, if the owner still runs them.

## Conversions, after the move

Whatever the type, every conversion has to keep being counted:
- **Key events:** each conversion fires the same analytics key event as
  before (form success, purchase, booking, donation, signup).
- **Embeds:** test each embed's own success callback on the pages.dev
  build.
- **In `docs/move.md`:** list each conversion, where it now lands (KV,
  email, a provider) and how it's counted.
