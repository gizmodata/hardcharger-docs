// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import mermaid from 'astro-mermaid';
import starlightLinksValidator from 'starlight-links-validator';
import starlightLlmsTxt from 'starlight-llms-txt';

// The site's address. DOCS_SITE and DOCS_BASE point a build at wherever it is served (the
// custom domain, the private preview on GitHub Pages, localhost). DOCS_GA=true is the one
// switch between the private preview and the public site (README, "Private preview and GA"):
// without it every page says noindex and carries the preview banner (src/components/ga.ts).
const site = process.env.DOCS_SITE ?? 'https://docs.hardcharger.gizmodata.com';
const base = process.env.DOCS_BASE ?? '/';
const indexable = process.env.DOCS_GA === 'true';

export default defineConfig({
	site,
	base,
	trailingSlash: 'always',
	// Pages that moved, from their old address to the new one. GitHub Pages can't send an HTTP
	// redirect, so Astro writes a page at each old address that forwards at once (and names
	// the new one as canonical). The one place the protocol's earlier name may stay.
	redirects: {
		'/concepts/warp-sql/': '/concepts/chargewire/',
		'/reference/warp-sql-protocol/': '/reference/chargewire-protocol/',
	},
	integrations: [
		mermaid({ theme: 'dark', autoTheme: true }),
		starlight({
			title: 'Hardcharger™',
			description:
				'Hardcharger™ is GizmoData’s DuckDB 2.0 server: fast, secure, remote DuckDB over the Chargewire protocol. Every feature included.',
			// The Hardcharger lockup (bull head and lettering) replaces the title text; the GizmoData
			// logo stays in the footer.
			logo: {
				light: './src/assets/brand/hardcharger-logo-light.svg',
				dark: './src/assets/brand/hardcharger-logo-dark.svg',
				alt: 'Hardcharger™',
				replacesTitle: true,
			},
			favicon: '/favicon.svg',
			// Hardcharger™ in each page's <title> and descriptions; the body: src/middleware.ts.
			routeMiddleware: './src/starlightRouteData.ts',
			customCss: ['./src/styles/theme.css'],
			editLink: { baseUrl: 'https://github.com/gizmodata/hardcharger-docs/edit/main/' },
			lastUpdated: true,
			social: [
				{ icon: 'github', label: 'GitHub', href: 'https://github.com/gizmodata/hardcharger' },
				{
					icon: 'slack',
					label: 'GizmoData Community Slack',
					href: 'https://join.slack.com/t/gizmodatacommunity/shared_invite/zt-42jk7kdti-SJp7qk7d6XYCIKfBG~4HrA',
				},
			],
			components: {
				Footer: './src/components/Footer.astro',
				SocialIcons: './src/components/SocialIcons.astro',
				Banner: './src/components/Banner.astro',
				PageTitle: './src/components/PageTitle.astro',
			},
			head: [
				{ tag: 'link', attrs: { rel: 'icon', href: `${base}favicon.ico`.replace('//', '/'), sizes: '32x32' } },
				{ tag: 'link', attrs: { rel: 'apple-touch-icon', href: `${base}apple-touch-icon.png`.replace('//', '/') } },
				{ tag: 'meta', attrs: { name: 'theme-color', content: '#0b1416' } },
				{ tag: 'meta', attrs: { property: 'og:image', content: new URL(`${base}og.png`.replace('//', '/'), site).href } },
				{ tag: 'meta', attrs: { property: 'og:image:width', content: '1200' } },
				{ tag: 'meta', attrs: { property: 'og:image:height', content: '630' } },
				{ tag: 'meta', attrs: { name: 'twitter:card', content: 'summary_large_image' } },
				...(indexable ? [] : [{ tag: 'meta', attrs: { name: 'robots', content: 'noindex, nofollow' } }]),
			],
			expressiveCode: {
				themes: ['github-dark-default', 'github-light-default'],
				styleOverrides: { borderRadius: '0.6rem', frames: { shadowColor: 'transparent' } },
			},
			plugins: [
				starlightLinksValidator({ errorOnLocalLinks: false }),
				starlightLlmsTxt({ projectName: 'Hardcharger' }),
			],
			sidebar: [
				{
					label: 'Get started',
					items: [
						{ label: 'Quickstart', slug: 'get-started/quickstart' },
						{ label: 'Your first query', slug: 'get-started/first-query' },
						{ label: 'Desktop app (v2.1.0+)', slug: 'guides/desktop-app' },
						{ label: 'Web UI', slug: 'guides/web-ui' },
						{ label: 'Coming from GizmoSQL', slug: 'get-started/coming-from-gizmosql' },
					],
				},
				{
					label: 'Concepts',
					items: [
						{ label: 'Chargewire in one page', slug: 'concepts/chargewire' },
						{ label: 'Security model', slug: 'concepts/security-model' },
						{ label: 'Performance model', slug: 'concepts/performance-model' },
					],
				},
				{
					label: 'Guides',
					items: [
						{
							label: 'Security',
							items: [
								{ label: 'TLS and mTLS', slug: 'guides/tls' },
								{ label: 'Users, roles and grants', slug: 'guides/access-control' },
								{ label: 'Row policies and masking', slug: 'guides/row-policies-and-masking' },
								{ label: 'Catalog access rules', slug: 'guides/catalog-access-rules' },
								{ label: 'SSO, OIDC and browser sign-in', slug: 'guides/sso' },
							],
						},
						{
							label: 'Data',
							items: [
								{ label: 'DuckDB extensions', slug: 'guides/extensions' },
								{ label: 'DuckLake and S3', slug: 'guides/ducklake-and-s3' },
								{ label: 'Bulk ingest', slug: 'guides/bulk-ingest' },
							],
						},
						{
							label: 'Operations',
							items: [
								{ label: 'Configuration (YAML, env, flags)', slug: 'guides/configuration' },
								{ label: 'SQL Monitor', slug: 'guides/sql-monitor' },
								{ label: 'Server Configuration tab', slug: 'guides/server-configuration' },
								{ label: 'Statement control', slug: 'guides/statement-control' },
								{ label: 'Instrumentation and audit log', slug: 'guides/instrumentation-and-audit' },
								{ label: 'Prometheus metrics', slug: 'guides/metrics' },
								{ label: 'Docker and Kubernetes', slug: 'guides/docker-and-kubernetes' },
								{ label: 'Behind a load balancer', slug: 'guides/load-balancers' },
								{ label: 'Raspberry Pi', slug: 'guides/raspberry-pi' },
								{ label: 'Upgrading', slug: 'guides/upgrading' },
							],
						},
					],
				},
				{
					label: 'Clients',
					items: [
						{ label: 'Python (ADBC)', slug: 'clients/python' },
						{ label: 'Go (ADBC)', slug: 'clients/go' },
						{ label: 'C, C++, R, Rust (ADBC)', slug: 'clients/adbc-driver-manager' },
						{ label: 'Java (JDBC) and DBeaver', slug: 'clients/jdbc' },
						{ label: 'JavaScript', slug: 'clients/javascript' },
						{ label: 'The hardcharger CLI', slug: 'clients/cli' },
						{ label: 'Plain HTTP', slug: 'clients/http' },
					],
				},
				{
					label: 'Reference',
					items: [
						{ label: 'Server configuration', slug: 'reference/configuration' },
						{ label: 'SQL functions and settings', slug: 'reference/sql' },
						{ label: 'Error codes', slug: 'reference/errors' },
						{ label: 'CLI reference', slug: 'reference/cli' },
						{ label: 'Chargewire protocol', slug: 'reference/chargewire-protocol' },
						{ label: 'Release notes', slug: 'reference/release-notes' },
						{ label: 'Versions', slug: 'reference/versions' },
					],
				},
				{ label: 'Benchmarks', slug: 'benchmarks' },
			],
		}),
	],
});
