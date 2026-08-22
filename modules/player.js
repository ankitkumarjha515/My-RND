(() => {
  const G = window.GAME;
  const C = G.core;

  const EYE = 1.7;
  const RAD = 0.45;
  const GRAV = 24;
  const JUMP_V = 7.4;
  const WALK = 5.4;
  const SPRINT = 8.4;
  const SENS = 0.0021;

  const yawObj = C.yawObj;
  const camera = C.camera;
  camera.rotation.order = 'YXZ';

  const keys = Object.create(null);
  const input = { mdx: 0, mdy: 0, mouseDown: false, ads: false };
  let velX = 0, velZ = 0, vy = 0;
  let pitch = 0;
  let locked = false;

  function collide(pos, r) {
    const cols = (G.arena && G.arena.colliders) || [];
    for (let i = 0; i < cols.length; i++) {
      const c = cols[i];
      const nx = Math.max(c.x0, Math.min(pos.x, c.x1));
      const nz = Math.max(c.z0, Math.min(pos.z, c.z1));
      const dx = pos.x - nx;
      const dz = pos.z - nz;
      const d2 = dx * dx + dz * dz;
      if (d2 > r * r) continue;
      if (d2 > 1e-8) {
        const d = Math.sqrt(d2);
        pos.x += (dx / d) * (r - d);
        pos.z += (dz / d) * (r - d);
      } else {
        const l = pos.x - c.x0, rr = c.x1 - pos.x, tt = pos.z - c.z0, bb = c.z1 - pos.z;
        const m = Math.min(l, rr, tt, bb);
        if (m === l) pos.x = c.x0 - r;
        else if (m === rr) pos.x = c.x1 + r;
        else if (m === tt) pos.z = c.z0 - r;
        else pos.z = c.z1 + r;
      }
    }
  }

  function die() {
    P.hp = 0;
    P.dead = true;
    C.state.dead = true;
    input.mouseDown = false;
    input.ads = false;
    C.setPlaying(false);
    try { document.exitPointerLock(); } catch (_) {}
    try { G.ui.updateHealth(0, P.hpMax); } catch (_) {}
    try { G.ui.overlay('death', { kills: C.state.kills, wave: C.state.wave }); } catch (_) {}
  }

  const P = {
    input,
    yawObj,
    hpMax: 100,
    hp: 100,
    dead: false,
    isSprinting: false,
    bobT: 0,
    lastHurt: -99,

    speed2D() { return Math.hypot(velX, velZ); },

    recoil(a) {
      pitch += a;
      if (pitch > 1.45) pitch = 1.45;
    },

    heal(n) {
      if (P.dead) return;
      P.hp = Math.min(P.hpMax, P.hp + n);
      try { G.ui.updateHealth(P.hp, P.hpMax); } catch (_) {}
    },

    damage(dmg, fromPos) {
      if (P.dead || !C.state.playing) return;
      P.hp -= dmg;
      P.lastHurt = C.state.time;
      try { G.ui.flashDamage(Math.min(.85, .25 + dmg / 50)); } catch (_) {}
      try { G.ui.updateHealth(P.hp, P.hpMax); } catch (_) {}
      if (P.hp <= 0) die();
    },

    explosionDamage(pos) {
      if (P.dead) return;
      const d = pos.distanceTo(yawObj.position);
      const dmg = 95 * Math.max(0, 1 - d / 8);
      if (dmg < 3) return;
      P.damage(dmg, pos);
    },

    requestLock() {
      try { C.canvas.requestPointerLock(); } catch (err) { console.error('GAME.player: pointer lock failed', err); }
    },

    reset() {
      P.hp = P.hpMax;
      P.dead = false;
      P.bobT = 0;
      P.lastHurt = -99;
      velX = 0; velZ = 0; vy = 0; pitch = 0;
      yawObj.rotation.y = 0;
      yawObj.position.set(0, EYE, 18);
      camera.rotation.x = 0;
      camera.position.set(0, 0, 0);
      input.mdx = 0; input.mdy = 0; input.mouseDown = false; input.ads = false;
      try { G.ui.updateHealth(P.hp, P.hpMax); } catch (_) {}
    },

    restartAll() {
      try { G.enemies.clearAll(); } catch (err) { console.error('GAME.player: restart enemies', err); }
      try { G.ballistics.reset(); } catch (err) { console.error('GAME.player: restart ballistics', err); }
      try { G.weapons.reset(); } catch (err) { console.error('GAME.player: restart weapons', err); }
      try { G.director.reset(); } catch (err) { console.error('GAME.player: restart director', err); }
      C.state.dead = false;
      P.reset();
      try { G.ui.overlay(null); } catch (_) {}
      try { G.ui.setWaveKills(1, 0); } catch (_) {}
      P.requestLock();
    }
  };

  document.addEventListener('pointerlockchange', () => {
    locked = document.pointerLockElement === C.canvas;
    if (locked) {
      C.state.started = true;
      if (!C.state.dead) {
        C.setPlaying(true);
        try { G.ui.overlay(null); } catch (_) {}
      }
    } else {
      input.mouseDown = false;
      input.ads = false;
      if (!C.state.dead && C.state.started) {
        C.setPlaying(false);
        try { G.ui.overlay('pause'); } catch (_) {}
      }
    }
  });

  C.canvas.addEventListener('click', () => {
    if (!locked && !C.state.dead && C.state.started) P.requestLock();
  });
  document.addEventListener('contextmenu', e => e.preventDefault());

  document.addEventListener('mousemove', e => {
    if (!locked || P.dead) return;
    yawObj.rotation.y -= e.movementX * SENS;
    pitch -= e.movementY * SENS;
    if (pitch > 1.45) pitch = 1.45;
    if (pitch < -1.45) pitch = -1.45;
    input.mdx += e.movementX;
    input.mdy += e.movementY;
  });

  document.addEventListener('mousedown', e => {
    if (!locked || P.dead) return;
    if (e.button === 0) input.mouseDown = true;
    else if (e.button === 2) input.ads = true;
  });
  document.addEventListener('mouseup', e => {
    if (e.button === 0) input.mouseDown = false;
    else if (e.button === 2) input.ads = false;
  });

  document.addEventListener('keydown', e => {
    keys[e.code] = true;
    if (e.code === 'Space') e.preventDefault();
    if (!locked || P.dead) return;
    if (e.code === 'KeyR') { try { G.weapons.startReload(); } catch (_) {} }
    else if (e.code === 'Digit1') { try { G.weapons.switchTo(0); } catch (_) {} }
    else if (e.code === 'Digit2') { try { G.weapons.switchTo(1); } catch (_) {} }
    else if (e.code === 'KeyQ') { try { G.weapons.nextWeapon(); } catch (_) {} }
  });
  document.addEventListener('keyup', e => { keys[e.code] = false; });

  document.addEventListener('wheel', () => {
    if (!locked || P.dead) return;
    try { G.weapons.nextWeapon(); } catch (_) {}
  }, { passive: true });

  C.registerUpdate((dt) => {
    camera.rotation.x = pitch;
    const st = C.state;
    if (!st.playing || P.dead) return;

    const fwd = (keys.KeyW ? 1 : 0) - (keys.KeyS ? 1 : 0);
    const strafe = (keys.KeyD ? 1 : 0) - (keys.KeyA ? 1 : 0);
    const yaw = yawObj.rotation.y;
    const s = Math.sin(yaw), c = Math.cos(yaw);
    let wx = -s * fwd + c * strafe;
    let wz = -c * fwd - s * strafe;
    const wl = Math.hypot(wx, wz);
    const moving = wl > 1e-4;
    if (moving) { wx /= wl; wz /= wl; }

    P.isSprinting = (!!keys.ShiftLeft || !!keys.ShiftRight) && fwd > 0 && moving && !input.ads;
    const target = P.isSprinting ? SPRINT : WALK;
    const k = 1 - Math.exp(-10 * dt);
    velX += ((moving ? wx * target : 0) - velX) * k;
    velZ += ((moving ? wz * target : 0) - velZ) * k;

    const p = yawObj.position;
    if (keys.Space && vy <= 0.01 && p.y <= EYE + 0.01) vy = JUMP_V;
    vy -= GRAV * dt;
    p.x += velX * dt;
    p.z += velZ * dt;
    p.y += vy * dt;
    if (p.y < EYE) { p.y = EYE; vy = 0; }

    collide(p, RAD);
    const B = ((G.arena && G.arena.BOUND) || 76) - 0.6;
    p.x = Math.max(-B, Math.min(B, p.x));
    p.z = Math.max(-B, Math.min(B, p.z));

    const spd = Math.hypot(velX, velZ);
    if (p.y <= EYE + 0.001 && spd > .5) P.bobT += dt * spd * 1.35;
    const sf = Math.min(spd / WALK, 1);
    camera.position.y = Math.sin(P.bobT * 2) * .035 * sf;

    if (st.time - P.lastHurt > 6 && P.hp < P.hpMax) {
      P.hp = Math.min(P.hpMax, P.hp + 9 * dt);
      try { G.ui.updateHealth(P.hp, P.hpMax); } catch (_) {}
    }
  }, 10);

  G.player = P;
})();
