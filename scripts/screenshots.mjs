// Screenshots of the built site in Chromium and WebKit, light and dark, desktop and phone,
// and checks every page for console errors and horizontal overflow at phone width.
//   npm run build && npx astro preview --port 4329 &  node scripts/screenshots.mjs [outdir]
import { chromium, webkit } from '@playwright/test';
import fs from 'node:fs';

const base = process.env.DOCS_PREVIEW_URL ?? 'http://localhost:4329';
const out = process.argv[2] ?? 'screenshots';
fs.mkdirSync(out, { recursive: true });
const shots = [
	{ name: 'landing', path: '/' },
	{ name: 'guide-tls', path: '/guides/tls/' },
	{ name: 'desktop-app', path: '/guides/desktop-app/' },
	{ name: 'sql-monitor', path: '/guides/sql-monitor/' },
	{ name: 'server-configuration', path: '/guides/server-configuration/' },
	{ name: 'web-ui', path: '/guides/web-ui/' },
	{ name: 'extensions', path: '/guides/extensions/' },
];
const sizes = { desktop: { width: 1440, height: 900 }, phone: { width: 390, height: 844 } };
const pages = fs
	.readFileSync('dist/sitemap-0.xml', 'utf8')
	.match(/<loc>[^<]+<\/loc>/g)
	.map((l) => new URL(l.slice(5, -6)).pathname);
let problems = 0;
for (const [engineName, engine] of [['chromium', chromium], ['webkit', webkit]]) {
	const browser = await engine.launch();
	for (const scheme of ['light', 'dark']) {
		for (const [sizeName, viewport] of Object.entries(sizes)) {
			const context = await browser.newContext({ viewport, colorScheme: scheme, deviceScaleFactor: sizeName === 'phone' ? 2 : 1 });
			const page = await context.newPage();
			// Console errors count on the pages we look at, after they have settled; the quick
			// overflow sweep below navigates away mid-load, which aborts module imports.
			const errors = [];
			let watching = true;
			page.on('console', (m) => watching && m.type() === 'error' && errors.push(m.text()));
			page.on('pageerror', (e) => watching && errors.push(String(e)));
			for (const shot of shots) {
				await page.goto(base + shot.path, { waitUntil: 'networkidle' });
				await page.waitForTimeout(800); // mermaid renders after load
				await page.screenshot({ path: `${out}/${shot.name}-${engineName}-${scheme}-${sizeName}.png`, fullPage: false });
			}
			watching = false;
			if (sizeName === 'phone') {
				for (const path of pages) {
					await page.goto(base + path, { waitUntil: 'load' });
					const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
					if (overflow > 1) {
						console.log(`${engineName} ${scheme}: ${path} scrolls sideways by ${overflow}px`);
						problems++;
					}
				}
			}
			for (const e of errors.filter((e) => !e.includes('img.shields.io'))) {
				console.log(`${engineName} ${scheme} ${sizeName}: console error: ${e}`);
				problems++;
			}
			await context.close();
		}
	}
	await browser.close();
}
console.log(`${problems} problems`);
process.exit(problems ? 1 : 0);
