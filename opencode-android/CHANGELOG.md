# Changelog

Versions are `app version (OpenCode version)`. The build number (versionCode) comes from CI and always grows.

## 0.2.0 (OpenCode 2.2.2)
- OpenCode's own app icon and a matching notification icon.
- Version shown in the installer, on the start screen and in the notification; versioned GitHub releases.
- Security fixes from `docs/security-audit-opencode-android.md`: WebView limited to the local server, port-squatting check, new password per start, pinned downloads, no backups, release (non-debuggable) build, storage limited to the OpenCode folder.
- Recovers from a blank white screen after time in the background.

## 0.1.x (OpenCode latest at install time)
- First working build: Alpine Linux through proot, OpenCode server in a foreground service, OpenCode web UI in a WebView.
