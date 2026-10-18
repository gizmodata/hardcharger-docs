// The trademark in each page's metadata: the <title>, og:title and the descriptions get ™ on
// their first mention of Hardcharger (the site title, and so og:site_name, carries it already).
import { defineRouteMiddleware } from '@astrojs/starlight/route-data';
import { markFirst } from './trademark.mjs';

export const onRequest = defineRouteMiddleware((context) => {
	const route = context.locals.starlightRoute;
	for (const entry of route.head) {
		if (entry.tag === 'title' && entry.content) {
			// The landing page is titled "Hardcharger": no "Hardcharger | Hardcharger™".
			const [page, ...site] = entry.content.split(' | ');
			entry.content = page === 'Hardcharger' ? 'Hardcharger™' : [page, ...site].join(' | ');
		} else if (entry.tag === 'meta' && typeof entry.attrs?.content === 'string') {
			const key = entry.attrs.property ?? entry.attrs.name;
			if (key === 'og:title' || key === 'og:description' || key === 'description' || key === 'twitter:title') {
				entry.attrs.content = markFirst(entry.attrs.content);
			}
		}
	}
});
