// Prints the site's form entries stored in Cloudflare KV, newest first.
//   npm run inbox                  the latest 20, all forms
//   npm run inbox -- 50            the latest 50
//   npm run inbox -- 20 contact    just one form (a key of FORMS)
import { execFileSync } from 'node:child_process';

const NS = 'KV_NAMESPACE_ID';
const limit = Number(process.argv[2] ?? 20);
const only = process.argv[3];
const wrangler = (...args) => execFileSync('npx', ['wrangler', 'kv', ...args, '--namespace-id', NS, '--remote'], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] });

const keys = JSON.parse(wrangler('key', 'list', ...(only ? ['--prefix', `${only}:`] : [])))
	.map((k) => k.name)
	.sort((a, b) => b.split(':').slice(1).join(':').localeCompare(a.split(':').slice(1).join(':')))
	.slice(0, limit);
if (!keys.length) console.log('No entries yet.');
for (const key of keys) {
	const e = JSON.parse(wrangler('key', 'get', key));
	console.log(`\n${e.at}  ${e.title}  ${e.contact?.name} <${e.contact?.email}>${e.agent ? '  (via an AI agent)' : ''}`);
	for (const [k, v] of Object.entries(e.fields)) if (v !== e.contact?.name && v !== e.contact?.email) console.log(`  ${e.labels[k] ?? k}: ${v}`);
}
