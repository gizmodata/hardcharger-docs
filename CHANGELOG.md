# Changelog

All notable changes to the Hardcharger documentation are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
