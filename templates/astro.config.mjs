// @ts-check
import { defineConfig } from 'astro/config';

import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
	// Canonical URLs and Open Graph tags name this domain.
	site: 'https://www.example.com', // the live domain: canonicals and OG URLs use it
	// Webflow serves every page without a trailing slash (example.com/about), so
	// the build writes about.html, which Pages serves at /about.
	trailingSlash: 'never',
	build: { format: 'file' },
	// screenshots of the dev server are compared with the live site
	devToolbar: { enabled: false },
	vite: {
		plugins: [tailwindcss()],
	},
});
