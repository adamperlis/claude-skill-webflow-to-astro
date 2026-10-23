// Each page's JSON-LD as one graph: the organization and the website (src/data/entity.ts),
// the page, its breadcrumbs and FAQ, and whatever else the page describes.
//
// Pages still pass the JSON-LD they had on Webflow (src/data/*.ts, generated
// from the live pages). It's tidied here rather than edited there:
//   - every Organization named like the entity becomes a reference to the one node, and
//     any serviceType / areaServed / makesOffer on it moves to a Service that
//     the organization provides (they're not Organization properties);
//   - relative url / @id / item values become absolute on www ("#x" means
//     this page's #x);
//   - the page's own WebPage (or AboutPage…) merges into the base WebPage;
//   - City nodes' addressRegion / addressCountry go into an address;
//   - hand-written FAQPage nodes are dropped: the FAQ is rebuilt from the
//     questions the page actually shows (Google requires the two to match).
import { SITE, ORG_ID, WEBSITE_ID, organization, website } from '../data/entity';

type Node = Record<string, any>;
/** one question the page shows, and its answer (HTML allowed) */
export interface FaqItem {
	q: string;
	a: string;
}
export interface Crumb {
	name: string;
	path: string;
}

const PAGE_TYPES = ['WebPage', 'AboutPage', 'CollectionPage', 'ContactPage', 'ItemPage'];
// the old pages' own nodes for the organization (adjust the name test)
const isOrg = (n: Node) => n['@type'] === 'Organization' && n.name === organization.name;
const text = (html: string) =>
	html
		.replace(/<br\s*\/?>/gi, ' ')
		.replace(/<[^>]+>/g, '')
		.replace(/&nbsp;/g, ' ')
		.replace(/&amp;/g, '&')
		.replace(/&quot;/g, '"')
		.replace(/&#x27;|&#39;/g, "'")
		.replace(/\s+/g, ' ')
		.trim();

/** the FAQPage for the questions a page shows (several sets: one FAQPage) */
export function faqPage(canonical: string, items: FaqItem[]) {
	const seen = new Set<string>();
	const unique = items.filter((i) => !seen.has(i.q) && seen.add(i.q));
	return {
		'@type': 'FAQPage',
		'@id': `${canonical}#faq`,
		mainEntity: unique.map(({ q, a }) => ({ '@type': 'Question', name: text(q), acceptedAnswer: { '@type': 'Answer', text: text(a) } })),
	};
}

export function pageGraph(opts: {
	canonical: string;
	title: string;
	description?: string;
	jsonLd?: Node | Node[];
	crumbs?: Crumb[];
	faq?: FaqItem[];
	schema?: Node[];
}) {
	const { canonical, title, description, jsonLd, crumbs = [], faq, schema = [] } = opts;
	const abs = (u: string) => (u.startsWith('#') ? canonical + u : u.startsWith('/') ? new URL(u, SITE).href.replace(/\/$/, '') : u);
	const extras: Node[] = [];
	let page: Node = {};

	const norm = (n: any): any => {
		if (Array.isArray(n)) return n.map(norm);
		if (!n || typeof n !== 'object') return n;
		if (isOrg(n)) {
			const { serviceType, areaServed, makesOffer } = n;
			if (serviceType || areaServed || makesOffer)
				extras.push({
					'@type': 'Service',
					'@id': `${canonical}#service`,
					provider: { '@id': ORG_ID },
					...(serviceType && { serviceType }),
					...(areaServed && { areaServed: norm(areaServed) }),
					...(makesOffer && { hasOfferCatalog: { '@type': 'OfferCatalog', name: 'Services', itemListElement: norm(makesOffer) } }),
				});
			return { '@id': ORG_ID };
		}
		const out: Node = {};
		for (const [k, v] of Object.entries(n)) {
			if (k === '@context') continue;
			out[k] = typeof v === 'string' && ['url', '@id', 'item'].includes(k) ? abs(v) : norm(v);
		}
		if (out['@type'] === 'City' && (out.addressRegion || out.addressCountry)) {
			const { addressRegion, addressCountry, ...rest } = out;
			return { ...rest, address: { '@type': 'PostalAddress', addressLocality: out.name, ...(addressRegion && { addressRegion }), ...(addressCountry && { addressCountry }) } };
		}
		return out;
	};

	const own = (Array.isArray(jsonLd) ? jsonLd : jsonLd ? [jsonLd] : []).flatMap((b) => b['@graph'] ?? [b]);
	const nodes = own
		.filter((n) => !['FAQPage', 'WebSite', 'BreadcrumbList'].includes(n['@type']) && !(n['@type'] === 'Organization' && isOrg(n) && !n.serviceType && !n.areaServed && !n.makesOffer))
		.flatMap((n) => {
			if (PAGE_TYPES.includes(n['@type'])) {
				page = { ...page, ...norm(n) };
				return [];
			}
			const x = norm(n);
			return x['@id'] === ORG_ID && Object.keys(x).length === 1 ? [] : [x];
		});
	// a FAQPage nested in the WebPage goes too (rebuilt from what's on the page)
	if (page.mainEntity?.['@type'] === 'FAQPage') delete page.mainEntity;
	delete page.breadcrumb;

	const trail = crumbs.length ? [{ name: 'Home', path: '/' }, ...crumbs] : [];
	return {
		'@context': 'https://schema.org',
		'@graph': [
			organization,
			website,
			{
				'@type': 'WebPage',
				...page,
				'@id': `${canonical}#webpage`,
				url: canonical,
				name: page.name ?? title,
				...(description && { description }),
				isPartOf: { '@id': WEBSITE_ID },
				publisher: { '@id': ORG_ID },
				inLanguage: 'en-US',
				...(trail.length && { breadcrumb: { '@id': `${canonical}#breadcrumb` } }),
			},
			...(trail.length
				? [
						{
							'@type': 'BreadcrumbList',
							'@id': `${canonical}#breadcrumb`,
							itemListElement: trail.map((c, i) => ({ '@type': 'ListItem', position: i + 1, name: c.name, item: abs(c.path) })),
						},
					]
				: []),
			...nodes,
			...extras,
			...schema.map(norm),
			...(faq?.length ? [faqPage(canonical, faq)] : []),
		],
	};
}
