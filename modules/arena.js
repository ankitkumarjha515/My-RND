(() => {
  const G = window.GAME;
  const T = THREE;
  const scene = G.scene;
  const arena = {};
  const colliders = [];
  const obstacleMeshes = [];
  const spawnPoints = [];

  function maxAniso() {
    return G.renderer && G.renderer.capabilities ? Math.min(8, G.renderer.capabilities.getMaxAnisotropy()) : 1;
  }

  // ---- procedural sky dome (replaces flat background) ----
  const SKY_TOP = new T.Color(0x24344e);
  const SKY_MID = new T.Color(0x66788f);
  const SKY_BOT = new T.Color(0x8f8674);
  const skyMat = new T.ShaderMaterial({
    side: T.BackSide,
    depthWrite: false,
    uniforms: { top: { value: SKY_TOP }, mid: { value: SKY_MID }, bot: { value: SKY_BOT } },
    vertexShader: 'varying vec3 vP;void main(){vP=position;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',
    fragmentShader: 'varying vec3 vP;uniform vec3 top,mid,bot;void main(){float h=normalize(vP).y;vec3 c=h>0.?mix(mid,top,pow(min(h*1.8,1.),.72)):mix(mid,bot,min(-h*3.,1.));gl_FragColor=vec4(c,1.);}'
  });
  scene.add(new T.Mesh(new T.SphereGeometry(340, 24, 12), skyMat));
  scene.background = null;
  scene.fog = new T.Fog(0x66788f, 55, 190);

  // ---- free environment reflections generated from the sky itself ----
  try {
    const pmrem = new T.PMREMGenerator(G.renderer);
    const es = new T.Scene();
    const sm = skyMat.clone();
    es.add(new T.Mesh(new T.SphereGeometry(50, 16, 10), sm));
    scene.environment = pmrem.fromScene(es, .07).texture;
    pmrem.dispose();
    sm.dispose();
  } catch (err) {
    console.error('GAME.arena: envmap failed:', err);
  }

  // ---- retune the core lights for a late-afternoon look ----
  let sun = null;
  let hemi = null;
  for (const o of scene.children) {
    if (!sun && o.isDirectionalLight) sun = o;
    else if (!hemi && o.isHemisphereLight) hemi = o;
  }
  if (sun) {
    sun.position.set(52, 38, -34);
    sun.intensity = 2.35;
    sun.color.setHex(0xffdcae);
    if (sun.shadow) {
      sun.shadow.normalBias = .04;
      sun.shadow.bias = -.0003;
    }
  } else {
    console.warn('GAME.arena: sun light not found');
  }
  if (hemi) {
    hemi.color.setHex(0x9fb2cc);
    hemi.groundColor.setHex(0x4d4232);
    hemi.intensity = .65;
  }

  // ---- sun glow on the horizon ----
  try {
    const gc = document.createElement('canvas');
    gc.width = gc.height = 64;
    const gx = gc.getContext('2d');
    const gg = gx.createRadialGradient(32, 32, 1, 32, 32, 32);
    gg.addColorStop(0, 'rgba(255,240,214,1)');
    gg.addColorStop(.4, 'rgba(255,205,140,.45)');
    gg.addColorStop(1, 'rgba(255,190,120,0)');
    gx.fillStyle = gg;
    gx.fillRect(0, 0, 64, 64);
    const gs = new T.Sprite(new T.SpriteMaterial({
      map: new T.CanvasTexture(gc),
      color: 0xffe8c0,
      transparent: true,
      opacity: .85,
      blending: T.AdditiveBlending,
      depthWrite: false,
      fog: false
    }));
    gs.position.copy(sun ? sun.position : new T.Vector3(52, 38, -34)).normalize().multiplyScalar(300);
    gs.scale.setScalar(95);
    scene.add(gs);
  } catch (err) {
    console.error('GAME.arena: sun glow failed:', err);
  }

  // ---- canvas texture helpers (all runtime-generated: 0 KB shipped) ----
  function speckle(c, S, amt) {
    const img = c.getImageData(0, 0, S, S);
    const d = img.data;
    for (let i = 0; i < d.length; i += 4) {
      const n = (Math.random() - .5) * amt;
      d[i] += n; d[i + 1] += n; d[i + 2] += n;
    }
    c.putImageData(img, 0, 0);
  }

  function normalFromCanvas(srcCv, strength) {
    const S = srcCv.width;
    const d = srcCv.getContext('2d').getImageData(0, 0, S, S).data;
    const ncv = document.createElement('canvas');
    ncv.width = ncv.height = S;
    const nx = ncv.getContext('2d');
    const out = nx.createImageData(S, S);
    const H = (x, y) => d[(((y + S) % S) * S + ((x + S) % S)) * 4] / 255;
    const st = strength || 1.5;
    for (let y = 0; y < S; y++) {
      for (let x = 0; x < S; x++) {
        const vx = (H(x - 1, y) - H(x + 1, y)) * st;
        const vy = (H(x, y - 1) - H(x, y + 1)) * st;
        const l = Math.hypot(vx, vy, 1);
        const i = (y * S + x) * 4;
        out.data[i] = ((vx / l) * .5 + .5) * 255;
        out.data[i + 1] = ((vy / l) * .5 + .5) * 255;
        out.data[i + 2] = ((1 / l) * .5 + .5) * 255;
        out.data[i + 3] = 255;
      }
    }
    nx.putImageData(out, 0, 0);
    const t = new T.CanvasTexture(ncv);
    t.wrapS = t.wrapT = T.RepeatWrapping;
    return t;
  }

  function repeatOf(tex, rx, ry) {
    tex.wrapS = tex.wrapT = T.RepeatWrapping;
    tex.repeat.set(rx, ry);
    tex.colorSpace = T.SRGBColorSpace;
    tex.anisotropy = maxAniso();
    return tex;
  }

  // ---- ground: weathered asphalt/dirt with generated normal map ----
  const GS = 512;
  const gCv = document.createElement('canvas');
  gCv.width = gCv.height = GS;
  {
    const c = gCv.getContext('2d');
    c.fillStyle = '#44433c';
    c.fillRect(0, 0, GS, GS);
    for (let i = 0; i < 2600; i++) {
      const v = Math.random();
      c.fillStyle = 'rgba(' + ((48 + v * 50) | 0) + ',' + ((46 + v * 46) | 0) + ',' + ((40 + v * 38) | 0) + ',' + (.05 + Math.random() * .15).toFixed(3) + ')';
      c.beginPath();
      c.arc(Math.random() * GS, Math.random() * GS, 2 + Math.random() * 13, 0, 6.283);
      c.fill();
    }
    c.strokeStyle = 'rgba(22,22,19,.55)';
    for (let i = 0; i < 26; i++) {
      c.lineWidth = .4 + Math.random() * 1.3;
      c.beginPath();
      let x = Math.random() * GS;
      let y = Math.random() * GS;
      c.moveTo(x, y);
      const seg = 3 + ((Math.random() * 5) | 0);
      for (let s = 0; s < seg; s++) {
        x += (Math.random() - .5) * 54;
        y += (Math.random() - .5) * 54;
        c.lineTo(x, y);
      }
      c.stroke();
    }
    for (let i = 0; i < 14; i++) {
      c.fillStyle = 'rgba(30,28,24,' + (.05 + Math.random() * .08).toFixed(3) + ')';
      c.beginPath();
      c.ellipse(Math.random() * GS, Math.random() * GS, 20 + Math.random() * 60, 12 + Math.random() * 36, Math.random() * 3, 0, 6.283);
      c.fill();
    }
    speckle(c, GS, 20);
  }
  const groundTex = repeatOf(new T.CanvasTexture(gCv), 30, 30);
  const groundNrm = normalFromCanvas(gCv, 1.4);
  groundNrm.repeat.set(30, 30);

  const ground = new T.Mesh(
    new T.PlaneGeometry(170, 170),
    new T.MeshStandardMaterial({
      map: groundTex,
      normalMap: groundNrm,
      normalScale: new T.Vector2(.85, .85),
      roughness: .97,
      metalness: 0
    })
  );
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true;
  scene.add(ground);

  function addSolid(x, z, w, h, d, color, rough) {
    const mat = new T.MeshStandardMaterial({ color: color, roughness: rough === undefined ? 0.8 : rough });
    const m = new T.Mesh(new T.BoxGeometry(w, h, d), mat);
    m.position.set(x, h / 2, z);
    m.castShadow = true;
    m.receiveShadow = true;
    scene.add(m);
    obstacleMeshes.push(m);
    colliders.push({ x0: x - w / 2, x1: x + w / 2, z0: z - d / 2, z1: z + d / 2, h: h });
    return m;
  }

  // ---- perimeter barriers: stained concrete slabs ----
  const WS = 256;
  const wCv = document.createElement('canvas');
  wCv.width = wCv.height = WS;
  {
    const c = wCv.getContext('2d');
    c.fillStyle = '#77756e';
    c.fillRect(0, 0, WS, WS);
    for (let x = 0; x <= WS; x += 64) {
      c.fillStyle = 'rgba(40,40,38,.6)';
      c.fillRect(x - 1, 0, 2.5, WS);
      c.fillStyle = 'rgba(255,255,255,.09)';
      c.fillRect(x + 2, 0, 1.5, WS);
    }
    c.fillStyle = 'rgba(30,30,26,.18)';
    c.fillRect(0, WS - 26, WS, 26);
    for (let i = 0; i < 9; i++) {
      const sx = Math.random() * WS;
      const grd = c.createLinearGradient(sx, WS, sx, WS - 40 - Math.random() * 90);
      grd.addColorStop(0, 'rgba(42,38,30,.34)');
      grd.addColorStop(1, 'rgba(42,38,30,0)');
      c.fillStyle = grd;
      c.fillRect(sx - 8 - Math.random() * 10, 0, 16 + Math.random() * 20, WS);
    }
    speckle(c, WS, 16);
  }
  const wallTex = repeatOf(new T.CanvasTexture(wCv), 14, 1);
  const wallNrm = normalFromCanvas(wCv, 2.2);
  wallNrm.repeat.set(14, 1);
  const wallMat = new T.MeshStandardMaterial({
    map: wallTex,
    normalMap: wallNrm,
    normalScale: new T.Vector2(.7, .7),
    roughness: .92
  });

  const CONCRETE = 0xffffff;
  [[0, 78, 160, 6, 2], [0, -78, 160, 6, 2], [78, 0, 2, 6, 160], [-78, 0, 2, 6, 160]].forEach(w => {
    const m = addSolid(w[0], w[1], w[2], w[3], w[4], CONCRETE, .92);
    m.material = wallMat;
  });

  // ---- crates: wooden planks with braces ----
  const CS = 256;
  const cCv = document.createElement('canvas');
  cCv.width = cCv.height = CS;
  {
    const c = cCv.getContext('2d');
    c.fillStyle = '#7c5a34';
    c.fillRect(0, 0, CS, CS);
    const ph = CS / 5;
    for (let i = 0; i < 5; i++) {
      const tone = 108 + ((Math.random() * 34) | 0);
      c.fillStyle = 'rgb(' + ((tone * 1.25) | 0) + ',' + ((tone * .87) | 0) + ',' + ((tone * .52) | 0) + ')';
      c.fillRect(0, i * ph + 1, CS, ph - 2);
      c.fillStyle = 'rgba(30,18,8,.5)';
      for (let k = 0; k < 7; k++) {
        c.fillRect(Math.random() * CS, i * ph + Math.random() * ph, 8 + Math.random() * 30, 1.2);
      }
    }
    c.strokeStyle = '#4a3018';
    c.lineWidth = 18;
    c.strokeRect(9, 9, CS - 18, CS - 18);
    c.lineWidth = 13;
    c.beginPath();
    c.moveTo(14, 14);
    c.lineTo(CS - 14, CS - 14);
    c.moveTo(CS - 14, 14);
    c.lineTo(14, CS - 14);
    c.stroke();
    speckle(c, CS, 18);
  }
  const crateTex = repeatOf(new T.CanvasTexture(cCv), 1, 1);
  const crateNrm = normalFromCanvas(cCv, 2.6);
  const crateMat = new T.MeshStandardMaterial({
    map: crateTex,
    normalMap: crateNrm,
    normalScale: new T.Vector2(.8, .8),
    roughness: .85
  });

  const RUST = 0x6e3b23;
  const OLIVE = 0x4a5240;

  const crateDefs = [
    [10, 10, 3], [-10, -10, 3],
    [14, -12, 2.5], [-14, 12, 2.5],
    [26, 18, 4], [-26, -18, 4],
    [22, -32, 3], [-22, 32, 3],
    [48, 40, 2.5], [-48, -40, 2.5],
    [52, -46, 3], [-52, 46, 3],
    [44, -14, 2], [-44, 14, 2]
  ];
  crateDefs.forEach(cd => {
    const m = addSolid(cd[0], cd[1], cd[2], cd[2], cd[2], OLIVE);
    m.material = crateMat;
  });

  const GRAY = 0x565b64;
  addSolid(0, 20, 3, 1.2, 0.6, GRAY);
  addSolid(0, -20, 3, 1.2, 0.6, GRAY);
  addSolid(20, 0, 0.6, 1.2, 3, GRAY);
  addSolid(-20, 0, 0.6, 1.2, 3, GRAY);

  const bunkerMat = new T.MeshStandardMaterial({ color: OLIVE, roughness: .9 });
  [[38, 8, 5, 4, 5], [-38, -8, 5, 4, 5]].forEach(b => {
    const m = addSolid(b[0], b[1], b[2], b[3], b[4], OLIVE);
    m.material = bunkerMat;
  });

  [[68, 68], [-68, 68], [68, -68], [-68, -68], [0, 70], [0, -70], [70, 0], [-70, 0]].forEach(p => {
    spawnPoints.push(new T.Vector3(p[0], 0, p[1]));
  });

  const barrelGeo = new T.CylinderGeometry(0.45, 0.45, 1.1, 14);
  const barrelMats = [
    new T.MeshStandardMaterial({ color: 0x7a3327, roughness: 0.7 }),
    new T.MeshStandardMaterial({ color: 0x3f4a52, roughness: 0.7 })
  ];
  [[6, -4, 0], [7.2, -2.6, 0], [-6, 4, 1], [-7.2, 2.6, 1], [33, 25, 0], [-33, -25, 1]].forEach(b => {
    const m = new T.Mesh(barrelGeo, barrelMats[b[2]]);
    m.position.set(b[0], 0.55, b[1]);
    m.castShadow = true;
    m.receiveShadow = true;
    scene.add(m);
  });
  [[16, 24, 1], [-16, -24, 0]].forEach(b => {
    const m = new T.Mesh(barrelGeo, barrelMats[b[2]]);
    m.rotation.z = Math.PI / 2;
    m.position.set(b[0], 0.45, b[1]);
    m.castShadow = true;
    m.receiveShadow = true;
    scene.add(m);
  });

  const bagGeo = new T.BoxGeometry(1, 0.42, 0.55);
  const bagMat = new T.MeshStandardMaterial({ color: 0x6b6248, roughness: 1 });
  function sandbagRow(x, z, rotY) {
    const grp = new T.Group();
    [[3, 0], [2, 0.42], [1, 0.84]].forEach(row => {
      for (let i = 0; i < row[0]; i++) {
        const bag = new T.Mesh(bagGeo, bagMat);
        bag.position.set((i - (row[0] - 1) / 2) * 1.04, 0.21 + row[1], 0);
        bag.rotation.y = (Math.random() - 0.5) * 0.14;
        bag.castShadow = true;
        bag.receiveShadow = true;
        grp.add(bag);
      }
    });
    grp.position.set(x, 0, z);
    grp.rotation.y = rotY;
    scene.add(grp);
  }
  sandbagRow(-4, 34, 0);
  sandbagRow(4, -34, 0);
  sandbagRow(58, 12, Math.PI / 2);
  sandbagRow(-58, -12, Math.PI / 2);

  const lampLights = [];
  const poleGeo = new T.CylinderGeometry(0.07, 0.1, 5, 8);
  const poleMat = new T.MeshStandardMaterial({ color: 0x2a2d33, roughness: 0.6, metalness: 0.4 });
  const bulbGeo = new T.SphereGeometry(0.16, 10, 8);
  const bulbMat = new T.MeshStandardMaterial({ color: 0xffe6bd, emissive: 0xffc98a, emissiveIntensity: 2.2 });
  [[30, 30], [30, -30], [-30, 30], [-30, -30]].forEach((p, i) => {
    const pole = new T.Mesh(poleGeo, poleMat);
    pole.position.set(p[0], 2.5, p[1]);
    pole.castShadow = true;
    scene.add(pole);
    const bulb = new T.Mesh(bulbGeo, bulbMat);
    bulb.position.set(p[0], 5.06, p[1]);
    scene.add(bulb);
    const light = new T.PointLight(0xffc98a, 60, 22);
    light.position.set(p[0], 4.85, p[1]);
    scene.add(light);
    lampLights.push(light);
  });
  G.core.registerUpdate(() => {
    const t = G.core.state.time;
    for (let i = 0; i < lampLights.length; i++) {
      const l = lampLights[i];
      l.intensity = 60 * (0.93 + 0.05 * Math.sin(t * 11 + i * 2.1) + 0.03 * Math.sin(t * 43 + i * 5.7));
    }
  }, 80);

  // ---- drifting dust motes for atmosphere ----
  try {
    const DN = 150;
    const dp = new Float32Array(DN * 3);
    for (let i = 0; i < DN; i++) {
      dp[i * 3] = (Math.random() - .5) * 130;
      dp[i * 3 + 1] = Math.random() * 8 + .3;
      dp[i * 3 + 2] = (Math.random() - .5) * 130;
    }
    const dg = new T.BufferGeometry();
    dg.setAttribute('position', new T.BufferAttribute(dp, 3));
    const dust = new T.Points(dg, new T.PointsMaterial({
      color: 0xd8cba8,
      size: .09,
      transparent: true,
      opacity: .3,
      depthWrite: false,
      blending: T.AdditiveBlending
    }));
    scene.add(dust);
    G.core.registerUpdate((dt) => {
      const pos = dg.attributes.position;
      for (let i = 0; i < pos.count; i++) {
        let y = pos.getY(i) - dt * .28;
        let x = pos.getX(i) + Math.sin(G.core.state.time * .5 + i) * dt * .18;
        if (y < .2) y = 8.2;
        pos.setY(i, y);
        pos.setX(i, x);
      }
      pos.needsUpdate = true;
    }, 79);
  } catch (err) {
    console.error('GAME.arena: dust failed:', err);
  }

  const silMat = new T.MeshBasicMaterial({ color: 0x151a22, fog: false });
  const silDefs = [
    [96, 4, 12, 26, 9], [112, 34, 14, 18, 11], [-96, 12, 11, 30, 10], [-110, -28, 9, 20, 13],
    [4, 97, 30, 22, 9], [36, 106, 18, 28, 12], [-22, -99, 26, 24, 10], [52, -109, 12, 30, 14], [-62, 101, 10, 26, 11]
  ];
  silDefs.forEach(s => {
    const m = new T.Mesh(new T.BoxGeometry(s[2], s[3], s[4]), silMat);
    m.position.set(s[0], s[3] / 2, s[1]);
    scene.add(m);
  });

  arena.colliders = colliders;
  arena.obstacleMeshes = obstacleMeshes;
  arena.ground = ground;
  arena.BOUND = 76;
  arena.spawnPoints = spawnPoints;
  G.arena = arena;
})();
