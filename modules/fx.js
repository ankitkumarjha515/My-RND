(() => {
  const G = window.GAME;
  const T = THREE;
  const C = G.core;

  function glowTexture() {
    const cv = document.createElement('canvas');
    cv.width = 64;
    cv.height = 64;
    const ctx = cv.getContext('2d');
    const g = ctx.createRadialGradient(32, 32, 1, 32, 32, 32);
    g.addColorStop(0, 'rgba(255,255,255,1)');
    g.addColorStop(.35, 'rgba(255,255,255,.55)');
    g.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, 64, 64);
    return new T.CanvasTexture(cv);
  }

  const TEX = glowTexture();
  const POOL = [];
  const LIVE = [];
  const LINES = [];
  let flashLight = null;

  function makeSprite() {
    const m = new T.SpriteMaterial({
      map: TEX,
      color: 0xffffff,
      transparent: true,
      opacity: 1,
      depthWrite: false
    });
    const s = new T.Sprite(m);
    s.visible = false;
    C.scene.add(s);
    return s;
  }

  function take() {
    if (POOL.length) return POOL.pop();
    return makeSprite();
  }

  function spawnParticle(x, y, z, vx, vy2, vz, o) {
    const s = take();
    s.position.set(x, y, z);
    s.material.color.setHex(o.color);
    s.material.blending = o.additive ? T.AdditiveBlending : T.NormalBlending;
    s.material.opacity = o.opacity !== undefined ? o.opacity : 1;
    s.scale.setScalar(o.size);
    s.visible = true;
    LIVE.push({
      s: s,
      vx: vx,
      vy: vy2,
      vz: vz,
      age: 0,
      life: o.life,
      size: o.size,
      grow: o.grow || 0,
      grav: o.gravity !== undefined ? o.gravity : -9,
      baseOp: o.opacity !== undefined ? o.opacity : 1,
      drag: o.drag || 0
    });
  }

  function particles(pos, a, b) {
    let count, opts;
    if (typeof a === 'number') {
      count = a;
      opts = b || {};
    } else {
      opts = a || {};
      count = opts.count || 8;
    }
    for (let i = 0; i < count; i++) {
      let dx = Math.random() * 2 - 1;
      let dy = Math.random() * 2 - 1;
      let dz = Math.random() * 2 - 1;
      const l = Math.hypot(dx, dy, dz) || 1;
      dx /= l; dy /= l; dz /= l;
      const sp = (opts.speed || 5) * (.35 + Math.random() * .65);
      spawnParticle(
        pos.x + dx * .05,
        pos.y + dy * .05,
        pos.z + dz * .05,
        dx * sp,
        dy * sp + (opts.up || 0),
        dz * sp,
        {
          color: opts.color !== undefined ? opts.color : 0xffffff,
          additive: opts.blending !== T.NormalBlending,
          opacity: opts.opacity,
          life: (opts.life || .4) * (.7 + Math.random() * .6),
          size: (opts.size || .08) * (.7 + Math.random() * .6),
          grow: opts.grow,
          gravity: opts.gravity,
          drag: opts.drag
        }
      );
    }
  }

  function tracer(from, to, color, width) {
    try {
      const geo = new T.BufferGeometry().setFromPoints([from.clone(), to.clone()]);
      const mat = new T.LineBasicMaterial({
        color: color !== undefined ? color : 0xffd28a,
        transparent: true,
        opacity: .9,
        blending: T.AdditiveBlending,
        depthWrite: false
      });
      const line = new T.Line(geo, mat);
      C.scene.add(line);
      LINES.push({ line: line, age: 0, life: width > .06 ? .09 : .07 });
    } catch (err) {
      console.error('GAME.fx.tracer:', err);
    }
  }

  function muzzleFlash(pos, scale) {
    const sc = scale || 1;
    spawnParticle(pos.x, pos.y, pos.z, 0, 0, 0, {
      color: 0xffe2a8,
      additive: true,
      life: .05,
      size: .38 * sc,
      gravity: 0
    });
    particles(pos, 3, { color: 0xffd9a0, speed: 6, life: .08, size: .04 });
  }

  function impactSpark(pos, color) {
    particles(pos, { count: 5, color: color !== undefined ? color : 0xffcf90, speed: 4.5, life: .22, size: .05 });
    spawnParticle(pos.x, pos.y, pos.z, 0, 0, 0, {
      color: 0xfff3d6,
      additive: true,
      life: .06,
      size: .14,
      gravity: 0
    });
  }

  function explosion(pos) {
    spawnParticle(pos.x, pos.y, pos.z, 0, 0, 0, {
      color: 0xffd9a0,
      additive: true,
      life: .28,
      size: 5.5,
      grow: 9,
      gravity: 0
    });
    particles(pos, { count: 34, color: 0xff8830, speed: 11, life: .55, size: .16, up: 3 });
    particles(pos, { count: 12, color: 0x55585c, speed: 3.2, life: 1.15, size: .5, grow: 2.6, gravity: -.6, blending: T.NormalBlending, opacity: .55 });
    particles(pos, { count: 10, color: 0xffe08a, speed: 14, life: .3, size: .08 });
    if (!flashLight) {
      flashLight = new T.PointLight(0xffa050, 0, 40);
      C.scene.add(flashLight);
    }
    flashLight.position.copy(pos);
    flashLight.position.y += .6;
    flashLight.intensity = 260;
  }

  function update(dt) {
    for (let i = LIVE.length - 1; i >= 0; i--) {
      const p = LIVE[i];
      p.age += dt;
      if (p.age >= p.life) {
        p.s.visible = false;
        POOL.push(p.s);
        LIVE.splice(i, 1);
        continue;
      }
      p.vy += p.grav * dt;
      if (p.drag) {
        const d = Math.exp(-p.drag * dt);
        p.vx *= d; p.vy *= d; p.vz *= d;
      }
      p.s.position.x += p.vx * dt;
      p.s.position.y += p.vy * dt;
      p.s.position.z += p.vz * dt;
      const t = p.age / p.life;
      p.s.material.opacity = p.baseOp * (1 - t);
      if (p.grow) p.s.scale.setScalar(p.size * (1 + p.grow * t));
    }
    for (let i = LINES.length - 1; i >= 0; i--) {
      const L = LINES[i];
      L.age += dt;
      if (L.age >= L.life) {
        C.scene.remove(L.line);
        L.line.geometry.dispose();
        L.line.material.dispose();
        LINES.splice(i, 1);
        continue;
      }
      L.line.material.opacity = .9 * (1 - L.age / L.life);
    }
    if (flashLight && flashLight.intensity > 0) {
      flashLight.intensity = Math.max(0, flashLight.intensity - dt * 900);
    }
  }

  C.registerUpdate(update, 50);

  G.fx = { particles, tracer, muzzleFlash, impactSpark, explosion };
})();
