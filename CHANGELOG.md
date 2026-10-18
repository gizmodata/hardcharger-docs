# Changelog

All notable changes to the Hardcharger documentation are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- The JavaScript page (and the landing page's client card) use `@gizmodata/hardcharger`
  (gizmodata/hardcharger-js): `import { connect } from '@gizmodata/hardcharger'` with
  `hardcharger://` URLs, a URL table, and `authType: 'client_certificate'` (or `'mtls'`);
  `@gizmodata/warp-sql` stays named as the generic client for any Warp SQL server. CI builds
  hardcharger-js on the warp-sql-js tarball it already builds (new secret
  `DEPLOY_KEY_HARDCHARGER_JS`, a read-only deploy key of gizmodata/hardcharger-js) and runs the
  page's examples with it.
- CI uses no personal token: the server and the CLI come from `ghcr.io/gizmodata/hardcharger:main`
  (pulled with `GITHUB_TOKEN`), and the internal repositories are read with one read-only deploy
  key each (`DEPLOY_KEY_*` secrets). Examples that download a release run against a release
  mirror made from that image, with the real installer and the real Python package.
- The docs follow Hardcharger's main (bced775): the version reads `0.2.0` everywhere,
  `max_queued_statements` reports `-1`, the CLI keeps color to terminals (and honours `NO_COLOR`),
  shows the server's reason for a refused sign-in and takes comments anywhere in a script, the
  Python driver raises DB-API's own exception classes, the CLI reads large results in 8
  partitions by default, and partitioned uploads (Warp SQL §8.3) are documented and run over
  plain HTTP. Benchmarks and the landing page carry the new load numbers.
- Output comparisons are exact again (no color codes are stripped outside the interactive
  shell), and `console` commands may span lines with open quotes or loops.
- 136 runnable examples.

## [0.1.0] - 2026-10-17

The first private preview of the Hardcharger documentation.

### Added

- 37 pages on Astro Starlight: get started (quickstart, a first query in six languages, coming
  from GizmoSQL), concepts (Warp SQL, security model, performance model), 18 guides, 7 client
  pages, the reference and the benchmarks.
- GizmoData branding: the README banners' dark card, the hex logo, the orange-to-blue gradient,
  a "Built by GizmoData" footer, and a private-preview banner with `noindex`.
- 134 runnable examples, each run in CI against a real hardcharger-server from Hardcharger's main
  branch with the real clients (`scripts/verify_examples.py`); missing prerequisites fail the run.
- A reference generated from the server and its repositories (`scripts/gen_reference.py`): server
  options, SQL settings and functions, metrics, CLI help, release notes, the Warp SQL spec. CI
  fails when it drifts.
- Link checks (internal at build time, external with lychee), and a Chromium and WebKit check of
  every page in light and dark mode at desktop and phone width.
- CI (`docs.yml`) and a release workflow that deploys the private GitHub Pages preview after
  every check passes on the tagged commit.
