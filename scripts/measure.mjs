// Measure elements on a page: a JS expression evaluated in the page, printed
// as JSON. Use it on the live page and the rebuild at the same width and
// match the numbers. Run from the repo (needs playwright-core) and Google
// Chrome, or Playwright's Chromium (npx playwright install chromium).
//   node measure.mjs <url> <width> <height> '<expression>'
// e.g. boxes of the first h1 and the nav logo:
//   node measure.mjs https://www.example.com 1440 900 '(()=>{const r=e=>{const b=e.getBoundingClientRect();return [b.left,b.top+scrollY,b.width,b.height].map(Math.round)};return {h1:r(document.querySelector("h1")),logo:r(document.querySelector("header a"))}})()'
// It loads lazy images and scrolls the page first, so live and local are
// measured in the same settled state. Use your own copy of this file per
// agent: parallel agents overwrite shared scratch scripts.
import { createRequire } from 'node:module';
const { chromium } = createRequire(process.cwd() + '/')('playwright-core');
const [url, w, h, expr] = process.argv.slice(2);
const b = await chromium.launch({ channel: 'chrome' }).catch(() => chromium.launch());
const p = await b.newPage({ viewport: { width: +w, height: +h } });
await p.goto(url, { waitUntil: 'networkidle' }).catch(() => {});
// Webflow lazy-loads images (slider arrows, avatars): unloaded they measure
// 0px tall. Force them to load and walk the page so scroll reveals run, then
// go back to the top before measuring.
await p.evaluate(async () => {
	document.querySelectorAll('img[loading="lazy"]').forEach((i) => (i.loading = 'eager'));
	for (let y = 0; y < document.documentElement.scrollHeight; y += innerHeight / 2) {
		scrollTo(0, y);
		await new Promise((r) => setTimeout(r, 60));
	}
	scrollTo(0, 0);
});
await p.waitForLoadState('networkidle').catch(() => {});
await p.waitForTimeout(2500);
console.log(JSON.stringify(await p.evaluate(expr)));
await b.close();
