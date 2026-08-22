(() => {
  const G = window.GAME;
  const T = THREE;
  const scene = G.scene;
  const arena = {};
  const colliders = [];
  const obstacleMeshes = [];
  const spawnPoints = [];

  const cv = document.createElement('canvas');
  cv.width = 256;
  cv.height = 256;
  const ctx = cv.getContext('2d');
  ctx.fillStyle = '#26262b';
  ctx.fillRect(0, 0, 256, 256);
  for (let i = 0; i < 4200; i++) {
    const v = (Math.random() * 255) | 0;
    const a = (Math.random() * 0.09).toFixed(3);
    ctx.fillStyle = 'rgba(' + v + ',' + v + ',' + v + ',' + a + ')';
    ctx.fillRect((Math.random() * 256) | 0, (Math.random() * 256) | 0, Math.random() < 0.2 ? 2 : 1, 1);
  }
  ctx.strokeStyle = 'rgba(255,255,255,0.05)';
  ctx.lineWidth = 1;
  for (let p = 0; p <= 256; p += 32) {
    ctx.beginPath();
    ctx.moveTo(p + 0.5, 0);
    ctx.lineTo(p + 0.5, 256);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(0, p + 0.5);
    ctx.lineTo(256, p + 0.5);
    ctx.stroke();
  }
  const groundTex = new T.CanvasTexture(cv);
  groundTex.wrapS = T.RepeatWrapping;
  groundTex.wrapT = T.RepeatWrapping;
  groundTex.repeat.set(40, 40);
  groundTex.colorSpace = T.SRGBColorSpace;
  if (G.renderer && G.renderer.capabilities) {
    groundTex.anisotropy = Math.min(8, G.renderer.capabilities.getMaxAnisotropy());
  }

  const ground = new T.Mesh(
    new T.PlaneGeometry(170, 170),
    new T.MeshStandardMaterial({ map: groundTex, roughness: 0.96, metalness: 0 })
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

  const CONCRETE = 0x4a4d55;
  addSolid(0, 78, 160, 6, 2, CONCRETE, 0.9);
  addSolid(0, -78, 160, 6, 2, CONCRETE, 0.9);
  addSolid(78, 0, 2, 6, 160, CONCRETE, 0.9);
  addSolid(-78, 0, 2, 6, 160, CONCRETE, 0.9);

  const RUST = 0x6e3b23;
  const OLIVE = 0x4a5240;
  const GRAY = 0x565b64;

  const crateDefs = [
    [10, 10, 3, RUST], [-10, -10, 3, RUST],
    [14, -12, 2.5, OLIVE], [-14, 12, 2.5, OLIVE],
    [26, 18, 4, GRAY], [-26, -18, 4, GRAY],
    [22, -32, 3, OLIVE], [-22, 32, 3, OLIVE],
    [48, 40, 2.5, RUST], [-48, -40, 2.5, RUST],
    [52, -46, 3, GRAY], [-52, 46, 3, GRAY],
    [44, -14, 2, RUST], [-44, 14, 2, RUST]
  ];
  crateDefs.forEach(c => addSolid(c[0], c[1], c[2], c[2], c[2], c[3]));

  addSolid(0, 20, 3, 1.2, 0.6, GRAY);
  addSolid(0, -20, 3, 1.2, 0.6, GRAY);
  addSolid(20, 0, 0.6, 1.2, 3, GRAY);
  addSolid(-20, 0, 0.6, 1.2, 3, GRAY);

  addSolid(38, 8, 5, 4, 5, OLIVE);
  addSolid(-38, -8, 5, 4, 5, OLIVE);

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

  const silMat = new T.MeshBasicMaterial({ color: 0x10131a });
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
