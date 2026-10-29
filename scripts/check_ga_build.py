#!/usr/bin/env python3
"""Check a build of the public site (DOCS_GA=true): nothing of the private preview is left in it.

    python3 scripts/check_ga_build.py dist

Fails if any page still carries the preview banner, an aside or a sentence written for the
preview, a GitHub-token instruction, or the noindex tag; if dist/CNAME doesn't name the custom
domain; or if the sitemap isn't on it. CI runs it on a DOCS_GA=true build of every push, so the
switch is proven before it is flipped (README, "Private preview and GA").
"""
import re
import json
import sys
from pathlib import Path

DOMAIN = "docs.hardcharger.gizmodata.com"
SERVER_VERSION = json.loads((Path(__file__).resolve().parent.parent / "src/data/server-version.json").read_text())["version"]
FORBIDDEN = [
    re.compile(p, re.I) for p in (
        r"private preview",
        r"during the preview",
        r"internal (?:to gizmodata|until launch)",
        r"until launch",
        r"gh auth token",
        r"HARDCHARGER_INSTALL_TOKEN",
        r"GOPRIVATE",
        r"<meta[^>]*name=\"robots\"[^>]*noindex",
    )
]


def main() -> int:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    pages = sorted(p for p in out.rglob("*.html") if "pagefind" not in p.parts)
    if not pages:
        print(f"{out}: no HTML pages: not a build", file=sys.stderr)
        return 1
    bad: list[str] = []
    for page in pages:
        text = page.read_text(encoding="utf-8", errors="replace")
        if re.match(r'<!doctype html><title>Redirecting to: [^<]*</title><meta http-equiv="refresh"', text):
            continue  # the page Astro writes at a moved page's old address (noindex, as it should be)
        badge = re.search(r'<a\b[^>]*class="[^"]*\bhc-version\b[^"]*"[^>]*>(.*?)</a>', text, re.S)
        if page == out / "index.html" and not badge:
            bad.append("index.html: missing server version badge")
        if badge and badge.group(1).strip() != SERVER_VERSION:
            bad.append(f"{page.relative_to(out)}: header version differs from server {SERVER_VERSION}")
        for pattern in FORBIDDEN:
            for m in pattern.finditer(text):
                snippet = text[max(0, m.start() - 60):m.end() + 60].replace("\n", " ")
                bad.append(f"{page.relative_to(out)}: /{pattern.pattern}/: …{snippet}…")
                break
        if 'class="expressive-code"' in text and "/_astro/ec." not in text:
            bad.append(f"{page.relative_to(out)}: code blocks without Expressive Code's stylesheet: the page's "
                       "first code block was inside <Preview> or <Ga> (see src/components/Preview.astro)")
    cname = out / "CNAME"
    if not cname.is_file() or cname.read_text(encoding="utf-8").strip() != DOMAIN:
        bad.append(f"{cname}: must contain exactly {DOMAIN}")
    sitemap = out / "sitemap-index.xml"
    if not sitemap.is_file() or f"https://{DOMAIN}/" not in sitemap.read_text(encoding="utf-8"):
        bad.append(f"{sitemap}: must point at https://{DOMAIN}/ (build with DOCS_SITE=https://{DOMAIN})")
    if bad:
        print(f"{out}: {len(bad)} problem(s) for the public site:")
        print("\n".join(bad))
        return 1
    print(f"{out}: {len(pages)} pages, nothing of the private preview, CNAME and sitemap on {DOMAIN}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
