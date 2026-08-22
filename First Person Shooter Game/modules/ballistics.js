(() => {
  const G = window.GAME;
  const T = THREE;

  const raycaster = new T.Raycaster();
  raycaster.far = 300;

  const NOSE_DIR = new T.Vector3(0, 0, -1);
  const _dir = new T.Vector3();
  const _end = new T.Vector3();
  const _near = new T.Vector3();
  const _boom = new T.Vector3();

  const rockets = [];
  let template = null;

  function glowTexture() {
    const cv = document.createElement('canvas');
    cv.width = 64;
    cv.height = 64;
    const ctx = cv.getContext('2d');
    const grd = ctx.createRadialGradient(32, 32, 2, 32, 32, 32);
    grd.addColorStop(0, 'rgba(255,236,204,1)');
    grd.addColorStop(0.35, 'rgba(255,152,72,0.62)');
    grd.addColorStop(1, 'rgba(255,110,40,0)');
    ctx.fillStyle = grd;
    ctx.fillRect(0, 0, 64, 64);
    return new T.CanvasTexture(cv);
  }

  function rocketTemplate() {
    if (template) return template;
    const g = new T.Group();
    const bodyGeo = new T.CylinderGeometry(0.05, 0.05, 0.5, 10);
    bodyGeo.rotateX(Math.PI / 2);
    const body = new T.Mesh(
      bodyGeo,
      new T.MeshStandardMaterial({ color: 0x3a3f47, metalness: 0.85, roughness: 0.35 })
    );
    g.add(body);
    const noseGeo = new T.ConeGeometry(0.055, 0.16, 12);
    noseGeo.rotateX(-Math.PI / 2);
    const nose = new T.Mesh(
      noseGeo,
      new T.MeshStandardMaterial({ color: 0x7a2f1a, roughness: 0.55 })
    );
    nose.position.z = -0.33;
    g.add(nose);
    const flame = new T.Sprite(new T.SpriteMaterial({
      map: glowTexture(),
      color: 0xffa860,
      blending: T.AdditiveBlending,
      transparent: true,
      depthWrite: false
    }));
    flame.scale.setScalar(0.42);
    flame.position.z = 0.34;
    g.add(flame);
    template = g;
    return g;
  }

  function findEnemyRef(node) {
    while (node) {
      if (node.userData && node.userData.enemyRef) return node.userData.enemyRef;
      node = node.parent;
    }
    return null;
  }

  function fireHitscan(origin, dir, dmg, opts) {
    _dir.copy(dir).normalize();
    raycaster.set(origin, _dir);
    const targets = [G.arena.ground, ...G.arena.obstacleMeshes, ...G.enemies.hittables()];
    const hits = raycaster.intersectObjects(targets, true);
    let hit = null;
    for (let i = 0; i < hits.length; i++) {
      const o = hits[i].object;
      if (o.isSprite || o.isLine) continue;
      hit = hits[i];
      break;
    }
    if (!hit) {
      _end.copy(_dir).multiplyScalar(120).add(origin);
      if (opts && opts.fromPlayer) G.fx.tracer(origin, _end, 0xffd28a, 0.05);
      return null;
    }
    _end.copy(hit.point);
    const enemy = findEnemyRef(hit.object);
    let killed = false;
    if (enemy) {
      killed = G.enemies.applyDamage(enemy, dmg, hit.object.userData.part === 'head');
      G.fx.impactSpark(_end, 0x9fd0ff);
      G.ui.hitmarker(killed);
    } else {
      G.fx.impactSpark(_end, 0xffcf90);
    }
    if (opts && opts.fromPlayer) G.fx.tracer(origin, _end, 0xffd28a, 0.05);
    return { enemy: enemy, killed: killed, point: _end };
  }

  function spawnRocket(origin, dir) {
    const g = rocketTemplate().clone();
    const vel = dir.clone().normalize().multiplyScalar(46);
    g.position.copy(origin);
    g.quaternion.setFromUnitVectors(NOSE_DIR, _dir.copy(vel).normalize());
    G.scene.add(g);
    rockets.push({ g: g, vel: vel, life: 6, smokeT: 0 });
    return g;
  }

  function removeAt(i) {
    G.scene.remove(rockets[i].g);
    rockets.splice(i, 1);
  }

  function nearEnemy(p) {
    if (!G.enemies || !G.enemies.list) return false;
    const list = G.enemies.list;
    for (let i = 0; i < list.length; i++) {
      const e = list[i];
      const ep = e.position || (e.group && e.group.position) ||
        (e.mesh && e.mesh.position) || (e.g && e.g.position);
      if (!ep) continue;
      _near.set(ep.x, ep.y, ep.z);
      if (_near.distanceToSquared(p) < 1.44) return true;
    }
    return false;
  }

  function insideCollider(p) {
    const cols = G.arena.colliders;
    for (let i = 0; i < cols.length; i++) {
      const c = cols[i];
      if (
        p.x > c.x0 - 0.35 && p.x < c.x1 + 0.35 &&
        p.z > c.z0 - 0.35 && p.z < c.z1 + 0.35 &&
        p.y < c.h + 0.35
      ) return true;
    }
    return false;
  }

  function updateRockets() {
    if (!G.core.state.playing) return;
    const dt = G.core.state.dt || 0;
    const bound = G.arena.BOUND;
    for (let i = rockets.length - 1; i >= 0; i--) {
      const r = rockets[i];
      r.life -= dt;
      r.smokeT += dt;
      const p = r.g.position;
      p.addScaledVector(r.vel, dt);
      while (r.smokeT >= 0.025) {
        r.smokeT -= 0.025;
        G.fx.particles(p, {
          count: 1,
          color: 0x969ba3,
          size: 0.15,
          speed: 0.4,
          life: 0.55,
          grow: 2.6,
          gravity: -0.25,
          blending: T.NormalBlending
        });
      }
      const out =
        p.y < 0.06 ||
        Math.abs(p.x) > bound + 1 ||
        Math.abs(p.z) > bound + 1 ||
        r.life <= 0;
      if (out || nearEnemy(p) || insideCollider(p)) {
        _boom.set(
          Math.min(bound, Math.max(-bound, p.x)),
          Math.max(0.05, p.y),
          Math.min(bound, Math.max(-bound, p.z))
        );
        removeAt(i);
        explode(_boom);
      }
    }
  }

  function explode(pos, radius = 7.5, maxDmg = 165, fromPlayer = true) {
    G.fx.explosion(pos);
    G.audio.explosion();
    G.enemies.applyExplosion(pos, radius, fromPlayer ? maxDmg : maxDmg * 0.55);
    G.player.explosionDamage(pos);
  }

  function reset() {
    for (let i = rockets.length - 1; i >= 0; i--) removeAt(i);
  }

  G.ballistics = { fireHitscan, spawnRocket, explode, reset };
  G.core.registerUpdate(updateRockets, 30);
})();
