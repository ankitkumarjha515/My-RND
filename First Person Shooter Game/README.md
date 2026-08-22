# REACH-OUT — Blacksite FPS

A wave-based arena survival first-person shooter built with **Three.js**.
Single page, no build step, no downloaded assets — every texture, sound and effect is generated procedurally in the browser.

![status](https://img.shields.io/badge/status-playable-green)

---

## How to Run

**Option A (quickest):**
Double-click `index.html`.
Requires internet once per session (loads the Three.js library from CDN).

**Option B (recommended, fully reliable):**

```bash
# from this folder
python -m http.server 8080
```

Then open <http://localhost:8080> and click **DEPLOY**.

---

## Controls

| Action | Input |
|---|---|
| Move | `W A S D` |
| Sprint | `Shift` (forward only) |
| Jump | `Space` |
| Look | Mouse |
| Fire | Left mouse button |
| Aim down sights | Hold right mouse button |
| Switch weapon | `1` / `2` / `Q` / mouse wheel |
| Reload | `R` |
| Pause | `Esc` |

---

## Gameplay

- Survive endless waves of hostiles; each wave spawns faster, tougher enemies.
- **Enemies:** Grunt (baseline) · Scout (fast, from wave 2) · Heavy (tanky, from wave 3).
- Headshots deal **2.2× damage**.
- Kills have a ~22% chance to drop a pickup:
  - 🟩 **Medkit** — +35 HP
  - 🟧 **Ammo box** — rifle +30, RPG +1
- Passive health regen kicks in 6 s after taking damage.
- Death screen shows kills + wave reached; hit **REDEPLOY** to restart instantly.

## Weapons

| Weapon | Type | Mag | Reserve | Notes |
|---|---|---|---|---|
| M4 Carbine | Hitscan | 30 | 150 | Full-auto, spread grows while moving/sprinting |
| RPG-7 | Rocket | 1 | 8 | Splash damage — hurts enemies *and you* if close |

---

## Project Structure

```
First Person Shooter Game/
├── index.html          entry point: bootstrap + module load order
└── modules/
    ├── core.js         renderer, scene, camera rig, game loop, adaptive resolution
    ├── arena.js        map: sky, lighting, textures, props, spawn points
    ├── player.js       pointer lock, movement, input, health, death/restart
    ├── weapons.js      viewmodels, firing, ADS, reload, weapon switching
    ├── ballistics.js   hitscan raycasts, rockets, explosions
    ├── enemies.js      enemy types, AI movement, walk animation, damage
    ├── director.js     wave director, difficulty scaling, pickups
    ├── ui.js           HUD, hitmarkers, kill feed, overlays
    ├── audio.js        synthesized WebAudio SFX (no sound files)
    └── fx.js           pooled particles, tracers, muzzle flashes, explosions
```

**Load order matters** (`index.html` script tags):
`three.js → bootstrap → core → glue → arena → ui → audio → fx → player → ballistics → weapons → enemies → director`
Each module grabs its dependencies at load time, so this sequence must not be reshuffled.

### Module API (glue between files)

Modules communicate through the global `window.GAME` namespace:
`GAME.core`, `GAME.arena`, `GAME.player`, `GAME.weapons`, `GAME.ballistics`,
`GAME.enemies`, `GAME.director`, `GAME.ui`, `GAME.audio`, `GAME.fx`.

---

## Graphics & Audio — all procedural, 0 KB of assets

- Gradient sky-dome shader with horizon haze and sun glow sprite.
- PBR-style canvas textures (asphalt ground, concrete barriers, wooden crates), each with a **normal map derived at runtime via Sobel filtering**.
- Environment reflections generated from the sky itself (PMREM) — metals pick it up for free.
- Late-afternoon directional lighting with soft shadows; drifting dust motes for depth.
- All SFX are synthesized WebAudio oscillators/noise bursts — zero sound files.

## Tech Notes

- Three.js r152+ (UMD build from CDN with fallback URL).
- Adaptive pixel-ratio scaling keeps framerate stable on weaker GPUs.
- Update loop is priority-sorted and crash-isolated per system (one broken subsystem can't freeze the game).
- Errors surface in a red banner at the top of the screen instead of failing silently.
