// The sitemap: the same pages, in the same order and format, as Webflow's.
// lastmod is each page's own last change (Webflow's dates up to the move);
// bump a page's date when its content changes.
const pages: [path: string, lastmod: string][] = [
	// copied from the live sitemap.xml; '' is the home page
	['', '2026-01-01T00:00:00.000Z'],
	['/about', '2026-01-01T00:00:00.000Z'],
];
// CMS pages: add them from the collection, e.g.
//   ...(await getCollection('caseStudies')).map((c) => [`/case-studies/${c.id}`, c.data.updated])

const SITE = 'https://www.example.com';

export function GET() {
	const urls = pages.map(([path, lastmod]) => `    <url>\n        <loc>${SITE}${path}</loc>\n        <lastmod>${lastmod}</lastmod>\n    </url>`).join('\n');
	const xml = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n${urls}\n</urlset>`;
	return new Response(xml, { headers: { 'content-type': 'application/xml; charset=utf-8' } });
}
