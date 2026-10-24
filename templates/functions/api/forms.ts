// POST /api/forms: the site's forms, which Webflow used to take (and Zapier
// used to forward). Each entry goes to KV, to the owner's inbox (the mailer
// Worker), to Slack (SLACK_WEBHOOK_URL) and to the CRM (CRM_WEBHOOK_URL), each
// only if configured; none of them can fail the form once it's stored, and if
// KV refuses the write the email alone carries the entry. A Cloudflare Pages Function: each
// entry is kept in KV (binding FORMS; read them with `npm run inbox`), then
// emailed to the owner by the mailer Worker (workers/forms-mail, through Cloudflare
// Email Routing), bound as MAILER. No address appears on the site or here.
//
// Field names are Webflow's (name, Email, Description, …), so entries line up
// with the old Webflow form exports.
//
// Spam: a hidden honeypot field, a minimum time on the form, size limits.

interface KV {
	put(key: string, value: string, opts?: { metadata?: unknown }): Promise<void>;
}

interface Env {
	FORMS?: KV;
	MAILER?: { fetch(input: Request | string, init?: RequestInit): Promise<Response> };
	/** optional: a Slack incoming-webhook URL (secret) */
	SLACK_WEBHOOK_URL?: string;
	/** optional: where the CRM takes new leads (secret); gets the entry as JSON */
	CRM_WEBHOOK_URL?: string;
}

interface Context {
	request: Request;
	env: Env;
	waitUntil(promise: Promise<unknown>): void;
}

type Field = { name: string; label: string; max: number; check?: (v: string) => boolean; optional?: boolean };
// which fields hold the person's name and email (for the email's reply-to and Slack)
type Form = { title: string; fields: Field[]; nameField: string; emailField: string };

const email = (v: string) => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v);
// for URL fields: check: url
const url = (v: string) => /^https?:\/\/\S+\.\S+/.test(v);
// Each form, keyed by the `kind` its <SiteForm> posts. Field names are
// Webflow's ("name-2", "Email-2", …), so entries line up with its old exports.
const FORMS: Record<string, Form> = {
	// e.g. the contact form; edit to match the site's forms
	contact: {
		title: 'Contact',
		nameField: 'name',
		emailField: 'Email',
		fields: [
			{ name: 'name', label: 'Name', max: 120 },
			{ name: 'Email', label: 'Email', max: 200, check: email },
			{ name: 'Message', label: 'Message', max: 5000 },
			// { name: 'Company', label: 'Company', max: 200, optional: true },
			// { name: 'LinkedIn-URL', label: 'LinkedIn', max: 300, check: url },
		],
	},
};

// the entry as a Slack message: title and who, then each field
const slack = (e: { title: string; contact: { name?: string; email?: string }; fields: Record<string, string>; labels: Record<string, string>; country?: string }) => ({
	text: `${e.title}: ${e.contact.name} <${e.contact.email}>`,
	blocks: [
		{ type: 'section', text: { type: 'mrkdwn', text: `*${e.title}* from *${e.contact.name}* <mailto:${e.contact.email}|${e.contact.email}>${e.country ? ` (${e.country})` : ''}` } },
		...Object.entries(e.fields)
			.filter(([k]) => e.labels[k] !== 'Name' && e.labels[k] !== 'Email')
			.map(([k, v]) => ({ type: 'section', text: { type: 'mrkdwn', text: `*${e.labels[k] ?? k}*\n${v.slice(0, 2900)}` } })),
	],
});

const json = (body: unknown, status = 200) =>
	new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json', 'cache-control': 'no-store' } });

const clean = (v: FormDataEntryValue | null, max: number) => String(v ?? '').trim().slice(0, max);

export async function onRequestPost({ request, env, waitUntil }: Context) {
	let form: FormData;
	try {
		form = await request.formData();
	} catch {
		return json({ ok: false, error: 'bad-request' }, 400);
	}

	const kind = clean(form.get('form'), 20);
	const spec = FORMS[kind];
	if (!spec) return json({ ok: false, error: 'unknown-form' }, 400);

	// Bots fill hidden fields and submit instantly; pretend it worked.
	const startedAt = Number(form.get('t') ?? 0);
	if (clean(form.get('company'), 200) || !startedAt || Date.now() - startedAt < 2500) {
		return json({ ok: true });
	}

	const fields: Record<string, string> = {};
	for (const f of spec.fields) {
		const v = clean(form.get(f.name), f.max);
		if (!v && f.optional) continue;
		if (!v || (f.check && !f.check(v))) return json({ ok: false, error: 'invalid', field: f.name }, 422);
		fields[f.name] = v;
	}

	if (!env.FORMS) return json({ ok: false, error: 'not-configured' }, 503);

	const at = new Date().toISOString();
	const entry = {
		form: kind,
		title: spec.title,
		at,
		fields,
		contact: { name: fields[spec.nameField], email: fields[spec.emailField] },
		labels: Object.fromEntries(spec.fields.map((f) => [f.name, f.label])),
		country: request.headers.get('cf-ipcountry') ?? undefined,
		// set by the WebMCP script when an AI agent submitted the form for someone
		agent: form.get('source_is_agent') === 'true' || undefined,
	};
	// keys sort oldest-first; the inbox script lists them newest-first. KV can
	// refuse a write (an outage, or the free plan's 1,000 writes a day across
	// the account, which one bulk import can use up), and then the email is
	// the only copy: the form answers ok only once it has gone.
	let kept = true;
	try {
		await env.FORMS.put(`${kind}:${at}:${crypto.randomUUID().slice(0, 8)}`, JSON.stringify(entry), {
			metadata: { at, name: fields[spec.nameField] },
		});
	} catch (err) {
		kept = false;
		console.error('forms: KV write failed, relying on the email', String(err));
	}
	const mailed = env.MAILER
		? env.MAILER.fetch('https://mail/', { method: 'POST', body: JSON.stringify(entry) }).then((r) => r.ok, () => false)
		: Promise.resolve(false);
	if (env.SLACK_WEBHOOK_URL) waitUntil(fetch(env.SLACK_WEBHOOK_URL, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(slack(entry)) }).catch(() => {}));
	if (env.CRM_WEBHOOK_URL) waitUntil(fetch(env.CRM_WEBHOOK_URL, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(entry) }).catch(() => {}));
	if (kept) {
		// already kept, so mail that fails never fails the form
		waitUntil(mailed);
		return json({ ok: true });
	}
	return (await mailed) ? json({ ok: true }) : json({ ok: false, error: 'unavailable' }, 503);
}
