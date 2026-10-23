// Full-page screenshots, desktop (1440) and phone (390), for comparing a
// rebuild with the Webflow original. Run from the repo (it needs
// playwright-core installed there: npm i -D playwright-core) and Google
// Chrome, or Playwright's Chromium (npx playwright install chromium).
//   node shots.mjs https://www.example.com live [out-dir] [/about /contact …]
//   node shots.mjs http://localhost:4321 local
// Pages default to the site's sitemap. Each page is scrolled through first
// so lazy media loads and scroll reveals fire. Out: <out-dir>/<label>/.
import { existsSync, mkdirSync, statSync } from 'node:fs';
import { createRequire } from 'node:module';
const { chromium } = createRequire(process.cwd() + '/')('playwright-core');

const [origin, label = 'shots', outArg, ...only] = process.argv.slice(2);
if (!origin) throw new Error('usage: node shots.mjs <origin> <label> [out-dir] [/paths…]');
// the third argument is the output folder if it's a relative path or an
// existing directory; a page path like /about is taken as a page
const isDir = (p) => existsSync(p) && statSync(p).isDirectory();
const outIsDir = outArg && (!outArg.startsWith('/') || isDir(outArg));
const outDir = outIsDir ? outArg : 'reference/shots';
if (outArg && !outIsDir) only.unshift(outArg);
let pages = only;
if (!pages.length) {
	const xml = await (await fetch(origin + '/sitemap.xml')).text().catch(() => '');
	pages = [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => new URL(m[1]).pathname || '/');
	pages.push('/__shots-404');
}
const sizes = { desktop: { width: 1440, height: 900 }, phone: { width: 390, height: 844 } };
const out = `${outDir}/${label}/`;
mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ channel: 'chrome' }).catch(() => chromium.launch());
for (const [size, viewport] of Object.entries(sizes)) {
	const context = await browser.newContext({ viewport });
	for (const path of pages) {
		const page = await context.newPage();
		await page.goto(origin + path, { waitUntil: 'networkidle', timeout: 60000 }).catch(() => {});
		const height = await page.evaluate(() => document.documentElement.scrollHeight);
		for (let y = 0; y < height; y += viewport.height / 2) {
			await page.evaluate((top) => window.scrollTo(0, top), y);
			await page.waitForTimeout(150);
		}
		await page.evaluate(() => window.scrollTo(0, 0));
		await page.waitForTimeout(1200);
		const name = (path === '/' ? 'home' : path.replace(/^\/|\/$/g, '').replace(/\//g, '__')) + `.${size}.png`;
		await page.screenshot({ path: out + name, fullPage: true });
		console.log(out + name);
		await page.close();
	}
	await context.close();
}
await browser.close();
