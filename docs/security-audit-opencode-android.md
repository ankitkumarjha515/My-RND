# Security audit: OpenCode Android (2026-10-30)

Read-only review of `opencode-android/`, the CI workflow, and the OpenCode server's auth code.

## Status (fixed in commit 80db740)
- Fixed: WebView port leak, port squatting, link launching, backups, debuggable build, password storage and rotation, command-line password, pinned downloads, CI action pins and permissions, release checksum, storage limited to `/sdcard/OpenCode`, tar symlink escape.
- Not fixable in the app: proot is not a sandbox, agent network access, OpenCode's loopback CORS rule, agent reading the server password from its environment, targetSdk 28.
- Needs the owner: a real signing key stored in GitHub Secrets.
- Left as is: the wake lock (keeps agents running with the screen off) and remote images in the UI (blocking them may break OpenCode's UI).

## Top 3 to fix first
1. WebView sends the password to any 127.0.0.1 port; limit it to port 4096 (`MainActivity.kt`).
2. Another app can take port 4096 first and receive the password; check the server is really ours (`LocalServer.kt`).
3. Pin versions and hashes for OpenCode (`setup.sh`), Alpine, Termux packages, and the GitHub Actions used.

## 1. Local network
- High: port squatting. A rogue app listening on 4096 first gets the password.
- Medium: the server trusts any `127.0.0.1:*` page for CORS, which makes the above worse.
- OK: without the password, other apps only get "401 unauthorized".
- OK: pairing codes and terminal tickets are random, short-lived and single-use.

## 2. Passwords and API keys
- Medium: backups and debug mode let anyone with USB debugging copy the password and API keys. Fix: `allowBackup=false` and a release build.
- Low: the password is visible on the proot command line (only to the app itself and adb).
- Low: the agent's shell can probably read the server password (unverified).
- Low: the password never changes and sessions last 30 days. Fix: a new password on each start.

## 3. WebView
- High: credentials and cookies are sent to any 127.0.0.1 port (see Top 3 #1).
- Medium: page scripts can open other apps through links without a tap. Fix: allow only http/https, and only on a tap.
- Low: remote images and iframes can load (tracking or data leaks).
- OK: cleartext is allowed only for 127.0.0.1, file access is off, and there is no JavaScript bridge.

## 4. Supply chain
- High: every setup installs the latest OpenCode from npm, with a hash taken from the same source. Fix: pin the version and hash.
- Medium: Termux and Alpine downloads are verified only against hashes from their own servers. Fix: pin hashes in the repo.
- Medium: CI actions are pinned by tag, not commit, and run with write access.
- Medium: the APK is debug-signed with a cached key and the release has no checksum. Fix: a real signing key in GitHub Secrets.
- OK: Alpine packages (`apk add`) are signature-checked.

## 5. Agent sandbox
- High: proot is not a security wall. The agent can read everything the app can, including its password and API keys.
- High: with storage access, the agent can read or delete all your phone files. Fix: share only `/sdcard/OpenCode`.
- Medium: the agent has full internet and local network access. Keep OpenCode's "ask before running" permissions on.

## 6. Android
- Medium: the APK is debuggable (debug build).
- Low: targetSdk 28 turns off newer Android protections (needed for proot, same as Termux).
- Low: the wake lock never times out (battery drain only).
- OK: the service is not exported and notification actions use immutable intents.

## 7. Unpacking Linux (TarExtractor)
- Low: a malicious rootfs could write outside its folder through symlinks. Only possible if the bundled rootfs is already compromised.
