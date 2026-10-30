#!/bin/sh
# First-run setup inside the bundled Alpine Linux. Safe to run again.
set -eu

echo "[1/3] Installing tools: bash, git, ripgrep…"
apk update
apk add --no-progress bash git ripgrep curl ca-certificates libstdc++ libgcc openssh-client

# Pinned: a new OpenCode release is only installed after its version and hash are reviewed and updated here.
version=2.2.2
sha512=96902086fde80b178bdc45030d6f242f6b363fe57eae8d32b8a6538c602ffefc781c3d2865f920a878d83e8f3ea518302c36063ae316ebea4c1f65253c59194a
tarball="https://registry.npmjs.org/@opencode/cli-linux-arm64-musl/-/cli-linux-arm64-musl-$version.tgz"

echo "[2/3] Downloading OpenCode $version…"
work=/tmp/opencode-install
rm -rf "$work"
mkdir -p "$work"
curl -fL --progress-bar -o "$work/cli.tgz" "$tarball"
echo "$sha512  $work/cli.tgz" | sha512sum -c -
tar -xzf "$work/cli.tgz" -C "$work"
install -m 755 "$work/package/bin/opencode" /usr/local/bin/opencode
rm -rf "$work"

echo "[3/3] Checking OpenCode runs…"
/usr/local/bin/opencode --version
mkdir -p /root/projects
echo "Setup complete."
