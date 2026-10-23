// The organization, defined once. Every page's JSON-LD points at this node by
// its @id (src/lib/schema.ts), so search and answer engines see one entity,
// not one per page. Every fact here comes from the owner: ask, don't infer
// from the old pages (they usually disagree with each other).
//
// '@type' follows what the site is (references/site-types.md): Organization,
// a subtype (LocalBusiness, Restaurant, NGO, OnlineStore…), or a Person for a
// portfolio or personal site, with that type's own properties (address and
// openingHoursSpecification for a local business, jobTitle for a person).

export const SITE = 'https://www.EXAMPLE.com';
export const ORG_ID = `${SITE}/#organization`;
export const WEBSITE_ID = `${SITE}/#website`;

export const organization = {
	'@type': 'Organization',
	'@id': ORG_ID,
	name: 'NAME',
	alternateName: [],
	url: SITE,
	logo: { '@type': 'ImageObject', '@id': `${SITE}/#logo`, url: `${SITE}/apple-touch-icon.png`, width: 256, height: 256 },
	image: { '@id': `${SITE}/#logo` },
	description: 'NAME is … (one plain sentence: what it is, for whom, where).',
	email: 'hello@EXAMPLE.com',
	foundingDate: 'YYYY',
	founder: { '@type': 'Person', name: 'FOUNDER', url: 'https://FOUNDER-SITE' },
	areaServed: 'Worldwide',
	knowsAbout: [],
	// the company's own profiles: LinkedIn, Crunchbase, Clutch, YouTube, podcast…
	sameAs: [],
};

export const website = {
	'@type': 'WebSite',
	'@id': WEBSITE_ID,
	url: SITE,
	name: 'NAME',
	publisher: { '@id': ORG_ID },
	inLanguage: 'en-US',
};
