// Sends the site's forms to /api/forms (functions/api/forms.ts) and shows
// Webflow's thank-you or error panel, or goes on to data-redirect. The spam
// check needs the time the form was opened (t) and an empty honeypot.

type AgentSubmit = SubmitEvent & { agentInvoked?: boolean };

document.querySelectorAll<HTMLFormElement>('form[data-form]').forEach((form) => {
	const t = form.querySelector<HTMLInputElement>('input[name="t"]');
	if (t) t.value = String(Date.now());
	const box = form.parentElement!;
	const done = box.querySelector<HTMLElement>('[data-done]');
	const fail = box.querySelector<HTMLElement>('[data-fail]');
	const button = form.querySelector<HTMLButtonElement>('button[type="submit"]');

	form.addEventListener('submit', async (event: AgentSubmit) => {
		event.preventDefault();
		if (fail) fail.hidden = true;
		const data = new FormData(form);
		// WebMCP: an AI agent submitted it for someone (the site-wide script also
		// sets this field, but after this handler has run)
		if (event.agentInvoked === true && data.has('source_is_agent')) data.set('source_is_agent', 'true');

		const label = button?.textContent ?? '';
		if (button) {
			button.disabled = true;
			button.textContent = button.dataset.wait ?? label;
		}
		try {
			const res = await fetch('/api/forms', { method: 'POST', body: data });
			const body = (await res.json().catch(() => ({}))) as { ok?: boolean };
			if (!res.ok || !body.ok) throw new Error(`form ${res.status}`);
			if (form.dataset.redirect) {
				window.location.href = form.dataset.redirect;
				return;
			}
			form.hidden = true;
			if (done) done.hidden = false;
		} catch {
			if (fail) fail.hidden = false;
		} finally {
			if (button) {
				button.disabled = false;
				button.textContent = label;
			}
		}
	});
});
