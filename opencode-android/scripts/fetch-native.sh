#!/usr/bin/env bash
# Downloads what the APK bundles: Termux's Android build of proot (plus its libraries) and the Alpine aarch64 rootfs.
set -euo pipefail
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

alpine=https://dl-cdn.alpinelinux.org/alpine/latest-stable/releases/aarch64
curl -fsSL "$alpine/latest-releases.yaml" -o "$work/releases.yaml"
read -r file sha < <(awk '/flavor: alpine-minirootfs/ { found = 1 } found && / file:/ { file = $2 } found && / sha256:/ { print file, $2; exit }' "$work/releases.yaml")
if [ -z "${file:-}" ] || [ -z "${sha:-}" ]; then
    echo "Alpine minirootfs not found in latest-releases.yaml" >&2
    exit 1
fi
curl -fsSL "$alpine/$file" -o "$assets/alpine-rootfs.bin"
echo "$sha  $assets/alpine-rootfs.bin" | sha256sum -c -

echo "Bundled: $(ls "$jni" | tr '\n' ' ')and $file"
