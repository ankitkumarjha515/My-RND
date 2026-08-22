(() => {
  const G = window.GAME;
  let ctx = null;
  let master = null;
  let noiseBuf = null;

  function unlock() {
    try {
      if (!ctx) {
        const AC = window.AudioContext || window.webkitAudioContext;
        if (!AC) {
          console.warn('GAME.audio: WebAudio not supported');
          return;
        }
        ctx = new AC();
        master = ctx.createGain();
        master.gain.value = .5;
        const comp = ctx.createDynamicsCompressor();
        comp.threshold.value = -18;
        comp.ratio.value = 6;
        master.connect(comp);
        comp.connect(ctx.destination);
        const len = Math.floor(ctx.sampleRate * 1.2);
        noiseBuf = ctx.createBuffer(1, len, ctx.sampleRate);
        const d = noiseBuf.getChannelData(0);
        for (let i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;
      }
      if (ctx.state === 'suspended') ctx.resume();
    } catch (err) {
      ctx = null;
      console.error('GAME.audio: init failed:', err);
    }
  }

  function ok() {
    return !!ctx && ctx.state === 'running';
  }

  function safe(fn) {
    if (!ok()) return;
    try {
      fn(ctx.currentTime);
    } catch (err) {
      console.error('GAME.audio:', err);
    }
  }

  function noise(t0, dur, type, f0, f1, vol, q) {
    const src = ctx.createBufferSource();
    src.buffer = noiseBuf;
    src.loop = true;
    src.playbackRate.value = .9 + Math.random() * .2;
    const flt = ctx.createBiquadFilter();
    flt.type = type;
    flt.Q.value = q || .8;
    flt.frequency.setValueAtTime(Math.max(30, f0), t0);
    flt.frequency.exponentialRampToValueAtTime(Math.max(30, f1), t0 + dur);
    const g = ctx.createGain();
    g.gain.setValueAtTime(vol, t0);
    g.gain.exponentialRampToValueAtTime(.0001, t0 + dur);
    src.connect(flt);
    flt.connect(g);
    g.connect(master);
    src.start(t0);
    src.stop(t0 + dur + .02);
  }

  function tone(t0, dur, type, f0, f1, vol) {
    const o = ctx.createOscillator();
    o.type = type;
    o.frequency.setValueAtTime(Math.max(20, f0), t0);
    o.frequency.exponentialRampToValueAtTime(Math.max(20, f1), t0 + dur);
    const g = ctx.createGain();
    g.gain.setValueAtTime(vol, t0);
    g.gain.exponentialRampToValueAtTime(.0001, t0 + dur);
    o.connect(g);
    g.connect(master);
    o.start(t0);
    o.stop(t0 + dur + .02);
  }

  const A = {
    unlock,

    shot() {
      safe(t => {
        noise(t, .09, 'bandpass', 2600, 700, .55, 1.2);
        noise(t, .16, 'lowpass', 900, 120, .5);
        tone(t, .07, 'square', 190, 60, .28);
      });
    },

    rocketFire() {
      safe(t => {
        noise(t, .5, 'lowpass', 300, 1600, .6);
        noise(t + .06, .45, 'bandpass', 800, 200, .4, 2);
        tone(t, .25, 'sine', 110, 45, .5);
      });
    },

    emptyClick() {
      safe(t => {
        tone(t, .03, 'square', 2100, 1400, .18);
        noise(t, .02, 'highpass', 4000, 4000, .12);
      });
    },

    reload() {
      safe(t => {
        noise(t, .04, 'highpass', 3000, 1500, .22);
        noise(t + .22, .05, 'highpass', 1800, 900, .26);
        tone(t + .22, .05, 'square', 300, 180, .14);
      });
    },

    explosion() {
      safe(t => {
        noise(t, 1.1, 'lowpass', 420, 50, 1);
        tone(t, .8, 'sine', 72, 26, .85);
        noise(t + .08, .7, 'lowpass', 200, 40, .5);
      });
    },

    enemyShot(dist) {
      safe(t => {
        const v = Math.min(.5, .5 / (1 + dist * .07));
        noise(t, .1, 'bandpass', 1200, 500, v, 1);
        tone(t, .06, 'square', 150, 55, v * .5);
      });
    },

    kill() {
      safe(t => {
        tone(t, .09, 'triangle', 660, 660, .2);
        tone(t + .09, .14, 'triangle', 990, 990, .2);
      });
    },

    pickup() {
      safe(t => {
        tone(t, .06, 'sine', 520, 520, .22);
        tone(t + .07, .09, 'sine', 780, 780, .22);
      });
    }
  };

  G.audio = A;
})();
