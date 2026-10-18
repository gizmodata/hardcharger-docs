# Changelog

All notable changes to the Hardcharger documentation are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Hardcharger integration/batch-1 (eb289605; lands with it): `CREATE VIEW` needs `SELECT` on what
  the view reads (tested refusal), views made by a `catalog_access` token get no owner, a statement
  that has failed when the server answers is an error response (never `200` with a `failed`
  document), lingering close (a resent upload's answer arrives), and CORS with credentials for
  cross-origin certificate sign-in (`cors_origins` plus `--mtls-require-client-cert=false`, tested).
  Reference regenerated from that build and its warp-sql (4c88fd0).
- Hardcharger™ and GizmoData™ (pending trademarks; ™, never ®): the site title and header
  wordmark, the home page hero, banner and social card, the first prose mention on every page
  (`src/middleware.ts`; never in code, CLI output or headings), each page's `<title>` and
  description metadata (Starlight route middleware), the "by GizmoData" links, and a footer line:
  "Hardcharger™ and GizmoData™ are trademarks of GizmoData LLC."
- TLS guide: certificate sign-in, tested end to end in Python, the CLI, Java and curl: the
  `client_certificate` grant, `--mtls-certificate-sign-in`, `--mtls-admin-identities`, the e-mail
  SAN default and how identities match (URI identities exactly, e-mail and CN ignoring ASCII case),
  certificate-bound tokens (`certificate_mismatch`), CRLs (a revoked certificate refused at the
  handshake, reloads, `nextUpdate`), audit records and rate limits.
- Users, roles and grants: certificate users under access control (`CREATE USER "joe@example.com"`,
  no password), and "What users can see": metadata follows privileges table by table, `DESCRIBE`
  of a table without a privilege (or with only some columns) is refused.
- SQL reference: HUGEINT and UHUGEINT values past 38 digits fail with a conversion error; `CAST` to
  `VARCHAR`, or `SET SESSION arrow_lossless_conversion = true` and decode the 16-byte values.
- Error codes: the certificate codes, `unsupported_grant_type`, the partitioned-upload codes, and
  the `session_ended` reasons, with a tested example of when a client sees `invalid_token` and when
  `session_ended`.
- Statement control: a stop during an upload aborts it and rolls it back.
- `rbac_mtls` example profile, and a certificate with an e-mail SAN in the test certificates.

### Changed

- The CLI uses TLS by default (Hardcharger feat/cli-tls-default): every CLI example against a
  plain-HTTP server says `--tls=false`; the CLI page shows the hint a TLS connection to a
  plain-HTTP server prints, and its option table, the GizmoSQL mapping and the Docker guide say
  what changed. Merge after that branch reaches Hardcharger's main (the examples run against
  `:main`, whose client doesn't take `--tls=false` yet).
- The CLI page's URI row follows the client's new URIs (Hardcharger fix/cli-uri-tls): the ADBC
  driver's `hardcharger://HOST[:PORT][/PREFIX][?tls=false]`, HTTPS unless `?tls=false`, with the
  user and the other settings as flags; `.connect URI [USER [PASSWORD]]`.
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
- The docs follow Hardcharger's main (5178d26) and warp-sql's (982a58c): the reference lists the
  seven `mtls_*` options and `--auth-type mtls`; the drivers read results in 8 partitions and send
  large loads in 8 parts by default (Python, JDBC); Linux builds after 0.2.0 need glibc 2.28;
  DuckLake, PostgreSQL and S3 are built in (no `INSTALL`); a restricted administrator reads none of
  the server's own catalogs. The versions page lists what `main` has and 0.2.0 doesn't.
- Coming from GizmoSQL: access control is described as new in Hardcharger (no store or options to
  migrate).
- CI: the Maven cache is keyed on the cloned JDBC poms (`actions/cache`; setup-java searched only the
  workspace), and the examples get setup-go's Go, Node and Java on their PATH (they had the runner
  image's older Go, which can't build the driver's module).
- `scripts/verify-in-docker.sh` works from a git worktree.
- release: a run waits for the one before it instead of cancelling it (a deploy is never cut
  off), and docs.yml's concurrency group no longer equals release's when release calls it (a
  called workflow sharing its caller's group deadlocks). The README says the preview appears
  after the first successful release run.
- 156 runnable examples.

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
