(() => {
  const GAME = window.GAME;
  const core = GAME.core;
  const state = core.state;
  const ui = GAME.ui;
  const enemies = GAME.enemies;
  const player = GAME.player;
  const weapons = GAME.weapons;
  const audio = GAME.audio;

  const dir = {
    pickups: [],
    nextSpawn: 0,
    graceUntil: 0,
    lastWave: 1
  };

  function disposeRoot(root) {
    root.traverse(o => {
      if (o.geometry) {
        o.geometry.dispose();
      }
      if (o.material) {
        if (Array.isArray(o.material)) {
          o.material.forEach(m => m.dispose());
        } else {
          o.material.dispose();
        }
      }
    });
    if (root.parent) {
      root.parent.remove(root);
    }
  }

  function makeMedkit() {
    const g = new THREE.Group();
    const body = new THREE.Mesh(
      new THREE.BoxGeometry(.45, .45, .45),
      new THREE.MeshStandardMaterial({ color: 0x27ae60 })
    );
    const white = new THREE.MeshStandardMaterial({ color: 0xffffff });
    const barX = new THREE.Mesh(new THREE.BoxGeometry(.13, .47, .47), white);
    const barZ = new THREE.Mesh(new THREE.BoxGeometry(.47, .475, .135), white);
    g.add(body);
    g.add(barX);
    g.add(barZ);
    g.userData.kind = 'medkit';
    return g;
  }

  function makeAmmo() {
    const g = new THREE.Group();
    const body = new THREE.Mesh(
      new THREE.BoxGeometry(.42, .34, .42),
      new THREE.MeshStandardMaterial({ color: 0xe67e22 })
    );
    const lid = new THREE.Mesh(
      new THREE.BoxGeometry(.46, .12, .46),
      new THREE.MeshStandardMaterial({ color: 0x8c4b06 })
    );
    lid.position.y = .17;
    g.add(body);
    g.add(lid);
    g.userData.kind = 'ammo';
    return g;
  }

  function spawnPickup(pos) {
    if (dir.pickups.length >= 6) {
      return;
    }
    const kind = Math.random() < .5 ? 'medkit' : 'ammo';
    const mesh = kind === 'medkit' ? makeMedkit() : makeAmmo();
    mesh.position.set(pos.x, .5, pos.z);
    mesh.rotation.y = Math.random() * Math.PI * 2;
    core.scene.add(mesh);
    dir.pickups.push({
      mesh,
      kind,
      born: state.time
    });
  }

  function removeAt(i) {
    disposeRoot(dir.pickups[i].mesh);
    dir.pickups.splice(i, 1);
  }

  function clearPickups() {
    for (let i = dir.pickups.length - 1; i >= 0; i--) {
      removeAt(i);
    }
  }

  function update() {
    if (!state.playing || state.dead) {
      return;
    }
    const t = state.time;
    const dt = state.dt;
    const wave = 1 + Math.floor(state.kills / 6);
    if (wave !== dir.lastWave) {
      dir.lastWave = wave;
      state.wave = wave;
      ui.setWaveKills(wave, state.kills);
      ui.popup('WAVE ' + wave);
    }
    const maxAlive = Math.min(4 + wave, 11);
    const interval = Math.max(.75, 3 - wave * .22);
    if (t >= dir.graceUntil && t >= dir.nextSpawn && enemies.aliveCount() < maxAlive) {
      const roll = Math.random();
      const typeName = wave >= 3 && roll < .18 ? 'heavy' : wave >= 2 && roll < .5 ? 'scout' : 'grunt';
      enemies.spawn(typeName);
      dir.nextSpawn = t + interval;
    }
    const pp = player.yawObj.position;
    for (let i = dir.pickups.length - 1; i >= 0; i--) {
      const p = dir.pickups[i];
      p.mesh.rotation.y += 2 * dt;
      p.mesh.position.y = .5 + Math.sin(t * 3) * .08;
      if (t - p.born > 25) {
        removeAt(i);
        continue;
      }
      if (pp.distanceTo(p.mesh.position) < 1.6) {
        if (p.kind === 'medkit') {
          player.heal(35);
          ui.popup('+35 HP');
        } else {
          weapons.addAmmo(30, 1);
          ui.popup('+AMMO');
        }
        audio.pickup();
        removeAt(i);
      }
    }
  }

  function reset() {
    clearPickups();
    state.kills = 0;
    state.wave = 1;
    dir.lastWave = 1;
    ui.setWaveKills(1, 0);
    dir.graceUntil = state.time + 2.5;
    dir.nextSpawn = state.time + 2.5;
  }

  function onKill(pos) {
    if (Math.random() < .22) {
      spawnPickup(pos);
    }
  }

  state.kills = 0;
  state.wave = 1;
  core.registerUpdate(update, 40);

  GAME.director = { reset, onKill };

  try {
    ui.overlay('start', null);
  } catch (e) {}
})();
