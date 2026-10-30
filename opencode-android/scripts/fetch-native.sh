#!/usr/bin/env bash
# Downloads what the APK bundles: Termux's Android build of proot (plus its libraries) and the Alpine aarch64 rootfs.
# Every file is checked against a hash pinned below, so a tampered mirror fails the build. When Termux publishes a new
# proot the build fails here on purpose: review the new version, then update the hashes.
set -euo pipefail

declare -A pinned=(
    [libproot.so]=bc3e5416748276374c513eaad1c6cabedc94246fdf2dd58fa6531374e481fa09
    [libproot-loader.so]=1da54355333cca3fb6ee10e3b82a24df24fb230c99241ce83809bf9e240609b5
    [libtalloc.so]=742b438c4d09e276985a61d44164c9de207b6d8cc268f3018cb3001961bcb309
    [libandroid-shmem.so]=84475798e07c8174dbbfaec70a827fdb02f19ffa69a589380c13e7507fd0e731
)
alpine_version=3.24.3
alpine_sha256=4d3f80afaebd447c5591a63a73bde380a149fe8b2d85488cafabb2ff97551f50
cd "$(dirname "$0")/.."

jni=app/src/main/jniLibs/arm64-v8a
assets=app/src/main/assets
mkdir -p "$jni" "$assets"
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

termux=https://packages.termux.dev/apt/termux-main
curl -fsSL "$termux/dists/stable/main/binary-aarch64/Packages" -o "$work/Packages"

fetch_deb() {
    local name=$1 record file sha
    record=$(awk -v RS= -v head="Package: $name\n" 'index($0 "\n", head) == 1 { print; exit }' "$work/Packages")
    file=$(sed -n 's/^Filename: //p' <<<"$record")
    sha=$(sed -n 's/^SHA256: //p' <<<"$record")
    if [ -z "$file" ] || [ -z "$sha" ]; then
        echo "Termux package $name not found in the package index" >&2
        exit 1
    fi
    curl -fsSL "$termux/$file" -o "$work/$name.deb"
    echo "$sha  $work/$name.deb" | sha256sum -c -
    dpkg-deb -x "$work/$name.deb" "$work/$name"
}

check_needed() {
    local binary=$1 lib
    for lib in $(readelf -d "$binary" | sed -n 's/.*Shared library: \[\(.*\)\]/\1/p'); do
        case $lib in
            libtalloc.so.2 | libandroid-shmem.so | libc.so | libdl.so | libm.so | liblog.so) ;;
            *)
                echo "$binary needs $lib, which the APK does not bundle" >&2
                exit 1
                ;;
        esac
    done
}

fetch_deb proot
fetch_deb libtalloc
fetch_deb libandroid-shmem
prefix=data/data/com.termux/files/usr
cp "$work/proot/$prefix/bin/proot" "$jni/libproot.so"
cp "$work/proot/$prefix/libexec/proot/loader" "$jni/libproot-loader.so"
if [ ! -e "$work/libtalloc/$prefix/lib/libtalloc.so.2" ]; then
    echo "libtalloc.so.2 missing from the libtalloc package; it contains:" >&2
    find "$work/libtalloc" -type f -o -type l >&2
    exit 1
fi
cp -L "$work/libtalloc/$prefix/lib/libtalloc.so.2" "$jni/libtalloc.so"
cp -L "$work/libandroid-shmem/$prefix/lib/libandroid-shmem.so" "$jni/libandroid-shmem.so"
check_needed "$jni/libproot.so"
check_needed "$jni/libtalloc.so"
check_needed "$jni/libandroid-shmem.so"
for lib in "${!pinned[@]}"; do
    if ! echo "${pinned[$lib]}  $jni/$lib" | sha256sum -c --quiet -; then
        echo "$lib does not match its pinned hash (new Termux release or tampering); review it and update fetch-native.sh" >&2
        exit 1
    fi
done

file=alpine-minirootfs-$alpine_version-aarch64.tar.gz
curl -fsSL "https://dl-cdn.alpinelinux.org/alpine/v${alpine_version%.*}/releases/aarch64/$file" -o "$assets/alpine-rootfs.bin"
echo "$alpine_sha256  $assets/alpine-rootfs.bin" | sha256sum -c -

echo "Bundled: $(ls "$jni" | tr '\n' ' ')and $file"
