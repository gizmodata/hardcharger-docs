// The first mention of Hardcharger in each page's body carries the trademark (src/trademark.mjs).
// Runs on every page as it is rendered, prerendered pages included.
import { defineMiddleware } from 'astro:middleware';
import { markPageBody } from './trademark.mjs';

export const onRequest = defineMiddleware(async (_context, next) => {
	const response = await next();
	if (!response.headers.get('content-type')?.includes('text/html')) return response;
	const html = await response.text();
	return new Response(markPageBody(html), {
		status: response.status,
		statusText: response.statusText,
		headers: response.headers,
	});
});
