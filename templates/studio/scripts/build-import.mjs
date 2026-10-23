// Builds the one-off import of the Webflow CMS content into Sanity:
// reference/cms/*.json (exported from Webflow) → reference/cms/sanity-import.ndjson.
// Rich text (Webflow HTML) becomes Portable Text; images are fetched by Sanity
// from their Webflow URLs at import time (`_sanityAsset`). Document ids are
// derived from the Webflow item ids (`<type>-<webflowId>`, never with a dot:
// Sanity keeps dotted ids private, unreadable without a token even in a
// public dataset), so re-running replaces rather than duplicates.
// The collections below (testimonials, case studies) are examples: replace
// them with the site's own.
// It reads one flat array per collection (`[{ id, name, slug, … }]`). From
// scripts/export_cms.py's `<slug>/items.json`, flatten each item first
// (`{ id: item.id, ...item.fieldData }`) and map Webflow's kebab-case field
// slugs onto the schema's names.
//   npx sanity exec scripts/build-import.mjs
//   npx sanity dataset import ../reference/cms/sanity-import.ndjson production --replace
import { readFileSync, writeFileSync } from 'node:fs';
import { JSDOM } from 'jsdom';
import { htmlToBlocks } from '@portabletext/block-tools';
import { Schema } from '@sanity/schema';
import { schemaTypes } from '../schemaTypes';

const cms = new URL('../../reference/cms/', import.meta.url);
const read = (f) => JSON.parse(readFileSync(new URL(f, cms), 'utf8'));
const schema = Schema.compile({ name: 'import', types: schemaTypes });
const blockType = (field) => schema.get('caseStudy').fields.find((f) => f.name === field).type;
// Webflow pads rich text with zero-width joiners and empty paragraphs
const clean = (html) => (html ?? '').replace(/‍/g, '').replace(/<p[^>]*>\s*<\/p>/g, '').replace(/ id=""/g, '');
const blocks = (html, field) => {
	const c = clean(html);
	if (!c.trim()) return undefined;
	return htmlToBlocks(c, blockType(field), { parseHtml: (h) => new JSDOM(h).window.document });
};
const image = (url) => (url ? { _type: 'image', _sanityAsset: `image@${url}` } : undefined);
const slug = (s) => ({ _type: 'slug', current: s });
const out = [];

for (const t of read('testimonials.json')) {
	out.push({ _id: `testimonial-${t.id}`, _type: 'testimonial', name: t.name, slug: slug(t.slug), personProfile: t.personProfile, type: t.type, text: t.text.trim(), avatar: image(t.avatar), order: t.order ?? undefined });
}
for (const c of read('case-studies.json')) {
	out.push({
		_id: `caseStudy-${c.id}`,
		_type: 'caseStudy',
		name: c.name,
		slug: slug(c.slug),
		client: c.client,
		typeOfWork: c.typeOfWork,
		workSummary: c.workSummary?.trim(),
		roles: c.role?.trim(),
		carouselImage: image(c.carouselImage),
		mainImage: image(c.mainImage),
		approach: blocks(c.approach, 'approach'),
		quote: blocks(c.quote, 'quote'),
		team: blocks(c.team, 'team'),
		next: c.next ? { _type: 'reference', _ref: `caseStudy-${c.next}` } : undefined,
		featured: c.featured,
		order: c.order,
	});
}
// …one loop like these per collection, its Webflow fields mapped onto the
// schema type's (plain fields as they are, rich text through blocks(), images
// through image(), references as `<type>-<webflowId>`)
writeFileSync(new URL('sanity-import.ndjson', cms), out.map((d) => JSON.stringify(d)).join('\n') + '\n');
console.log(`${out.length} documents → reference/cms/sanity-import.ndjson`);
