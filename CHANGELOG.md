# Changelog

All notable changes to the Hardcharger documentation are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Desktop guide covers copyable connection examples, TLS detection, client credentials
  and CA certificates, plus the About screen's documentation link.
- v2.1.0+ desktop app guide, package selection in the quickstart, and SQL Editor guides
  for SQL Monitor and Server Configuration, linked from the home page and sidebar.
- Desktop dashboard design-preview screenshots and real SQL Monitor / Server Configuration
  captures from temporary servers with synthetic data, in light and dark themes.

### Changed

- Document v2.1.0+ native runtime extensions, automatic installation/loading matching
  GizmoSQL, custom repositories, offline caches, iOS built-ins and upstream DuckLake
  metadata-format behavior. Record Python/server version alignment and `.postN` fixes.

- Retire the pre-2.0 ban on version-availability notes so readers can distinguish v2.1.0+
  features from their installed 2.0 server. No generated reference pages are changed.

## [2.0.1] - 2026-10-22

### Fixed

- Document the published `@gizmodata/hardcharger` npm package, its installation and Node.js
  requirement, and remove the JavaScript preview labels and source-build instructions.
- Use the Hardcharger JavaScript driver for the first-query example, including session cleanup.
- Run JavaScript examples against the npm package pinned in the lockfile instead of building
  unpublished driver tarballs in CI.

## [2.0.0] - 2026-10-21

- Refresh every Web UI screenshot from the signed 2.0.0 release test artifacts, including sign-in, SQL results, saved queries, API requests and Excel uploads.

### Fixed

- Match the CLI's current TLS hint and explain that password credentials cannot inspect a
  scoped token's expired session because the credentials have different authority.

### Added

- **GA preparation.** One switch, `DOCS_GA` (`src/components/ga.ts`), chooses between the private
  preview and the public site: with it there is no preview banner or `noindex`, the `<Preview>`
  MDX blocks are left out and the `<Ga>` blocks shown (the quickstart's installer, image, binaries
  and `pip install hardcharger` without a token, the Python and Go drivers from PyPI and the Go
  proxy, the JDBC jar from the release, the JavaScript client's note without "internal", the
  Raspberry Pi guide, and the Versions page and the header badge saying 2.0.0 instead of
  2.0.0-rc.1 from main), `scripts/verify_examples.py` runs the tested blocks of the side that is
  built, and lychee checks `github.com/gizmodata/` links. `public/CNAME` names
  `docs.hardcharger.gizmodata.com`, whose DNS points at GitHub Pages. Both workflows read the
  repository variable `DOCS_GA` (`DOCS_INDEXABLE` is gone); **docs** also takes it as the `ga`
  input of a run started by hand, builds the public site on every push and fails if anything of
  the preview is left in it (`scripts/check_ga_build.py`, which fails on a preview build). The
  README's GA checklist has the flip-day steps. Merged: `docs/web-ui-parity`, `docs/ui-upload`,
  `docs/tpch-fair-use` and `docs/home-sidebar`.

### Changed

- Document connection profiles and their driver manifest, Python 3.11 minimum, and the native
  library build. Test examples with the 2.0 driver on main instead of the old internal RC pin.
- Refresh release notes from the tested f43b705 server, including ADBC images and Web UI fixes.
- Regenerated the reference from the Hardcharger 2.0.0 candidate and Warp SQL 1.0.1:
  configuration and CLI help, SQL functions, metrics, protocol and release notes.
- Hardcharger 2.0.0-rc.1 (main feaa5d39, warp-sql e38b28e): the reference is regenerated from the
  `:main` image (2.0.0-rc.1): the release notes' `[2.0.0-rc.1]` section, the Warp SQL 1.0.0
  specification, the CLI's `--licenses`, the sensitive-path and instrumentation options' new
  wording, and the access-control introspection functions (`hardcharger_grants()`,
  `hardcharger_role_members()`, `hardcharger_roles()`, `hardcharger_users()`,
  `hardcharger_policies()`, `hardcharger_effective_privileges()`), each described in the SQL
  reference. The docs that rc.1 made wrong are corrected, each checked against an rc.1 server:
  the browser sign-in, Warp SQL 1.0, API page, instrumentation id and sensitive-path guard pages
  (from `docs/oauth-in-protocol`, `spec/v1.0`, `docs/ui-api-page`, `docs/instrumentation-ids` and
  `docs/sensitive-paths-fs-layer`) and the no-version-history check (`docs/no-version-history`)
  are merged; instrumentation no longer goes to DuckLake (a DuckLake `instrumentation_catalog`
  stops the server; the DuckLake guide keeps catalog logs only); `HARDCHARGER_CURRENT_SESSION()`
  is the `s_...` session id; discovery lists `openapi`; a blocked file read is a DuckDB
  `Permission Error` with the statement's position; `.tables` lists
  `hardcharger_information_schema`; a statement that meets a killed session says it wasn't run
  again; the Versions page names 2.0.0-rc.1 and release candidates. Access control: "Seeing
  grants" shows the introspection functions and the SQL standard's privilege views, with a tested
  `hardcharger_effective_privileges()` example. CI builds the Python driver from the release that
  speaks Warp SQL 1.0 (`internal-0.1.0rc1`), since hardcharger-adbc main still commits a
  partitioned ingest the draft way.
- Instrumentation: the records are written in the background, in batches, so they appear a moment
  after a statement ends; the guide says so, and its examples (and statement control's query-tag
  example) wait for their row before reading it. Release run 39454484457 read
  `execution_details` before the row was there.
- The Hardcharger™ logo: the header shows the bull-head lockup (light and dark versions, it
  replaces the title text), the favicon is the bull head (SVG, with an ICO and an Apple touch
  icon), and the social card is the brand kit's 1200x630 share image. `scripts/brand_images.mjs`,
  which drew the old favicon and card, is gone. The GizmoData™ logo stays in the footer.
- The hero banners (the home page, Python and Go, JDBC, JavaScript, the CLI, and the README's)
  show the full charging bull in place of GizmoData's hexagon mark, with the same text and
  layout: the brand kit's mascot, cropped, 480 px wide, as WebP
  (`src/assets/brand/hardcharger-mascot.webp`), which `scripts/banner.py` now draws too. The
  Warp SQL banners keep GizmoData's mark.
- Browser sign-in is part of Warp SQL now (`oauth_browser`, on the server's own port): the SSO
  guide describes the new flow (create a flow, sign in in the browser, collect the token once
  with the poll secret; PKCE, state and nonce with the provider), says plainly that operators
  must re-register the redirect URI as `<oauth_base_url>/warp/v1/auth/oauth/callback`, and drops
  the separate port (31339), `oauth_port`, `oauth_disable_tls`, the `/oauth/...` routes and the
  CLI's `--oauth-port`/`--oauth-base-url` (`HARDCHARGER_OAUTH_PORT`, `HARDCHARGER_OAUTH_BASE_URL`).
  New options `oauth_provider_name` and `oauth_max_flows`; `oauth_base_url` is the server's public
  URL. The tested example checks discovery (`auth.oauth_browser`) and a new flow's authorize URL.
  The web UI page shows its "Sign in with ..." button, the JDBC page `authType=oauth_browser`
  (alias `external`), the error reference `flow_not_found`, `invalid_return_to` and a failed
  sign-in's codes, and the migration page the removed 1.x options. The configuration reference's
  browser sign-in group, the CLI help and the protocol page's §3.1, §4.3, §9.7 and §11 are
  regenerated from the new server and spec.
- No version history in the docs: "New in" notes, "from 0.3.0" and "0.2.0 has" asides are gone, the Versions page says which version the docs describe and how versions work, and CI fails on such phrasing (`scripts/check_no_version_history.py`; the release notes are exempt).

### Added

- Web UI guide: **The API page** (the server's Warp SQL API in Swagger UI; Try it out runs as
  the signed-in user, sends the token to the page's own origin only, offers Arrow answers as a
  download), with a dark screenshot, and the CSP table's reasons now name Swagger UI. Warp SQL
  page: **The API description** (`GET /warp/v1/openapi.json`, OpenAPI 3.1, listed in discovery
  as capability `openapi` and `links.openapi`), with a tested example.
- Instrumentation guide: **Statement and execution ids**, how `sql_statements` and
  `sql_executions` key rows by the Warp SQL ids clients hold (`q_...` for a statement and its
  execution, `q_....N` for the statements of a one-request script, `p_...` for a prepared
  statement with an execution per request), the same ids in the query log, and what startup
  says about a table with UUID ids; with a tested example (a statement found by the id
  `hardcharger_active_connections()` shows). Coming from GizmoSQL: the UUID columns' row
  (hardcharger `feat/instrumentation-warp-ids`).
- Web UI guide, the editor's full behavior (Hardcharger feat/ui-portal-parity): tabs with their
  own sessions, Run all, transactions, the grid, the schema browser and autocomplete, saved
  queries, Run as, every download format, resizing, the help, phone-sized screens; a section on
  sessions and transactions (the session idle timeout, tested: `--session-idle-timeout 3600`
  shows as the session document's `idle_timeout_s`) and a table of what the page keeps in the
  browser. Fresh screenshots (the editor with tabs and a selection, saved queries with the
  Download menu). The page's 18 examples pass against a server that embeds the UI (main
  7a8c72f8); a changed expected value fails, as it should.
- Web UI: **Upload data** (hardcharger `feat/ui-upload`): what it reads (CSV, TSV, Excel
  .xlsx/.xls/.xlsb, Parquet, JSON lines and arrays, Arrow IPC) and which formats stream or are read
  whole (with their limits), the dialog's fields and its create / append (columns matched by name) /
  replace modes, CSV and Excel detection (delimiter, header row, encodings, the 1904 date system,
  formulas' saved values, error cells, empty rows, merged ranges), **Preview & column types**, the
  one-transaction upload (cancel and failures leave the table unchanged), the privileges it needs
  under access control, and a dark-theme screenshot. The Content-Security-Policy section names the
  upload's worker and Parquet reader. The page no longer says which release brought the UI.
- Hardcharger 0.3.0 (main 5983a6a, warp-sql a8d762a): the reference is regenerated from the
  `:main` image (`sha-5983a6a`), and the release notes show the `[0.3.0]` section. New:
  - Error codes: `invalid_token` reasons (`token_expired`, `token_revoked`, `credentials_changed`,
    `principal_dropped`; none for a token the server can't verify as its own), `token_revoked` among
    the `session_ended` reasons, and a scoped token's session ending when the token expires, with
    tested examples (a dropped scoped token, a forged signature, an expired scoped token).
  - The CLI page: what the client prints when the server stops accepting its sign-in (tested with a
    password changed mid-script) and when an administrator ends its session (tested with
    `KILL SESSION`: a new session, the statement that met the kill fails).
  - TLS guide: the CLI's messages for a revoked client certificate and for a server that requires
    one (both tested).
  - Plain HTTP: preparing never runs the statement, and a prepared `INSERT … RETURNING` describes its
    rows (tested: the schema, and no row written).
  - SQL reference: the CLI prints HUGEINT/UHUGEINT exactly with `SET SESSION
    arrow_lossless_conversion = true` (tested).
  - Quickstart: the Windows zips and MSIs (the PowerShell lines hardcharger's Windows CI runs).
  - Versions: the docs describe 0.3.0, and the page lists what 0.3.0 has and 0.2.0 doesn't; "the
    release after 0.2.0" is 0.3.0 everywhere (CLI, TLS, Docker, Raspberry Pi, quickstart, upgrading).
- Hardcharger integration/batch-1 (eb289605): `CREATE VIEW` needs `SELECT` on what
  the view reads (tested refusal), views made by a `catalog_access` token get no owner, a statement
  that has failed when the server answers is an error response (never `200` with a `failed`
  document), lingering close (a resent upload's answer arrives), and CORS with credentials for
  cross-origin certificate sign-in (`cors_origins` plus `--mtls-require-client-cert=false`, tested).
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
- Users, roles and grants: a DuckDB file as the access-control store, for development or a server
  that will only ever run one replica (PostgreSQL for production and for several replicas), with
  tested examples (the administrator refused reading it, a second server on the file stopped) and
  the `rbac_duckdb` example profile. Security model: the server's own files (the store, the
  database, instrumentation and log files) out of reach of SQL for everyone, and the one limit: an
  extension with file I/O of its own, such as `sqlite_scanner`, is refused only a path written out
  in the statement (a computed one finds no SQLite database). Configuration reference regenerated
  (`rbac_store_uri`).
- Web UI (`guides/web-ui`): the server's built-in browser UI at `/ui` (`--web-ui`,
  `HARDCHARGER_WEB_UI`, `web_ui: true`), how it signs in, and how it behaves with TLS, mutual
  TLS and certificate sign-in, its Content-Security-Policy, and access control. Linked from the
  sidebar and the landing page, with screenshots; its 16 examples run against the `:main` image,
  which embeds the UI.

### Changed

- Warp SQL 1.0.0 (warp-sql spec/v1.0, a828247, on the browser sign-in spec; outputs captured from
  a Hardcharger server built from its spec/v1.0, b4c813b2): the protocol page is the 1.0.0
  specification in full, §4.3 included (its description no longer says draft), and the rest of
  the reference is regenerated from that server and its CHANGELOG (the release notes' Unreleased
  section, `result_retention_seconds`, the metrics options' descriptions, the introspection
  functions). Plain HTTP: discovery without `result_retention` (retention is core) and with
  `ipc_compression_lz4_frame`; the session document's `duckdb_arrow_lossless_conversion` (was
  `arrow_lossless_conversion`; DuckDB's SQL setting keeps its name) and `transaction`; a bad option
  fails `POST /sessions`; new tested sections for `PATCH` (every option plus `errors`), a statement
  cancelled by its timeout while the submission waits (`409 statement_timeout`), and server-info's
  keys (`server_read_only`, `duckdb_version`, `hardcharger_instance_id`,
  `hardcharger_access_control`). Bulk ingest: the commit takes `{"part_count": n}`, and the ingest
  document (tested). Error codes: `certificate_required`, `statement_not_found` for a forgotten
  statement, `partition_not_found`, `not_found` for endpoints only, `statement_cancelled` and
  `statement_timeout` at `409`, `execution_error` at `422`, `internal_error` at `500`, the
  cancelled-at-submit problem document, codes clients make up (`client_*`), unknown codes by status,
  and which `invalid_token`/`session_ended` reasons a client signs in again after. Warp SQL in one
  page: `retained` (a server may decline), both split-result headers, `result_locations`, and the
  error statuses. Statement control: `Warp-Query-Tag`'s ASCII and 4,096-byte rule (tested).
- Security model: the sensitive-path guard as Hardcharger 2.0.0-rc.1 has it (hardcharger branch
  `fix/sensitive-paths-in-fs-layer`): checked in DuckDB's file system, so computed paths,
  `query('…')`, macros, views and prepared parameters are covered and literals are no longer
  refused; globs from above leave protected matches out; the sqlite_scanner plan-time check; and
  the two limits (startup and init SQL, `postgres_scanner`'s libpq). The configuration reference's
  new `block_sensitive_paths` / `sensitive_paths` wording comes with the next regeneration.
- The home page shows the sidebar (the table of contents) and "On this page", like every other page,
  and on a phone the menu button: it used Starlight's `splash` template, which has neither, so the
  contents appeared only after opening a section.
- Benchmark results follow the TPC's fair-use policy: the runs are described as derived from
  TPC-H ("the 22 queries derived from TPC-H, SF10", "TPC-H-derived data"), never as TPC-H
  results. The benchmarks page says how the runs deviate from the specification and carries the
  disclaimer (derived from the TPC-H benchmark, not an official TPC-H result and not comparable
  to published TPC-H results; TPC-H™ a trademark of the Transaction Processing Performance
  Council), as do the home page under its results table and the performance model and bulk
  ingest pages (a footnote). The benchmarks page's SF10 section is now "Queries derived from
  TPC-H at SF10, on one machine". The release notes follow when they are regenerated from
  hardcharger's changelog, which has the same change.
- The CLI uses TLS by default (Hardcharger feat/cli-tls-default): every CLI example against a
  plain-HTTP server says `--tls=false`; the CLI page shows the hint a TLS connection to a
  plain-HTTP server prints, and its option table, the GizmoSQL mapping and the Docker guide say
  what changed. The DuckDB-store and `CREATE VIEW` examples, written before it, say `--tls=false`
  too.
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
- 184 runnable examples (all passing locally against `ghcr.io/gizmodata/hardcharger:main` at sha-5983a6a).

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
