(() => {
  const G = window.GAME;
  const T = THREE;

  const GUNMETAL = 0x2b2f36;
  const DARK = 0x17191d;
  const ACCENT = 0x3a4150;

  const defs = [
    { name: 'M4 CARBINE', type: 'hitscan', magSize: 30, mag: 30, reserve: 150, maxReserve: 150, dmg: 26, rate: .105, reload: 1.6, auto: true },
    { name: 'RPG-7', type: 'rocket', magSize: 1, mag: 1, reserve: 8, maxReserve: 8, dmg: 0, rate: 1, reload: 2.6, auto: false }
  ];

  const hipPoses = [new T.Vector3(.26, -.23, -.45), new T.Vector3(.3, -.27, -.55)];
  const adsPoses = [new T.Vector3(0, -.158, -.34), new T.Vector3(.14, -.22, -.5)];

  let cur = 0;
  let reloading = false;
  let reloadEnd = 0;
  let switching = false;
  let swEnd = 0;
  let nextFire = 0;
  let raise = 0;
  let adsLerp = 0;
  let vmKick = 0;
  let swayX = 0;
  let swayY = 0;
  let fovCur = 75;
  let prevDown = false;
  let clickConsumed = false;
  let emptyDone = false;

  const groups = [];
  const muzzles = [];

  function mat(c) {
    return new T.MeshStandardMaterial({ color: c, metalness: .7, roughness: .45 });
  }

  function prep(m) {
    m.castShadow = false;
    m.frustumCulled = false;
    return m;
  }

  function box(w, h, d, m) {
    return prep(new T.Mesh(new T.BoxGeometry(w, h, d), m));
  }

  function cyl(r, l, m) {
    const c = new T.Mesh(new T.CylinderGeometry(r, r, l, 14), m);
    c.rotation.x = Math.PI / 2;
    return prep(c);
  }

  function cone(r, h, m, back) {
    const c = new T.Mesh(new T.ConeGeometry(r, h, 14), m);
    c.rotation.x = back ? Math.PI / 2 : -Math.PI / 2;
    return prep(c);
  }

  function place(g, mesh, x, y, z) {
    mesh.position.set(x, y, z);
    g.add(mesh);
    return mesh;
  }

  function buildRifle() {
    const g = new T.Group();
    const gun = mat(GUNMETAL);
    const dark = mat(DARK);
    const acc = mat(ACCENT);
    place(g, box(.07, .09, .42, gun), 0, 0, 0);
    place(g, box(.06, .06, .22, acc), 0, .01, -.32);
    place(g, cyl(.017, .34, dark), 0, .015, -.52);
    place(g, box(.05, .14, .07, dark), 0, -.1, .02).rotation.x = .18;
    place(g, box(.06, .08, .16, gun), 0, -.01, .3);
    place(g, box(.04, .1, .05, dark), 0, -.09, .14).rotation.x = .45;
    place(g, box(.02, .05, .02, dark), 0, .06, -.6);
    place(g, box(.04, .04, .03, dark), 0, .06, .1);
    const mz = new T.Object3D();
    mz.position.set(0, .01, -.6);
    g.add(mz);
    return { g: g, mz: mz };
  }

  function buildRPG() {
    const g = new T.Group();
    const gun = mat(GUNMETAL);
    const dark = mat(DARK);
    const acc = mat(ACCENT);
    const warhead = new T.MeshStandardMaterial({ color: 0x7a2f1a, metalness: .7, roughness: .45 });
    place(g, cyl(.05, .9, gun), 0, 0, 0);
    place(g, cone(.07, .18, acc, true), 0, 0, .54);
    place(g, cone(.06, .25, warhead, false), 0, 0, -.56);
    place(g, box(.04, .09, .05, dark), 0, -.11, .12).rotation.x = .3;
    place(g, box(.04, .09, .05, dark), 0, -.1, -.08).rotation.x = -.2;
    place(g, box(.05, .06, .12, dark), 0, .09, 0);
    const mz = new T.Object3D();
    mz.position.set(0, .02, -.85);
    g.add(mz);
    return { g: g, mz: mz };
  }

  function hud() {
    const d = defs[cur];
    G.ui.setAmmo(d.mag, d.reserve, d.name);
  }

  function currentDef() {
    return defs[cur];
  }

  function fire() {
    const st = G.core.state;
    const d = defs[cur];
    const p = G.player;
    G.core.yawObj.updateMatrixWorld(true);
    muzzles[cur].getWorldPosition(G.core.V1);
    G.core.camera.getWorldDirection(G.core.V2);
    nextFire = st.time + d.rate;
    if (d.type === 'hitscan') {
      const spread = (p.input.ads ? .0012 : .009) +
        Math.min(p.speed2D() * .002, .02) +
        (p.isSprinting ? .012 : 0);
      G.core.V2.x += (Math.random() - .5) * 2 * spread;
      G.core.V2.y += (Math.random() - .5) * 2 * spread;
      G.core.V2.z += (Math.random() - .5) * 2 * spread;
      G.core.V2.normalize();
      G.ballistics.fireHitscan(G.core.V1.clone(), G.core.V2.clone(), d.dmg, { fromPlayer: true });
      G.fx.muzzleFlash(G.core.V1, 1);
      G.audio.shot();
      vmKick = Math.min(vmKick + .05, .12);
      p.recoil(.011);
    } else {
      G.ballistics.spawnRocket(G.core.V1.clone(), G.core.V2.clone());
      G.audio.rocketFire();
      vmKick = Math.min(vmKick + .14, .2);
      p.recoil(.035);
    }
    hud();
  }

  function tryFire() {
    const st = G.core.state;
    const d = defs[cur];
    if (reloading || switching || st.time < nextFire) return false;
    if (d.mag <= 0) {
      if (!emptyDone) {
        G.audio.emptyClick();
        emptyDone = true;
      }
      if (d.reserve > 0) startReload();
      return false;
    }
    fire();
    return true;
  }

  function startReload() {
    const d = defs[cur];
    if (reloading || switching || d.mag === d.magSize || d.reserve <= 0) return;
    reloading = true;
    reloadEnd = G.core.state.time + d.reload;
    G.audio.reload();
    G.ui.msg('RELOADING', Math.round(d.reload * 1000));
  }

  function finishReload() {
    const d = defs[cur];
    const n = Math.min(d.magSize - d.mag, d.reserve);
    d.mag += n;
    d.reserve -= n;
    reloading = false;
    hud();
  }

  function switchTo(i) {
    if (i === cur || switching || i < 0 || i >= defs.length) return;
    groups[cur].visible = false;
    cur = i;
    groups[cur].visible = true;
    reloading = false;
    raise = 1;
    swEnd = G.core.state.time + .35;
    switching = true;
    hud();
  }

  function nextWeapon() {
    switchTo((cur + 1) % defs.length);
  }

  function muzzleWorld(out) {
    return muzzles[cur].getWorldPosition(out);
  }

  function addAmmo(rifleN, rpgN) {
    defs[0].reserve = Math.min(defs[0].reserve + rifleN, defs[0].maxReserve);
    defs[1].reserve = Math.min(defs[1].reserve + rpgN, defs[1].maxReserve);
    hud();
  }

  function refillAll() {
    for (let i = 0; i < defs.length; i++) defs[i].reserve = defs[i].maxReserve;
    hud();
  }

  function reset() {
    for (let i = 0; i < defs.length; i++) {
      defs[i].mag = defs[i].magSize;
      defs[i].reserve = defs[i].maxReserve;
    }
    cur = 0;
    for (let i = 0; i < groups.length; i++) groups[i].visible = i === 0;
    reloading = false;
    reloadEnd = 0;
    switching = false;
    swEnd = 0;
    nextFire = 0;
    raise = 0;
    adsLerp = 0;
    vmKick = 0;
    swayX = 0;
    swayY = 0;
    fovCur = 75;
    prevDown = false;
    clickConsumed = false;
    emptyDone = false;
    G.core.camera.fov = 75;
    G.core.camera.updateProjectionMatrix();
    hud();
  }

  function update() {
    const st = G.core.state;
    if (!st.playing) return;
    const dt = st.dt || 0;
    const t = st.time;
    const input = G.player.input;
    const d = defs[cur];
    const k = 1 - Math.exp(-12 * dt);
    swayX += (T.MathUtils.clamp(-input.mdx * .0015, -.05, .05) - swayX) * k;
    swayY += (T.MathUtils.clamp(-input.mdy * .0015, -.05, .05) - swayY) * k;
    input.mdx = 0;
    input.mdy = 0;
    if (reloading && t >= reloadEnd) finishReload();
    if (switching && t >= swEnd) switching = false;
    const down = input.mouseDown;
    const pressed = down && !prevDown;
    if (!down) {
      clickConsumed = false;
      emptyDone = false;
    }
    if (down && !(reloading || switching)) {
      if (d.mag <= 0) {
        if (!emptyDone) {
          G.audio.emptyClick();
          emptyDone = true;
        }
        if (d.reserve > 0) startReload();
        clickConsumed = true;
      } else if ((d.auto && down) || (pressed && !clickConsumed)) {
        if (tryFire()) clickConsumed = true;
      }
    }
    prevDown = down;
    let fovTarget = 75 + (G.player.isSprinting ? 6 : 0);
    if (input.ads && !reloading) fovTarget = cur === 0 ? 52 : 62;
    const pf = G.core.camera.fov;
    fovCur += (fovTarget - fovCur) * (1 - Math.exp(-12 * dt));
    if (Math.abs(pf - fovCur) > .01) {
      G.core.camera.fov = fovCur;
      G.core.camera.updateProjectionMatrix();
    }
    adsLerp += (((input.ads && !reloading) ? 1 : 0) - adsLerp) * (1 - Math.exp(-10 * dt));
    const sf = Math.min(G.player.speed2D() / 6, 1);
    const g = groups[cur];
    g.position.lerpVectors(hipPoses[cur], adsPoses[cur], adsLerp);
    g.position.y += Math.sin(G.player.bobT * 2) * .012 * (1 - adsLerp) * sf;
    g.position.x += Math.cos(G.player.bobT) * .008 * (1 - adsLerp) * sf;
    g.position.z += vmKick;
    g.position.y += raise * .25;
    g.rotation.set(vmKick * 1.2 + swayY * 2 - raise * .5, swayX * 2, 0);
    vmKick *= Math.exp(-8 * dt);
    raise = Math.max(0, raise - dt * 3);
  }

  const rifle = buildRifle();
  const rpg = buildRPG();
  groups.push(rifle.g, rpg.g);
  muzzles.push(rifle.mz, rpg.mz);
  rifle.g.visible = true;
  rpg.g.visible = false;
  G.core.camera.add(rifle.g);
  G.core.camera.add(rpg.g);

  G.weapons = {
    defs: defs,
    get cur() { return cur; },
    currentDef: currentDef,
    switchTo: switchTo,
    nextWeapon: nextWeapon,
    startReload: startReload,
    tryFire: tryFire,
    muzzleWorld: muzzleWorld,
    addAmmo: addAmmo,
    refillAll: refillAll,
    reset: reset
  };

  G.core.registerUpdate(update, 25);
  reset();
})();
