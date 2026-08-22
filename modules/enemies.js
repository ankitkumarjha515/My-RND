(() => {
const G = window.GAME;
const C = G.core;
const A = G.arena;
const P = G.player;
const FX = G.fx;
const AU = G.audio;
const UI = G.ui;
const clamp = THREE.MathUtils.clamp;
const V1 = C.V1 || (C.V1 = new THREE.Vector3());
const V2 = C.V2 || (C.V2 = new THREE.Vector3());
const T1 = new THREE.Vector3();
const T2 = new THREE.Vector3();
const T3 = new THREE.Vector3();
const ray = new THREE.Raycaster();

const TYPES = {
  grunt: { name: 'Grunt', hp: 100, spd: 2.3, dmg: 7, body: 0x4a5240, visor: 0xff3030, scale: 1, w: 0.55 },
  scout: { name: 'Scout', hp: 60, spd: 3.6, dmg: 5, body: 0x4a5240, visor: 0x35e0ff, scale: 0.92, w: 0.5 },
  heavy: { name: 'Heavy', hp: 220, spd: 1.5, dmg: 13, body: 0x4a5240, visor: 0xffa020, scale: 1.18, w: 0.62 }
};

const list = [];

function buildBot(t) {
  const g = new THREE.Group();
  const mat = new THREE.MeshStandardMaterial({ color: t.body, roughness: 0.6, metalness: 0.3 });
  const vmat = new THREE.MeshStandardMaterial({ color: t.visor, emissive: new THREE.Color(t.visor), emissiveIntensity: 0.9, roughness: 0.4, metalness: 0.2 });
  const legGeo = new THREE.BoxGeometry(0.16, 0.5, 0.16);
  for (let s = -1; s <= 1; s += 2) {
    const leg = new THREE.Mesh(legGeo, mat);
    leg.position.set(s * 0.12, 0.25, 0);
    leg.castShadow = true;
    leg.userData.part = 'body';
    g.add(leg);
  }
  const torso = new THREE.Mesh(new THREE.CapsuleGeometry(0.3, 0.55, 6, 12), mat);
  torso.position.y = 0.95;
  torso.scale.set(t.w / 0.6, 1, t.w / 0.6);
  torso.castShadow = true;
  torso.userData.part = 'body';
  g.add(torso);
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.21, 14, 10), mat);
  head.position.y = 1.55;
  head.castShadow = true;
  head.userData.part = 'head';
  g.add(head);
  const visor = new THREE.Mesh(new THREE.BoxGeometry(0.26, 0.07, 0.05), vmat);
  visor.position.set(0, 1.57, 0.19);
  visor.userData.part = 'body';
  g.add(visor);
  const gun = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.09, 0.5), mat);
  gun.position.set(0.28, 1.05, 0.15);
  gun.castShadow = true;
  gun.userData.part = 'body';
  g.add(gun);
  const barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.22, 8), mat);
  barrel.rotation.x = Math.PI / 2;
  barrel.position.set(0.28, 1.05, 0.48);
  barrel.castShadow = true;
  barrel.userData.part = 'body';
  g.add(barrel);
  const muzzle = new THREE.Object3D();
  muzzle.position.set(0.28, 1.05, 0.6);
  g.add(muzzle);
  g.scale.setScalar(t.scale);
  g.scale.y = 0.001;
  return { g, mat, vmat, head, muzzle };
}

function spawn(typeName) {
  const t = TYPES[typeName] || TYPES.grunt;
  const wave = Math.max(1, C.state.wave || 1);
  const parts = buildBot(t);
  const g = parts.g;
  const pp = C.yawObj ? C.yawObj.position : T1.set(0, 0, 0);
  const pts = A.spawnPoints || [];
  let sp = null;
  for (let i = 0; i < 12; i++) {
    const cand = pts.length ? pts[(Math.random() * pts.length) | 0] : null;
    if (!cand) break;
    sp = cand;
    if (cand.distanceTo(pp) > 25) break;
  }
  if (!sp) sp = new THREE.Vector3(0, 0, 40);
  g.position.copy(sp);
  const hp = t.hp * (1 + 0.08 * (wave - 1));
  const e = {
    g,
    type: t,
    hp,
    maxHp: hp,
    speed: t.spd * Math.min(1 + 0.04 * (wave - 1), 1.5),
    dmg: t.dmg,
    nextShot: C.state.time + Math.random() * 1.5,
    burstLeft: 0,
    burstNext: 0,
    flashT: 0,
    spawnT: 0.35,
    baseScale: t.scale,
    mat: parts.mat,
    vmat: parts.vmat,
    head: parts.head,
    muzzle: parts.muzzle
  };
  g.userData.enemyRef = e;
  list.push(e);
  C.scene.add(g);
  return e;
}

function collideCircle(pos, r) {
  const cols = A.colliders || [];
  for (let i = 0; i < cols.length; i++) {
    const c = cols[i];
    let minX, maxX, minZ, maxZ;
    if (c.min !== undefined && c.max !== undefined) {
      minX = c.min.x; maxX = c.max.x; minZ = c.min.z; maxZ = c.max.z;
    } else {
      const cx = c.x !== undefined ? c.x : (c.position ? c.position.x : 0);
      const cz = c.z !== undefined ? c.z : (c.position ? c.position.z : 0);
      const hx = c.hx !== undefined ? c.hx : (c.hw !== undefined ? c.hw : (c.w !== undefined ? c.w * 0.5 : 1));
      const hz = c.hz !== undefined ? c.hz : (c.hd !== undefined ? c.hd : (c.d !== undefined ? c.d * 0.5 : 1));
      minX = cx - hx; maxX = cx + hx; minZ = cz - hz; maxZ = cz + hz;
    }
    const nx = Math.max(minX, Math.min(pos.x, maxX));
    const nz = Math.max(minZ, Math.min(pos.z, maxZ));
    const dx = pos.x - nx;
    const dz = pos.z - nz;
    const d2 = dx * dx + dz * dz;
    if (d2 > r * r) continue;
    if (d2 > 1e-8) {
      const d = Math.sqrt(d2);
      const pen = r - d;
      pos.x += (dx / d) * pen;
      pos.z += (dz / d) * pen;
    } else {
      const l = pos.x - minX, rr = maxX - pos.x, tt = pos.z - minZ, bb = maxZ - pos.z;
      const m = Math.min(l, rr, tt, bb);
      if (m === l) pos.x = minX - r;
      else if (m === rr) pos.x = maxX + r;
      else if (m === tt) pos.z = minZ - r;
      else pos.z = maxZ + r;
    }
  }
}

function fire(e, dist) {
  e.muzzle.getWorldPosition(T1);
  C.camera.getWorldPosition(T2);
  const spd = P.speed2D ? P.speed2D() : 0;
  const acc = clamp(0.8 - dist * 0.018 - spd * 0.02, 0.15, 0.85);
  if (Math.random() < acc) {
    T3.copy(T2);
    T3.x += (Math.random() - 0.5) * 0.3;
    T3.y += (Math.random() - 0.5) * 0.3;
    T3.z += (Math.random() - 0.5) * 0.3;
    if (P.damage) P.damage(e.dmg + (Math.random() * 4 - 2), e.g.position);
  } else {
    T3.copy(T2).sub(e.g.position);
    T3.y = 0;
    if (T3.lengthSq() < 1e-6) T3.set(1, 0, 0);
    T3.normalize();
    const off = (Math.random() * 2 - 1) * 1.2;
    const ox = -T3.z * off;
    const oz = T3.x * off;
    T3.copy(T2);
    T3.x += ox;
    T3.z += oz;
    T3.y += (Math.random() - 0.5) * 0.8;
  }
  if (FX.tracer) FX.tracer(T1, T3, 0xff5040, 0.06);
  if (FX.particles) FX.particles(T1, 3, { color: 0xffc080, speed: 4, life: 0.12, size: 0.05 });
  if (AU.enemyShot) AU.enemyShot(dist);
}

function attackCheck(e, dist, time, wave) {
  e.head.getWorldPosition(T1);
  C.camera.getWorldPosition(T2);
  T3.copy(T2).sub(T1);
  const dTot = T3.length();
  if (dTot < 1e-4) return;
  T3.divideScalar(dTot);
  ray.set(T1, T3);
  ray.far = dTot;
  const hits = ray.intersectObjects(A.obstacleMeshes || [], false);
  if (hits.length > 0 && hits[0].distance < dTot - 0.5) return;
  if (e.burstLeft > 0) {
    if (time >= e.burstNext) {
      fire(e, dist);
      e.burstNext = time + 0.13;
      e.burstLeft--;
    }
  } else if (time >= e.nextShot) {
    e.burstLeft = 3;
    e.burstNext = time;
    e.nextShot = time + (1.3 + Math.random() * 0.6) * Math.max(1 - wave * 0.03, 0.65);
  }
}

function disposeEnemy(e) {
  C.scene.remove(e.g);
  e.g.traverse(o => {
    if (!o.isMesh) return;
    if (o.geometry) o.geometry.dispose();
    const m = o.material;
    if (Array.isArray(m)) m.forEach(x => x.dispose());
    else if (m) m.dispose();
  });
}

function die(e) {
  const p = e.g.position;
  T1.set(p.x, p.y + 1, p.z);
  if (FX.particles) {
    FX.particles(T1, 16, { color: 0xff7733, speed: 6, life: 0.5, size: 0.09, gravity: -9 });
    FX.particles(T1, 6, { color: 0x3a3a3a, speed: 1.2, life: 0.9, size: 0.22, gravity: 1 });
  }
  try { AU.kill(); } catch (_) {}
  C.state.kills = (C.state.kills || 0) + 1;
  try { UI.killFeed(e.type.name + ' down'); } catch (_) {}
  try { G.director.onKill(p); } catch (_) {}
  disposeEnemy(e);
  const i = list.indexOf(e);
  if (i >= 0) list.splice(i, 1);
}

function update() {
  if (!C.state.playing) return;
  const time = C.state.time;
  const dt = C.state.dt || 0;
  const wave = Math.max(1, C.state.wave || 1);
  const pp = C.yawObj ? C.yawObj.position : T1.set(0, 0, 0);
  for (let i = 0; i < list.length; i++) {
    const e = list[i];
    if (e.flashT > 0) {
      e.flashT -= dt;
      if (e.flashT > 0) {
        e.mat.emissive.setHex(0xffffff);
        e.mat.emissiveIntensity = 2 * (e.flashT / 0.09);
      } else {
        e.mat.emissive.setHex(0x000000);
        e.mat.emissiveIntensity = 1;
      }
    }
    if (e.spawnT > 0) {
      e.spawnT -= dt;
      e.g.scale.y = e.baseScale * clamp(1 - Math.max(e.spawnT, 0) / 0.35, 0, 1);
      if (e.spawnT > 0) continue;
      e.g.scale.y = e.baseScale;
    }
    e.g.lookAt(pp.x, e.g.position.y, pp.z);
  }
  for (let i = 0; i < list.length; i++) {
    for (let j = i + 1; j < list.length; j++) {
      const pa = list[i].g.position;
      const pb = list[j].g.position;
      const dx = pb.x - pa.x;
      const dz = pb.z - pa.z;
      const d2 = dx * dx + dz * dz;
      if (d2 < 1.69 && d2 > 1e-6) {
        const d = Math.sqrt(d2);
        const push = (1.3 - d) * 0.5 / d;
        pa.x -= dx * push; pa.z -= dz * push;
        pb.x += dx * push; pb.z += dz * push;
      } else if (d2 <= 1e-6) {
        pa.x += 0.05;
        pb.x -= 0.05;
      }
    }
  }
  for (let i = list.length - 1; i >= 0; i--) {
    const e = list[i];
    const gp = e.g.position;
    const dx = pp.x - gp.x;
    const dz = pp.z - gp.z;
    const dist = Math.hypot(dx, dz);
    if (dist > 11 && dist > 1e-4) {
      gp.x += (dx / dist) * e.speed * dt;
      gp.z += (dz / dist) * e.speed * dt;
      collideCircle(gp, 0.45);
      gp.x = clamp(gp.x, -76, 76);
      gp.z = clamp(gp.z, -76, 76);
    }
    if (dist < 28) attackCheck(e, dist, time, wave);
  }
}

function applyDamage(e, dmg, isHead) {
  if (!e || e.hp <= 0) return false;
  e.hp -= dmg * (isHead ? 2.2 : 1);
  e.flashT = 0.09;
  if (e.hp <= 0) {
    die(e);
    return true;
  }
  return false;
}

function applyExplosion(pos, radius, maxDmg) {
  const snapshot = list.slice();
  for (let i = 0; i < snapshot.length; i++) {
    const e = snapshot[i];
    T1.set(e.g.position.x, e.g.position.y + 1, e.g.position.z);
    const d = T1.distanceTo(pos);
    if (d < radius) applyDamage(e, maxDmg * (1 - d / radius), false);
  }
}

function hittables() {
  const out = [];
  for (let i = 0; i < list.length; i++) {
    list[i].g.traverse(o => {
      if (o.isMesh) out.push(o);
    });
  }
  return out;
}

function clearAll() {
  for (let i = 0; i < list.length; i++) disposeEnemy(list[i]);
  list.length = 0;
}

function aliveCount() {
  return list.length;
}

C.registerUpdate(update, 20);

G.enemies = { list, spawn, clearAll, applyDamage, applyExplosion, hittables, aliveCount };
})();
