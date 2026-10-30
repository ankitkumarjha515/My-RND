#!/bin/sh
# First-run setup inside the bundled Alpine Linux. Safe to run again.
set -eu

echo "[1/3] Installing tools: bash, git, ripgrep…"
apk update
apk add --no-progress bash git ripgrep curl ca-certificates libstdc++ libgcc openssh-client

echo "[2/3] Downloading the latest OpenCode…"
package=@opencode/cli-linux-arm64-musl
meta=$(curl -fsSL "https://registry.npmjs.org/$package/latest")
version=$(printf '%s' "$meta" | grep -o '"version":"[^"]*"' | head -n 1 | cut -d '"' -f 4)
tarball=$(printf '%s' "$meta" | grep -o '"tarball":"[^"]*"' | head -n 1 | cut -d '"' -f 4)
shasum=$(printf '%s' "$meta" | grep -o '"shasum":"[^"]*"' | head -n 1 | cut -d '"' -f 4)
if [ -z "$version" ] || [ -z "$tarball" ] || [ -z "$shasum" ]; then
    echo "Could not read OpenCode release info from the npm registry" >&2
    exit 1
fi
echo "OpenCode $version"
work=/tmp/opencode-install
rm -rf "$work"
mkdir -p "$work"
curl -fL --progress-bar -o "$work/cli.tgz" "$tarball"
echo "$shasum  $work/cli.tgz" | sha1sum -c -
tar -xzf "$work/cli.tgz" -C "$work"
install -m 755 "$work/package/bin/opencode" /usr/local/bin/opencode
rm -rf "$work"

echo "[3/3] Checking OpenCode runs…"
/usr/local/bin/opencode --version
mkdir -p /root/projects
echo "Setup complete."
