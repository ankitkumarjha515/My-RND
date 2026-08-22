(() => {
  const G = window.GAME;

  const style = document.createElement('style');
  style.textContent = `
#hud{position:fixed;inset:0;pointer-events:none;z-index:20;font-family:"Segoe UI",system-ui,sans-serif;color:#e8ecf2;user-select:none}
.hud-off{display:none!important}
#xh{position:absolute;left:50%;top:50%;width:22px;height:22px;transform:translate(-50%,-50%)}
#xh:before,#xh:after{content:"";position:absolute;background:rgba(240,244,250,.9);box-shadow:0 0 3px rgba(0,0,0,.9)}
#xh:before{left:50%;top:3px;width:2px;height:16px;margin-left:-1px}
#xh:after{top:50%;left:3px;height:2px;width:16px;margin-top:-1px}
#hm{position:absolute;left:50%;top:50%;width:30px;height:30px;transform:translate(-50%,-50%) rotate(45deg);opacity:0;transition:opacity .18s}
#hm span{position:absolute;background:#fff;box-shadow:0 0 4px rgba(0,0,0,.8)}
#hm span:nth-child(1){left:0;top:0;width:10px;height:2px}
#hm span:nth-child(2){right:0;top:0;width:2px;height:10px}
#hm span:nth-child(3){left:0;bottom:0;width:2px;height:10px}
#hm span:nth-child(4){right:0;bottom:0;width:10px;height:2px}
#hm.killed span{background:#ff4040}
#vig{position:absolute;inset:0;box-shadow:inset 0 0 140px 60px rgba(200,10,10,.85);opacity:0;transition:opacity .35s}
#cine{position:absolute;inset:0;background:radial-gradient(ellipse at center,transparent 52%,rgba(4,7,11,.52) 100%)}
#hpwrap{position:absolute;left:26px;bottom:26px}
#hplabel{font-size:11px;letter-spacing:.28em;color:#9aa3b2;margin-bottom:6px}
#hpbar{width:230px;height:14px;background:rgba(10,14,20,.72);border:1px solid rgba(255,255,255,.16);border-radius:3px;overflow:hidden}
#hpfill{height:100%;width:100%;background:#43d17c;transition:width .15s,background .3s}
#hpnum{margin-top:5px;font-size:12px;color:#c6ccd6}
#ammowrap{position:absolute;right:26px;bottom:22px;text-align:right}
#wname{font-size:11px;letter-spacing:.3em;color:#9aa3b2;margin-bottom:4px}
#amag{font-size:44px;font-weight:700;line-height:1;text-shadow:0 2px 8px rgba(0,0,0,.7)}
#ares{font-size:16px;color:#98a0ad;margin-left:8px}
#wavehud{position:absolute;left:26px;top:24px;font-size:13px;letter-spacing:.24em;color:#cfd6e0;text-shadow:0 1px 4px rgba(0,0,0,.8)}
#feed{position:absolute;right:26px;top:24px;display:flex;flex-direction:column;align-items:flex-end;gap:5px}
.fitem{font-size:12px;padding:4px 10px;background:rgba(12,16,22,.72);border:1px solid rgba(255,255,255,.1);border-radius:3px;color:#dfe5ee;transition:opacity .5s}
.fitem.out{opacity:0}
#msg{position:absolute;left:50%;bottom:19%;transform:translateX(-50%);font-size:15px;letter-spacing:.34em;color:#ffd27a;text-shadow:0 1px 6px rgba(0,0,0,.9);opacity:0;transition:opacity .2s}
#popup{position:absolute;left:50%;top:33%;transform:translateX(-50%);font-size:34px;font-weight:700;letter-spacing:.42em;color:#fff;text-shadow:0 0 18px rgba(120,180,255,.65),0 2px 8px rgba(0,0,0,.8);opacity:0}
#popup.pop{animation:popa 1.5s ease forwards}
@keyframes popa{0%{opacity:0;transform:translateX(-50%) scale(.86)}12%{opacity:1;transform:translateX(-50%) scale(1)}75%{opacity:1}100%{opacity:0}}
#ovl{position:fixed;inset:0;z-index:30;display:flex;align-items:center;justify-content:center;background:rgba(6,9,14,.82);backdrop-filter:blur(6px);font-family:"Segoe UI",system-ui,sans-serif;color:#e8ecf2}
.panel{text-align:center;max-width:560px;padding:40px 48px;background:rgba(13,18,26,.92);border:1px solid rgba(255,255,255,.1);border-radius:10px;box-shadow:0 24px 80px rgba(0,0,0,.6)}
.panel h1{font-size:34px;letter-spacing:.3em;margin-bottom:8px}
.panel .sub{font-size:12px;letter-spacing:.24em;color:#93a0b4;margin-bottom:26px}
.ctl{display:grid;grid-template-columns:auto auto;gap:6px 22px;justify-content:center;font-size:13px;margin-bottom:28px;color:#b9c2cf;text-align:left}
.ctl b{color:#f2f5fa;font-weight:600}
.btn{pointer-events:auto;cursor:pointer;border:1px solid #3f74ff;background:#1d3a86;color:#fff;font-size:15px;letter-spacing:.3em;padding:13px 42px;border-radius:5px;transition:background .15s,transform .12s;font-family:inherit}
.btn:hover{background:#2950b4;transform:translateY(-1px)}
.stats{display:flex;gap:38px;justify-content:center;margin-bottom:26px}
.stat .v{font-size:36px;font-weight:700;color:#ffd27a}
.stat .k{font-size:10px;letter-spacing:.26em;color:#8b96a8;margin-top:3px}
.hidden{display:none!important}
`;
  document.head.appendChild(style);

  const hud = document.createElement('div');
  hud.id = 'hud';
  hud.innerHTML = [
    '<div id="cine"></div>',
    '<div id="vig"></div>',
    '<div id="xh"></div>',
    '<div id="hm"><span></span><span></span><span></span><span></span></div>',
    '<div id="wavehud">WAVE 1 &nbsp;&middot;&nbsp; KILLS 0</div>',
    '<div id="feed"></div>',
    '<div id="hpwrap"><div id="hplabel">INTEGRITY</div><div id="hpbar"><div id="hpfill"></div></div><div id="hpnum">100 / 100</div></div>',
    '<div id="ammowrap"><div id="wname">M4 CARBINE</div><div><span id="amag">30</span><span id="ares">/ 150</span></div></div>',
    '<div id="msg"></div>',
    '<div id="popup"></div>'
  ].join('');
  document.body.appendChild(hud);

  const $ = id => document.getElementById(id);
  const el = {
    vig: $('vig'), xh: $('xh'), hm: $('hm'), wave: $('wavehud'),
    feed: $('feed'), hpfill: $('hpfill'), hpnum: $('hpnum'),
    wname: $('wname'), amag: $('amag'), ares: $('ares'),
    msg: $('msg'), popup: $('popup')
  };

  const ovl = document.createElement('div');
  ovl.id = 'ovl';
  ovl.innerHTML = `
<div class="panel" id="p-start">
  <h1>REACH-OUT</h1>
  <div class="sub">BLAKSITE PERIMETER &mdash; HOLD AS LONG AS YOU CAN</div>
  <div class="ctl">
    <span>MOVE</span><b>W A S D</b>
    <span>SPRINT</span><b>SHIFT</b>
    <span>JUMP</span><b>SPACE</b>
    <span>FIRE</span><b>LMB</b>
    <span>AIM</span><b>RMB</b>
    <span>WEAPONS</span><b>1 / 2 / Q / WHEEL</b>
    <span>RELOAD</span><b>R</b>
  </div>
  <button class="btn" id="b-start">DEPLOY</button>
</div>
<div class="panel hidden" id="p-pause">
  <h1>PAUSED</h1>
  <div class="sub">POINTER RELEASED</div>
  <button class="btn" id="b-resume">RESUME</button>
</div>
<div class="panel hidden" id="p-death">
  <h1 style="color:#ff5a5a">K.I.A.</h1>
  <div class="sub">PERIMETER OVERRUN</div>
  <div class="stats">
    <div class="stat"><div class="v" id="s-kills">0</div><div class="k">KILLS</div></div>
    <div class="stat"><div class="v" id="s-wave">1</div><div class="k">WAVE</div></div>
  </div>
  <button class="btn" id="b-restart">REDEPLOY</button>
</div>`;
  ovl.classList.add('hidden');
  document.body.appendChild(ovl);

  const panels = { start: $('p-start'), pause: $('p-pause'), death: $('p-death') };

  function act(id, fn) {
    $(id).addEventListener('click', () => {
      try { G.audio.unlock(); } catch (err) { console.error('GAME.ui: audio unlock', err); }
      fn();
    });
  }
  act('b-start', () => { try { G.player.requestLock(); } catch (err) { console.error(err); } });
  act('b-resume', () => { try { G.player.requestLock(); } catch (err) { console.error(err); } });
  act('b-restart', () => { try { G.player.restartAll(); } catch (err) { console.error(err); } });

  let msgTimer = 0;
  let hmTimer = 0;
  let vigTimer = 0;

  const UI = {
    setAmmo(mag, reserve, name) {
      el.amag.textContent = String(mag);
      el.ares.textContent = '/ ' + reserve;
      el.wname.textContent = name;
    },
    updateHealth(hp, max) {
      const p = Math.max(0, Math.min(100, (hp / max) * 100));
      el.hpfill.style.width = p.toFixed(1) + '%';
      el.hpfill.style.background = p > 50 ? '#43d17c' : p > 25 ? '#ffb02e' : '#ff4747';
      el.hpnum.textContent = Math.ceil(Math.max(0, hp)) + ' / ' + max;
    },
    setWaveKills(wave, kills) {
      el.wave.innerHTML = 'WAVE ' + wave + ' &nbsp;&middot;&nbsp; KILLS ' + kills;
    },
    hitmarker(killed) {
      el.hm.classList.toggle('killed', !!killed);
      el.hm.style.transition = 'none';
      el.hm.style.opacity = '1';
      clearTimeout(hmTimer);
      hmTimer = setTimeout(() => {
        el.hm.style.transition = 'opacity .18s';
        el.hm.style.opacity = '0';
      }, killed ? 170 : 110);
    },
    msg(text, ms) {
      el.msg.textContent = text;
      el.msg.style.opacity = '1';
      clearTimeout(msgTimer);
      msgTimer = setTimeout(() => { el.msg.style.opacity = '0'; }, ms || 900);
    },
    popup(text) {
      el.popup.classList.remove('pop');
      void el.popup.offsetWidth;
      el.popup.textContent = text;
      el.popup.classList.add('pop');
    },
    killFeed(text) {
      const d = document.createElement('div');
      d.className = 'fitem';
      d.textContent = text;
      el.feed.prepend(d);
      while (el.feed.children.length > 4) el.feed.removeChild(el.feed.lastChild);
      setTimeout(() => d.classList.add('out'), 2600);
      setTimeout(() => { if (d.parentNode) d.parentNode.removeChild(d); }, 3200);
    },
    flashDamage(i) {
      el.vig.style.opacity = String(Math.max(.25, Math.min(.95, i)));
      clearTimeout(vigTimer);
      vigTimer = setTimeout(() => { el.vig.style.opacity = '0'; }, 70);
    },
    overlay(kind, payload) {
      if (!kind) {
        ovl.classList.add('hidden');
        hud.classList.remove('hud-off');
        return;
      }
      Object.keys(panels).forEach(k => panels[k].classList.add('hidden'));
      if (!panels[kind]) {
        console.error('GAME.ui.overlay: unknown kind', kind);
        return;
      }
      if (kind === 'death' && payload) {
        $('s-kills').textContent = String(payload.kills || 0);
        $('s-wave').textContent = String(payload.wave || 1);
      }
      panels[kind].classList.remove('hidden');
      ovl.classList.remove('hidden');
      if (kind === 'start') hud.classList.add('hud-off');
    }
  };

  G.ui = UI;
})();
