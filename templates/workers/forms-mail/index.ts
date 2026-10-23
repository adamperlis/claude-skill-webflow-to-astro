// Each entry from the site's forms (functions/api/forms.ts), emailed to the owner
// by Cloudflare Email Routing: free to an address verified in it, and no
// third party. Pages Functions can't hold a send_email binding, so the forms
// function calls this Worker through a service binding (MAILER).
// Their address is the secret FORMS_TO, never in this repo or on the site; the
// sender is FROM_EMAIL (wrangler.jsonc), on a domain with Email Routing on.
// Replying to the email replies to the person who wrote.

interface Entry {
	form: string;
	title: string;
	at: string;
	fields: Record<string, string>;
	contact: { name?: string; email?: string };
	labels: Record<string, string>;
	country?: string;
	agent?: boolean;
}

interface Env {
	EMAIL: {
		send(message: { to: string; from: { email: string; name?: string }; replyTo?: string; subject: string; text: string }): Promise<unknown>;
	};
	FORMS_TO?: string;
	FROM_EMAIL: string;
	FROM_NAME: string;
}

// one line, for the subject (a name with a newline in it can't add a header)
const line = (s = '') => s.replace(/[\r\n]+/g, ' ').trim();

export default {
	async fetch(request: Request, env: Env): Promise<Response> {
		if (request.method !== 'POST') return new Response(null, { status: 405 });
		if (!env.FORMS_TO) return new Response('FORMS_TO is not set', { status: 503 });
		const e = (await request.json()) as Entry;
		const { name = '', email: from = '' } = e.contact;
		await env.EMAIL.send({
			to: env.FORMS_TO,
			from: { email: env.FROM_EMAIL, name: env.FROM_NAME },
			replyTo: from,
			subject: `${e.title}: ${line(name)}`,
			text: [
				`${name} <${from}>`,
				'',
				...Object.entries(e.fields)
					.filter(([, v]) => v !== name && v !== from)
					.map(([k, v]) => `${e.labels[k] ?? k}:\n${v}\n`),
				`— sent ${e.at}${e.country ? ` from ${e.country}` : ''} through ${env.FROM_NAME}${e.agent ? ', by an AI agent on their behalf' : ''} (also kept: npm run inbox)`,
			].join('\n'),
		});
		return new Response(null, { status: 204 });
	},
};
