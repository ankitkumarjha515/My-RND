# Research: running OpenCode fully on a phone

Date: 2026-10-30. Source read: `github.com/sst/opencode` @ `2273b607` (v2.2.2, branch `dev`).

## Goal
Run both halves of OpenCode on the phone itself (no laptop, no remote server):
the agent backend (server) and a phone-friendly client. LLM calls still go to the
model provider over the internet; everything else stays on the phone.

## What runs on the laptop today
`opencode` starts one local process containing:

| Part | Package | Notes |
|---|---|---|
| Agent core (sessions, tools, permissions, LLM calls) | `packages/core` | TypeScript on Effect; runs on Bun or Node |
| HTTP API server | `packages/server` | Clients talk to this |
| Clients | `packages/tui` (terminal), `packages/app` (web/PWA), `packages/desktop` (Electron) | All talk to the server over HTTP |
| Storage | SQLite | `core/src/database/sqlite.bun.ts` and `sqlite.node.ts` (`node:sqlite`) |

Things the core runs or loads on the machine:
- **Shell and PTY**: the bash tool and terminals spawn `bash`/`sh` through `node-pty`/`bun-pty`/`opencode-pty`.
- **git**, **ripgrep** (`core/src/ripgrep/binary.ts`: looks for `rg` on PATH first, then downloads a pinned build), LSP servers, formatters, MCP servers.
- **Native add-ons**: `@parcel/watcher` (file watching), `@ff-labs/fff` and `ffi-rs` (fuzzy file finder), `node-pty`, and `@opentui` (TUI only). Prebuilt only for darwin, linux and win32 (`cli/src/node/target.ts`). There is no Android target.

## Findings
1. **There are two runtimes.** The default binary is compiled with Bun (`cli/script/build.ts`). There is also a Node build (`cli/script/build-node.ts`, Node 26 SEA, needs `--experimental-ffi`). Node runs natively on Android in Termux. Bun does not: only community glibc wrappers exist.
2. **The web client is already phone-ready.** `packages/app` is a PWA (`manifest.json`, `vite.pwa.ts`, service worker). It has mobile layouts (`shell/mobile-drawer.tsx`, `mobile-panel-drawer.tsx`, `runtime/plugin/mobile.tsx`) and QR pairing (`servers/connect/scanner.tsx`, `opencode pair`). It is built to let a phone connect to a laptop server, so it already works as a phone client.
3. **The client and server are separate over HTTP.** That means the server can run on `localhost` on the phone, and the PWA or an app WebView can connect to it.
4. **Android blockers are the native pieces, not the TypeScript.** The official linux-arm64 binary fails under Termux (wrong ELF interpreter, non-PIE: anomalyco/opencode#10504). Community ports get around it.
5. **iOS cannot host the backend.** Apps cannot spawn processes (no shell, git or ripgrep), and a JIT is not allowed. On iPhone, only the client part is possible.

## Prior art
- **Spectra010s/opencode-termux**: native Termux build of OpenCode 2.0.x on ARM64, no PRoot, one install script. Tested on one Android 14 phone. *Worth stealing:* their native-module rebuild steps. *Skip:* pinned to old 2.0.x.
- **HanSoBored/opencode-termux** and **tribixbite/bun-on-termux**: run Bun binaries through Termux's glibc loader. *Worth stealing:* a fallback if the Node build is not usable. *Skip:* fragile across Android versions.
- **criollojoel10/opencode-termux-native**: prebuilt 1.14.x for Android 16. Old version.
- **Jonathan's blog / dev.to guides**: Termux + Node/npm install, then run in the project directory.
- **Upstream itself**: the PWA plus `opencode pair` is the official "phone as client" path, but the server stays on the laptop.

## Verdict
- **Android: possible.** Termux provides the Linux userland (bash, git, rg, clang). OpenCode's server runs there, and the client is the existing PWA (or a thin Android wrapper app) on `localhost`. Main work: build or patch the native add-ons for Android (watcher, fff, pty) or use the Node build with fallbacks, and polish the mobile UI.
- **One APK with no Termux: possible but much bigger.** You would have to bundle a Node runtime (e.g. nodejs-mobile), a shell, git and rg inside the app. That means effectively rebuilding parts of Termux.
- **iPhone: backend not possible.** Client only.
