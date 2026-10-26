<p align="center">
  <a href="https://gizmodata.com">
    <img src="src/assets/banners/hardcharger-docs-banner.svg" alt="Hardcharger Docs by GizmoData" width="100%">
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/status-GA%20ready-f15a24.svg" alt="GA ready">
  <img src="https://img.shields.io/badge/built%20with-Astro%20Starlight-31a8db.svg?logo=astro&logoColor=white" alt="Astro Starlight">
  <img src="https://img.shields.io/badge/examples-run%20in%20CI-brightgreen.svg" alt="Every example runs in CI">
  <a href="https://github.com/gizmodata/hardcharger"><img src="https://img.shields.io/badge/docs%20for-Hardcharger-f15a24.svg" alt="Hardcharger"></a>
  <a href="https://gizmodata.com"><img src="https://img.shields.io/badge/by-GizmoData-31a8db.svg" alt="GizmoData"></a>
</p>

<h3 align="center">The documentation for Hardcharger, GizmoData's DuckDB 2.0 server on Warp SQL.</h3>

---

## 🔒 Private preview and GA

The same source builds two sites, chosen by **one switch, `DOCS_GA`** (`src/components/ga.ts`):

| | Private preview (`DOCS_GA` unset) | Public site (`DOCS_GA=true`) |
|---|---|---|
| Address | <https://curly-adventure-gke7ezg.pages.github.io/> (GitHub Pages, visible to the gizmodata organization only) | <https://docs.hardcharger.gizmodata.com/> (`public/CNAME`, DNS already points there) |
| Banner, `noindex` | on every page | none |
| Content | `<Preview>` blocks (tokens, internal packages) | `<Ga>` blocks (`pip install hardcharger`, the release jar, "version 2.0.0") |
| Examples | the tested blocks inside `<Preview>` | the tested blocks inside `<Ga>` (`scripts/verify_examples.py`) |
| External links | `github.com/gizmodata/` left out (also in a dry run with the **ga** input: the repositories are private until the flip) | checked |

`<Preview>` and `<Ga>` are the MDX components in `src/components/`. Every push builds both
variants and `scripts/check_ga_build.py` fails the **docs** workflow if the public build still
carries anything of the preview. A run started by hand with the **ga** input tests the public
site end to end (examples included) without flipping anything.

**The flip, when Hardcharger is public:** set the repository variable `DOCS_GA` to `true`
(`gh variable set DOCS_GA --body true --repo gizmodata/hardcharger-docs`), then the Pages custom
domain (below) and a **release** run. Both workflows read the variable; nothing else changes.

The site is deployed by a release tag (`vX.Y.Z`) or by running **release** by hand on `main`,
after every check passes. Or locally: download the `site` artifact of any **docs** run, or build it
yourself:

```bash
npm ci
npm run build && npm run preview     # http://localhost:4321, the preview
DOCS_GA=true npm run build           # the public site, in dist/
npm run dev                          # live reload while writing
```

## 📚 What's inside

| Section | Pages |
|---|---|
| Get started | quickstart, desktop app (v2.1.0+), web UI, your first query (Python, Go, Java, JavaScript, CLI, curl), coming from GizmoSQL |
| Concepts | Warp SQL in one page, security model, performance model |
| Guides | TLS and mTLS; users, roles and grants; row policies, masking, tenants, scoped tokens; catalog access rules; SSO; DuckLake and S3; bulk ingest; configuration; SQL Monitor and Server Configuration (v2.1.0+); statement control; instrumentation and the audit log; Prometheus metrics; Docker and Kubernetes; load balancers; Raspberry Pi; upgrading |
| Clients | Python, Go, C/C++/R/Rust, JDBC and DBeaver, JavaScript (`@gizmodata/hardcharger` on npm), the `hardcharger` CLI, plain HTTP |
| Reference | server configuration, SQL functions and settings, error codes, CLI, the Warp SQL protocol, release notes, versions |
| Benchmarks | method, every number, and where Hardcharger still loses |

Built with [Astro Starlight](https://starlight.astro.build): static output, Pagefind search,
tabs per language, copy buttons, dark and light themes, an edit link on every page, a sitemap,
`llms.txt`, and per-page descriptions and Open Graph tags. Mermaid diagrams render in the browser.

## ✅ Every example runs

A fenced code block whose info string contains `test` is an example CI runs against a real
`hardcharger-server` built from Hardcharger's `main` branch:

````markdown
```python test
from adbc_driver_hardcharger import dbapi as hardcharger
...
```

```text output
[{'answer': 42}]
```
````

[`scripts/verify_examples.py`](scripts/verify_examples.py) extracts them page by page and runs
them in order in a fresh directory and environment (nothing from your shell, credentials
included, reaches an example): Python, Go (fetching the real modules), Java (against the
standalone JDBC jar), Node.js, SQL through the CLI, bash, `console` transcripts (each `$ command`
and its expected output), interactive CLI sessions (driven through a pseudo-terminal), YAML
server configs, and files checked by a command (Kubernetes manifests with kubeconform, an nginx
config by proxying a real 8 MiB upload through it). An `output` block after a tested block is its
expected output; `…` matches any text. Options in the info string pick the server
(`profile=rbac`, `server=self`, `fresh`), the expected exit status, background processes and
their cleanup; the docstring lists them. [`tests/profiles.yaml`](tests/profiles.yaml) defines the
servers (PostgreSQL for access control, TLS, metrics, a stand-in identity provider, ...).

Missing prerequisites (the server, PostgreSQL, the drivers, the read token) **fail** the run;
nothing is skipped, and a run in which no example ran fails too. Each gate was proven by breaking
it: a wrong expected output, no server, a drifted reference, a broken internal link, a broken
external link, and an empty run all exit non-zero.

```bash
export HARDCHARGER_DOCS_BIN_DIR=/path/to/hardcharger/server/build   # hardcharger-server + hardcharger
export HARDCHARGER_DOCS_JDBC_JAR=/path/to/hardcharger-jdbc.jar
export HARDCHARGER_DOCS_PG_URI=postgresql://hardcharger:hardcharger@127.0.0.1:55450/postgres
.venv/bin/python scripts/verify_examples.py [--page guides/tls]
```

The examples use the documented ports (31337, 31338, 9091, ...). On a machine where something
else holds them, [`scripts/verify-in-docker.sh`](scripts/verify-in-docker.sh) runs the same
examples in a Linux container (it needs a `hardcharger-linux-<arch>` build, a hardcharger-adbc
checkout and the JDBC jar).

## 🔁 The reference can't drift

[`scripts/gen_reference.py`](scripts/gen_reference.py) builds the reference from the software
itself: the configuration page from `hardcharger-server --print-options-json` (added in
gizmodata/hardcharger#1), the SQL settings and functions from `hardcharger_settings()` and
`duckdb_functions()` on a running server, the metrics table from a live `/metrics`, the CLI
reference from `hardcharger --help` and `.help`, the release notes from Hardcharger's
`CHANGELOG.md`, and the protocol page from `warp-sql/spec/warp-sql.md`. CI runs it with `--check`
and fails when anything committed differs from what the server says.

## ⚙️ CI

| Workflow | When | What |
|---|---|---|
| [docs](.github/workflows/docs.yml) | every push and pull request; called by release | build (internal links), external links (lychee), Chromium and WebKit in light and dark at desktop and phone width (console errors, sideways scrolling), every example, the reference check |
| [release](.github/workflows/release.yml) | `vX.Y.Z` tags, or by hand | docs on the tagged commit, then a GitHub Release with the CHANGELOG section and the built site, and the GitHub Pages deployment (the preview, or the public site when `DOCS_GA` is true) |

While Hardcharger is internal, CI uses no personal token:

1. **The image**, `ghcr.io/gizmodata/hardcharger:main` (the server and the CLI) and `:latest`
   (the Docker examples), pulled with the workflow's `GITHUB_TOKEN`. The package must grant this
   repository read access (package settings, **Manage Actions access**).
2. **Read-only deploy keys**, one per internal repository, stored here as secrets:
   `DEPLOY_KEY_HARDCHARGER`, `DEPLOY_KEY_WARP_SQL`, `DEPLOY_KEY_HARDCHARGER_ADBC`,
   `DEPLOY_KEY_WARP_SQL_ADBC`, `DEPLOY_KEY_HARDCHARGER_JDBC`, `DEPLOY_KEY_WARP_SQL_JDBC`.
   Each source repository has the matching public key as a read-only deploy key titled
   "hardcharger-docs CI (read-only)". The JavaScript driver is installed from npm.
3. **No release downloads.** Examples that download a release (the installer, tarballs, the
   Python package's server) run against a release mirror made from the `:main` image, with the
   real installer script and the real package.

Without the image or a key, the examples job fails; it never skips.

## ✍️ Writing

Short sentences, task first, no marketing in guides, and nothing that isn't true and tested.
Python examples use keyword arguments. Don't name competing products, customers or internal
documents. Every page has a `description` (it is the page's search and social summary). New
pages go in the sidebar in [`astro.config.mjs`](astro.config.mjs). Brand assets:
[`scripts/banner.py`](scripts/banner.py) draws README-style banners with the charging bull
(`src/assets/brand/hardcharger-mascot.webp`). The header logo
(`src/assets/brand/`), the favicons, `public/apple-touch-icon.png` and the social card
(`public/og.png`) are files from the Hardcharger™ brand kit (`docs/assets/brand/` in the
hardcharger repository), losslessly optimized, not drawn here.

## 🚀 GA checklist

Done, ready for the flip:

- [x] DNS: `docs.hardcharger.gizmodata.com` is a `CNAME` to `gizmodata.github.io`
      (gizmodata-infrastructure-terraform `aws/dns/gizmodata_com.tf`, applied 2026-10-20), and
      gizmodata.com is a verified GitHub Pages domain of the organization.
- [x] `public/CNAME`, the `DOCS_GA` switch, and the GA build checked on every push.

At the flip (the repository public, Hardcharger 2.0.0 released):

- [ ] `gh variable set DOCS_GA --body true --repo gizmodata/hardcharger-docs`.
- [ ] Pages custom domain: `gh api -X PUT repos/gizmodata/hardcharger-docs/pages -f cname=docs.hardcharger.gizmodata.com`
      (Settings → Pages → Custom domain). Wait for the DNS check and the certificate
      (`gh api repos/gizmodata/hardcharger-docs/pages --jq '.https_certificate.state'` says
      `approved`), then `gh api -X PUT repos/gizmodata/hardcharger-docs/pages -F https_enforced=true`.
- [ ] Pin `HARDCHARGER_IMAGE` in `docs.yml` to the release (`ghcr.io/gizmodata/hardcharger:2.0.0`),
      regenerate the reference from it (`scripts/gen_reference.py`: the `[2.0.0]` release notes, the
      Warp SQL 1.0.1 protocol page, the CLI and configuration pages) and move
      `HARDCHARGER_ADBC_REF` to `main` once the driver's main speaks Warp SQL 1.0.
- [x] Retire the pre-2.0 version-history check; guides now label features by their first version.
- [ ] Run **release** (a `vX.Y.Z` tag or by hand) and open every page on the live domain in
      Chromium and WebKit (CSP violations included); then link the docs from the READMEs,
      gizmodata.com and the CLI's `.about`.
- [ ] Search Console: add the domain and submit `sitemap-index.xml`.
- [ ] Versioned docs: archive the launch version with
      [starlight-versions](https://github.com/HiDeoo/starlight-versions) and replace the header
      badge with its picker.

## 📄 License

Apache License 2.0, like Hardcharger.

---

<p align="center">
  <a href="https://gizmodata.com"><img src="src/assets/gizmodata-logo.png" alt="GizmoData" width="56"></a><br>
  <sub>Built by <a href="https://gizmodata.com">GizmoData</a></sub>
</p>

---

<p align="center"><sub>Hardcharger™ and GizmoData™ are trademarks of GizmoData LLC.</sub></p>
