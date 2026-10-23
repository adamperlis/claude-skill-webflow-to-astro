// Rebuilds the site every morning, so data read at build time from another
// system (jobs from an ATS) stays current: a Cron Trigger that POSTs to the
// Pages project's deploy hook (the secret DEPLOY_HOOK_URL). CMS publishes call
// the same hook from a webhook. No routes, no workers.dev address.

interface Env {
	DEPLOY_HOOK_URL?: string;
}

export default {
	async scheduled(_controller: ScheduledController, env: Env, ctx: ExecutionContext) {
		if (!env.DEPLOY_HOOK_URL) return console.error('DEPLOY_HOOK_URL is not set');
		ctx.waitUntil(
			fetch(env.DEPLOY_HOOK_URL, { method: 'POST' }).then((res) => console.log(`deploy hook: ${res.status}`)),
		);
	},
};
