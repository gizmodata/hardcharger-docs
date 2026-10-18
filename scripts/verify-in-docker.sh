#!/usr/bin/env bash
# Runs scripts/verify_examples.py inside a Linux container, so the examples get the
# documented ports (31337, 31338, ...) to themselves even when something on this machine
# already holds them. CI runs the same examples directly on its runner.
#
#   scripts/verify-in-docker.sh [verify_examples.py arguments]
#
# Needs (paths on this machine):
#   HARDCHARGER_DOCS_LINUX_DIR   an unpacked hardcharger-linux-<arch> release or CI artifact
#                                (bin/hardcharger-server, bin/hardcharger, lib/)
#   HARDCHARGER_DOCS_ADBC_SRC    a gizmodata/hardcharger-adbc checkout with its submodule
#   HARDCHARGER_DOCS_PY_SRC      gizmodata/hardcharger's python/ directory (the server package)
#   HARDCHARGER_DOCS_JDBC_JAR    the standalone hardcharger-jdbc.jar
# Optional: HARDCHARGER_DOCS_PG_URI (as seen from the container: host.docker.internal).
# The gizmodata Go modules are fetched over SSH with this machine's SSH agent (Docker Desktop
# forwards it), as a developer with access to the repositories does.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
for v in HARDCHARGER_DOCS_LINUX_DIR HARDCHARGER_DOCS_ADBC_SRC HARDCHARGER_DOCS_PY_SRC HARDCHARGER_DOCS_JDBC_JAR; do
  [ -n "${!v:-}" ] && [ -e "${!v}" ] || { echo "$v must name an existing path" >&2; exit 1; }
done
IMAGE=hardcharger-docs-verify
docker build -q -t "$IMAGE" "$ROOT/tests/docker" >/dev/null

# The container's own Python environment and Go caches live in volumes, so later runs are fast.
docker run --rm -i \
  --add-host host.docker.internal:host-gateway \
  -v "$ROOT":/docs \
  -v "$HARDCHARGER_DOCS_LINUX_DIR":/hc:ro \
  -v "$HARDCHARGER_DOCS_ADBC_SRC":/src/hardcharger-adbc:ro \
  -v "$HARDCHARGER_DOCS_PY_SRC":/src/hardcharger-py:ro \
  -v "$HARDCHARGER_DOCS_JDBC_JAR":/src/hardcharger-jdbc.jar:ro \
  -v hardcharger-docs-venv:/opt/venv \
  -v hardcharger-docs-go:/root/go \
  -e HARDCHARGER_DOCS_BIN_DIR=/hc/bin \
  -e HARDCHARGER_DOCS_VENV=/opt/venv \
  -e HARDCHARGER_DOCS_JDBC_JAR=/src/hardcharger-jdbc.jar \
  -e GOMODCACHE=/root/go/pkg/mod -e GOCACHE=/root/go/cache \
  -e HARDCHARGER_DOCS_PG_URI="${HARDCHARGER_DOCS_PG_URI:-}" \
  -v /run/host-services/ssh-auth.sock:/ssh-agent -e SSH_AUTH_SOCK=/ssh-agent \
  -w /docs "$IMAGE" bash -euo pipefail -s -- "$@" <<'SCRIPT'
# The Hardcharger ADBC driver's C library, built from the hardcharger-adbc checkout (no zig:
# this library only has to run in this container), into a Python environment with the
# server package and the examples' other imports. Rebuilt when the checkout changes.
REV=$(git -C /src/hardcharger-adbc rev-parse HEAD 2>/dev/null || echo unknown)
mkdir -p ~/.ssh && ssh-keyscan -t ed25519 github.com >> ~/.ssh/known_hosts 2>/dev/null
git -C / config --global url."git@github.com:gizmodata/".insteadOf https://github.com/gizmodata/  # -C /: /docs may be a worktree whose .git points outside the container
export GOPRIVATE='github.com/gizmodata/*' GOFLAGS=-mod=mod
if [ ! -f "/opt/venv/.built-$REV" ]; then
  rm -rf /tmp/hc-adbc /tmp/hc-py /opt/venv/* && cp -R /src/hardcharger-adbc /tmp/hc-adbc && cp -R /src/hardcharger-py /tmp/hc-py
  (cd /tmp/hc-adbc/go && CGO_ENABLED=1 go build -tags driverlib -buildmode=c-shared \
     -o ../python/src/adbc_driver_hardcharger/libadbc_driver_hardcharger.so ./pkg/hardcharger)
  python3 -m venv /opt/venv
  /opt/venv/bin/pip install -q /tmp/hc-adbc/python /tmp/hc-py pyyaml pexpect pyjwt cryptography
  touch "/opt/venv/.built-$REV"
fi
/opt/venv/bin/python scripts/verify_examples.py "$@"
SCRIPT
