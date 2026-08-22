(() => {
  const G = window.GAME;
  const T = window.THREE;
  if (!G || !T) throw new Error('GAME.core: bootstrap missing');

  const host = document.getElementById('game');
  if (!host) console.warn('GAME.core: #game div not found, appending to body');

  const renderer = new T.WebGLRenderer({
    antialias: true,
    powerPreference: 'high-performance'
  });
  const baseRatio = Math.min(window.devicePixelRatio || 1, 1.5);
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(baseRatio);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = T.PCFSoftShadowMap;
  renderer.toneMapping = T.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  (host || document.body).appendChild(renderer.domElement);

  const scene = new T.Scene();
  scene.background = new T.Color(0x141a24);
  scene.fog = new T.Fog(0x141a24, 40, 150);

  const yawObj = new T.Object3D();
  yawObj.position.set(0, 1.7, 18);
  const camera = new T.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.05, 400);
  yawObj.add(camera);
  scene.add(yawObj);

  const hemi = new T.HemisphereLight(0x8899bb, 0x332a20, 0.9);
  scene.add(hemi);

  const sun = new T.DirectionalLight(0xffd9a0, 1.6);
  sun.position.set(40, 70, 25);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  sun.shadow.camera.left = -85;
  sun.shadow.camera.right = 85;
  sun.shadow.camera.top = 85;
  sun.shadow.camera.bottom = -85;
  sun.shadow.camera.near = 1;
  sun.shadow.camera.far = 200;
  sun.shadow.bias = -0.0004;
  scene.add(sun);

  const state = {
    time: 0,
    dt: 0,
    playing: false,
    dead: false,
    started: false,
    kills: 0,
    wave: 1
  };

  const V1 = new T.Vector3();
  const V2 = new T.Vector3();
  const V3 = new T.Vector3();

  const updates = [];
  const errored = new Set();

  function registerUpdate(fn, priority) {
    if (typeof fn !== 'function') {
      console.error('GAME.core.registerUpdate: fn is not a function');
      return;
    }
    updates.push({ fn: fn, priority: priority ?? 100 });
  }

  if (Array.isArray(G._updates)) {
    for (const entry of G._updates) {
      if (typeof entry === 'function') registerUpdate(entry, 100);
      else if (entry && typeof entry.fn === 'function') registerUpdate(entry.fn, entry.priority);
    }
    G._updates.length = 0;
  }

  const clock = new T.Clock();
  let winFrames = 0;
  let winMs = 0;

  function setPlaying(b) {
    const next = b === true;
    if (state.playing === next) return;
    state.playing = next;
    if (next) clock.getDelta();
  }

  function stepRatio(delta) {
    const current = renderer.getPixelRatio();
    const next = Math.min(baseRatio, Math.max(0.75, current + delta));
    if (Math.abs(next - current) < 0.001) return false;
    renderer.setPixelRatio(next);
    console.log('GAME.core: pixelRatio ->', next.toFixed(2));
    return true;
  }

  function trackFrame(ms) {
    if (ms > 500) {
      winFrames = 0;
      winMs = 0;
      return;
    }
    winMs += ms;
    winFrames++;
    if (winFrames < 90) return;
    const avg = winMs / winFrames;
    let acted = false;
    if (avg > 24) acted = stepRatio(-0.15);
    else if (winFrames >= 240 && avg < 14) acted = stepRatio(0.15);
    if (acted || winFrames >= 240) {
      winFrames = 0;
      winMs = 0;
    }
  }

  renderer.setAnimationLoop(() => {
    const rawDt = clock.getDelta();
    const dt = Math.min(rawDt, 0.05);
    state.dt = dt;
    state.time += dt;
    updates.sort((a, b) => a.priority - b.priority);
    for (const u of updates) {
      try {
        u.fn(dt, state.time);
      } catch (err) {
        if (!errored.has(u.fn)) {
          errored.add(u.fn);
          console.error('GAME.core: update crashed:', err);
        }
      }
    }
    trackFrame(rawDt * 1000);
    renderer.render(scene, camera);
  });

  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  document.addEventListener('visibilitychange', () => {
    if (document.hidden && state.playing) setPlaying(false);
  });

  G.core = {
    scene: scene,
    camera: camera,
    renderer: renderer,
    yawObj: yawObj,
    canvas: renderer.domElement,
    state: state,
    registerUpdate: registerUpdate,
    V1: V1,
    V2: V2,
    V3: V3,
    setPlaying: setPlaying
  };
  G.registerUpdate = registerUpdate;
})();
