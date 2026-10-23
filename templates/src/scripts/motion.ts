// Motion, site-wide: Lenis smooth scrolling (as the Webflow site had) and the
// scroll reveals. Anything marked [data-reveal] gets .is-in as it comes into
// view and eases up into place (global.css); --reveal-delay staggers it, in ms.
// With reduced motion there's no .motion class, so nothing is hidden and
// nothing here runs but the check-in.
import Lenis from 'lenis';

const root = document.documentElement;

if (root.classList.contains('motion')) {
	const lenis = new Lenis({ autoRaf: true });
	// in-page anchors glide too
	document.addEventListener('click', (e) => {
		const a = (e.target as Element).closest?.('a[href^="#"]');
		const id = a?.getAttribute('href');
		if (!id || id === '#') return;
		const target = document.querySelector(id);
		if (!target) return;
		e.preventDefault();
		lenis.scrollTo(target as HTMLElement, { offset: -80 });
	});

	const seen = new IntersectionObserver(
		(entries) => {
			for (const entry of entries) {
				if (!entry.isIntersecting) continue;
				entry.target.classList.add('is-in');
				seen.unobserve(entry.target);
			}
		},
		{ rootMargin: '0px 0px -8% 0px' },
	);
	document.querySelectorAll('[data-reveal]').forEach((el) => seen.observe(el));
}

root.classList.add('motion-ready');
