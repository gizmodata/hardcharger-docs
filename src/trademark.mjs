// Hardcharger™ is a pending trademark of GizmoData LLC (™, never ®: it is not registered).
// Its first mention on each page carries the mark: in the page's body (src/middleware.ts) and
// in its <title> and description metadata (src/starlightRouteData.ts). Never in code (inline,
// blocks, CLI output), never in headings (their anchors stay as they are), and never on
// "Chargewire".

const NAME = /\bHardcharger\b(?![™\-.\w])/;
const MARKED = /\bHardcharger™/;

/** The text with ™ after its first "Hardcharger" (a mention already marked counts). */
export function markFirst(text) {
	return MARKED.test(text) ? text : text.replace(NAME, 'Hardcharger™');
}

// Elements whose text is never marked: code and its output, headings, and what isn't prose.
const SKIP = new Set(['code', 'pre', 'kbd', 'samp', 'script', 'style', 'svg', 'textarea', 'title',
	'h1', 'h2', 'h3', 'h4', 'h5', 'h6']);
const VOID = new Set(['area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta',
	'source', 'track', 'wbr']);

/** Marks the first prose mention of Hardcharger in the page's content (Starlight's
 * `sl-markdown-content`). Works on the rendered HTML: tags and their attributes are left alone,
 * only text between them is looked at. */
export function markPageBody(html) {
	const start = html.indexOf('class="sl-markdown-content');
	if (start < 0) return html;
	const from = html.indexOf('>', start) + 1;
	const tokens = /<!--[\s\S]*?-->|<\/?([a-zA-Z][\w-]*)[^>]*>|[^<]+|</g;
	tokens.lastIndex = from;
	const skipping = [];
	let m;
	while ((m = tokens.exec(html)) !== null) {
		const [token, tag] = m;
		if (tag) {
			const name = tag.toLowerCase();
			if (token.startsWith('</')) {
				if (skipping.length && skipping[skipping.length - 1] === name) skipping.pop();
			} else if (!VOID.has(name) && !token.endsWith('/>') && (skipping.length || SKIP.has(name))) {
				skipping.push(name);
			}
		} else if (!skipping.length && token[0] !== '<') {
			if (MARKED.test(token)) return html;
			if (NAME.test(token)) {
				return html.slice(0, m.index) + markFirst(token) + html.slice(m.index + token.length);
			}
		}
	}
	return html;
}
