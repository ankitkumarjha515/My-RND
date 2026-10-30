# OpenCode Android

One Android app that runs [OpenCode](https://github.com/sst/opencode) entirely on the phone. A bundled Alpine Linux
(run through Termux's `proot`) hosts `opencode serve` on `127.0.0.1:4096`, and a full-screen WebView shows OpenCode's
own web UI, which has phone layouts for chat, the file tree and the terminal. Decision record: `../docs/DECISIONS.md`.

## Install
Download `opencode-android.apk` from the `opencode-android-latest` pre-release on GitHub. Needs an arm64 phone running Android 8+.
On first launch the app downloads git, ripgrep, bash and OpenCode (~300 MB), so it needs internet.

## How it works
- `app/.../MainActivity.kt`: setup screen, then the WebView. Signs in through OpenCode's pairing link (`/api/pair` → `/auth/connect/<code>`).
- `app/.../OpenCodeService.kt`: foreground service that keeps the server running and restarts it after a crash (up to 3 times in 2 minutes).
- `app/.../OpenCodeRuntime.kt`: unpacks Alpine, runs `assets/setup.sh` once, and launches commands through proot.
- `core/`: plain-Kotlin logic with unit tests (proot arguments, tar extraction, pairing).
- `scripts/fetch-native.sh`: CI step that downloads proot, libtalloc (Termux) and the Alpine minirootfs into the APK.

## Commands
- Unit tests (any machine with JDK 17+): `CORE_ONLY=1 gradle :core:test`
- Full build (needs the Android SDK): `scripts/fetch-native.sh && gradle :core:test :app:assembleDebug`
- CI: `.github/workflows/opencode-android.yml` builds on every push under `opencode-android/` and publishes the APK.
