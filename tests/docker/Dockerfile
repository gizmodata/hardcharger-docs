# A Linux environment for running the docs' examples on a laptop where other servers may hold
# the documented ports (scripts/verify-in-docker.sh). CI runs the same examples on its runner.
FROM ubuntu:24.04
ARG GO_VERSION=1.27.2
ARG NODE_VERSION=24.22.0
ARG GH_VERSION=2.83.0
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      ca-certificates curl jq openssl git openssh-client build-essential python3 python3-venv \
      openjdk-17-jdk-headless postgresql-client xz-utils libssl3t64 \
    && rm -rf /var/lib/apt/lists/*
RUN arch=$(dpkg --print-architecture) \
    && curl -fsSL "https://go.dev/dl/go${GO_VERSION}.linux-${arch}.tar.gz" | tar -C /usr/local -xz \
    && node_arch=$([ "$arch" = amd64 ] && echo x64 || echo arm64) \
    && curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-${node_arch}.tar.xz" \
       | tar -C /usr/local --strip-components=1 -xJ \
    && curl -fsSL "https://github.com/cli/cli/releases/download/v${GH_VERSION}/gh_${GH_VERSION}_linux_${arch}.tar.gz" \
       | tar -C /usr/local --strip-components=1 -xz
ENV PATH=/usr/local/go/bin:$PATH
