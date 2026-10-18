<p align="center">
  <a href="https://gizmodata.com">
    <img src="src/assets/banners/hardcharger-docs-banner.svg" alt="Hardcharger Docs by GizmoData" width="100%">
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/status-private%20preview-f15a24.svg" alt="Private preview">
  <img src="https://img.shields.io/badge/built%20with-Astro%20Starlight-31a8db.svg?logo=astro&logoColor=white" alt="Astro Starlight">
  <img src="https://img.shields.io/badge/examples-run%20in%20CI-brightgreen.svg" alt="Every example runs in CI">
  <a href="https://github.com/gizmodata/hardcharger"><img src="https://img.shields.io/badge/docs%20for-Hardcharger-f15a24.svg" alt="Hardcharger"></a>
  <a href="https://gizmodata.com"><img src="https://img.shields.io/badge/by-GizmoData-31a8db.svg" alt="GizmoData"></a>
</p>

<h3 align="center">The documentation for Hardcharger, GizmoData's DuckDB 2.0 server on Warp SQL.</h3>

---

## 🔒 Status: private preview

These docs are internal to GizmoData until Hardcharger launches. Their future home is
`https://docs.hardcharger.gizmodata.com`; nothing is published there yet. Until launch:

- **Preview:** <https://curly-adventure-gke7ezg.pages.github.io/> (GitHub Pages with private
  visibility: only members of the gizmodata organization can open it). It is deployed by a
  release tag (`vX.Y.Z`) or by running **release** by hand on `main`, after every check passes.
  **The preview appears after the first successful release run;** until then the link answers 404.
- **Or locally:** download the `site` artifact of any **docs** run, or build it yourself:

  ```bash
  npm ci
  npm run build && npm run preview     # http://localhost:4321
  npm run dev                          # live reload while writing
  ```

Every page shows a "Private preview" banner and tells search engines not to index it until
`DOCS_INDEXABLE=true`.

## 📚 What's inside

| Section | Pages |
|---|---|
| Get started | quickstart, your first query (Python, Go, Java, JavaScript, CLI, curl), coming from GizmoSQL |
| Concepts | Warp SQL in one page, security model, performance model |
| Guides | TLS and mTLS; users, roles and grants; row policies, masking, tenants, scoped tokens; catalog access rules; SSO; DuckLake and S3; bulk ingest; configuration; statement control; instrumentation and the audit log; Prometheus metrics; Docker and Kubernetes; load balancers; Raspberry Pi; upgrading |
| Clients | Python, Go, C/C++/R/Rust, JDBC and DBeaver, JavaScript (preview), the `hardcharger` CLI, plain HTTP |
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
| [release](.github/workflows/release.yml) | `vX.Y.Z` tags, or by hand | docs on the tagged commit, then a GitHub Release with the CHANGELOG section and the built site, and the GitHub Pages deployment |

While Hardcharger is internal, CI uses no personal token:

1. **The image**, `ghcr.io/gizmodata/hardcharger:main` (the server and the CLI) and `:latest`
   (the Docker examples), pulled with the workflow's `GITHUB_TOKEN`. The package must grant this
   repository read access (package settings, **Manage Actions access**).
2. **Read-only deploy keys**, one per internal repository, stored here as secrets:
   `DEPLOY_KEY_HARDCHARGER`, `DEPLOY_KEY_WARP_SQL`, `DEPLOY_KEY_HARDCHARGER_ADBC`,
   `DEPLOY_KEY_WARP_SQL_ADBC`, `DEPLOY_KEY_HARDCHARGER_JDBC`, `DEPLOY_KEY_WARP_SQL_JDBC`,
   `DEPLOY_KEY_WARP_SQL_JS`. Each repository has the matching public key as a read-only deploy
   key titled "hardcharger-docs CI (read-only)".
3. **No release downloads.** Examples that download a release (the installer, tarballs, the
   Python package's server) run against a release mirror made from the `:main` image, with the
   real installer script and the real package.

Without the image or a key, the examples job fails; it never skips.

## ✍️ Writing

Short sentences, task first, no marketing in guides, and nothing that isn't true and tested.
Python examples use keyword arguments. Don't name competing products, customers or internal
documents. Every page has a `description` (it is the page's search and social summary). New
pages go in the sidebar in [`astro.config.mjs`](astro.config.mjs). Brand assets:
[`scripts/banner.py`](scripts/banner.py) draws README-style banners, and
[`scripts/brand_images.mjs`](scripts/brand_images.mjs) the favicon and social card.

## 🚀 Launch checklist (docs.hardcharger.gizmodata.com)

Same pattern as [hardcharger-install](https://github.com/gizmodata/hardcharger-install): a private
S3 bucket behind CloudFront, deployed from CI by GitHub OIDC, all of it in
[gizmodata-infrastructure-terraform](https://github.com/gizmodata/gizmodata-infrastructure-terraform)
(`aws/dns/`, next to `hardcharger_install.tf`). Don't create any of it before Philip says go.

- [ ] Terraform (`aws/dns/hardcharger_docs.tf`), one reviewed plan with only additions:
  - [ ] S3 bucket `gizmodata-hardcharger-docs`: public access blocked, bucket-owner-enforced,
        SSE, versioning, a lifecycle rule for old versions, a policy that lets only the
        distribution (OAC) read.
  - [ ] ACM certificate for `docs.hardcharger.gizmodata.com` in us-east-1, DNS-validated.
  - [ ] CloudFront distribution with OAC, HTTP/2 and HTTP/3, `redirect-to-https`, compression,
        and a CloudFront Function that maps `/path/` to `/path/index.html` (S3 behind OAC has
        no index documents) and serves `404.html` for misses.
  - [ ] A response headers policy: HSTS, `X-Content-Type-Options: nosniff`, `Referrer-Policy`,
        and a CSP that allows the site's own scripts and the shields.io badge images.
  - [ ] Route53 A/AAAA alias records for `docs.hardcharger.gizmodata.com`.
  - [ ] An IAM role trusted by GitHub OIDC for this repository's `refs/tags/v*` only, allowed to
        write that bucket and invalidate that distribution.
- [ ] `release.yml`: build with `DOCS_SITE=https://docs.hardcharger.gizmodata.com` and
      `DOCS_INDEXABLE=true`, `aws s3 sync --delete` (HTML `no-cache`, `_astro/` immutable), invalidate,
      then fetch the live pages and check they serve this commit. Keep the deployment record.
- [ ] Drop the private-preview banner and `noindex` (`DOCS_INDEXABLE=true`), and the GitHub Pages
      preview (or keep it for pull-request previews).
- [ ] Remove the "private preview" asides: the installer, the image and the drivers without a
      token; `pip install hardcharger` and `adbc-driver-hardcharger` from PyPI; the JDBC jar from
      Maven Central or the releases.
- [ ] Lychee: stop excluding `github.com/gizmodata/` once the repositories are public.
- [ ] Search Console: add the domain and submit `sitemap-index.xml`.
- [ ] Versioned docs: archive the launch version with
      [starlight-versions](https://github.com/HiDeoo/starlight-versions) and replace the header
      badge with its picker.
- [ ] Check every page in Chromium and WebKit on the live domain (CSP violations included),
      then link the docs from the READMEs, gizmodata.com and the CLI's `.about`.

## 📄 License

Apache License 2.0, like Hardcharger.

---

<p align="center">
  <a href="https://gizmodata.com"><img src="src/assets/gizmodata-logo.png" alt="GizmoData" width="56"></a><br>
  <sub>Built by <a href="https://gizmodata.com">GizmoData</a></sub>
</p>
