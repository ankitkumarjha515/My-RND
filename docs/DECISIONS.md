# Decisions

## 2026-10-30 — OpenCode on Android: approach C (proot Linux + phone UI)

**Decision:** Build one Android app. Inside it, a proot Linux environment runs the official OpenCode
Linux ARM64 build as a local server. The app shows OpenCode's own web UI (already has phone layouts) in a
WebView pointed at that local server. Opening the app goes straight to chat; no typing commands.

**Owner requirements:** Chat-first phone UI on launch. File tree available. Terminal available but optional.

**Why (owner's reasoning):** Medium effort. Gives a proper phone UI instead of a terminal.

**Rejected:** A (proot + terminal only): terminal-first experience, not wanted.
B (rebranded Termux, native build): highest effort, OpenCode's native modules need porting on every update.

**Research finding that shapes the build:** OpenCode's web UI (`packages/app`, `packages/gui-plugins`)
already has mobile views for the file tree (`file/mobile.tsx`) and the terminal (`terminal/renderer.tsx`),
so no separate native terminal screen is needed.

**Constraints accepted:** Sideloaded APK only (no Play Store). Proot makes shell, git and search slower than native.
