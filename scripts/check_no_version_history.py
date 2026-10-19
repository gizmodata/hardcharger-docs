#!/usr/bin/env python3
"""Fail if the hand-written docs talk about version history.

TEMPORARY: until Hardcharger 2.0.0 (its first public release), the docs describe the product as it
is. Retire this check at 2.0.0 by deleting this script and the "No version history" step in
.github/workflows/docs.yml; "New in <version>" notes are welcome after that.

Hardcharger's docs describe the product as it is. What changed in which release belongs in the
release notes (the generated reference/release-notes.md, which this check skips, as it does the
other generated reference pages). Install commands and pins (`HARDCHARGER_VERSION=0.3.0`,
`:0.3.0`) are instructions, not history, and don't match.

    python3 scripts/check_no_version_history.py [content-dir]
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {
    "reference/release-notes.md",
    "reference/warp-sql-protocol.md",
    "reference/configuration.mdx",
}
VERSION = r"(?<![\d.])v?(?:\d+\.\d+\.\d+|0\.\d+)\b"
PATTERNS = [
    re.compile(rf"\b(?:new|added|introduced|changed|fixed|deprecated|removed|available|arrives?|arrived)\s+(?:in|with|since|from)\s+(?:hardcharger\s+)?{VERSION}", re.I),
    re.compile(rf"\b(?:since|as of|until|before|after|from|starting (?:in|with)|beginning (?:in|with))\s+(?:hardcharger\s+)?{VERSION}", re.I),
    re.compile(r"\bthe (?:release|version) (?:after|before)\b", re.I),
    re.compile(rf"\bchanged since\b|\bwhat {VERSION} changed\b", re.I),
]


def main() -> int:
    content = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "src" / "content"
    bad = []
    for path in sorted(content.rglob("*")):
        if path.suffix not in (".md", ".mdx"):
            continue
        rel = path.relative_to(content / "docs").as_posix() if (content / "docs").is_dir() else path.name
        if rel in SKIP:
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if any(p.search(line) for p in PATTERNS):
                bad.append(f"{path.relative_to(content.parent.parent) if content.is_relative_to(ROOT) else path}:{number}: {line.strip()[:140]}")
    if bad:
        print("Version-history phrasing in the docs. Until Hardcharger 2.0.0, docs describe the product as it is: describe the current behavior; history belongs in the release notes.")
        print("\n".join(bad))
        return 1
    print("no version-history phrasing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
