"""Add the Pulse H-03 to the pinned Gun Zone source during the site build."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = Path("src")


def replace(filename, old, new):
    path = SRC / filename
    source = path.read_text(encoding="utf-8")
    if source.count(old) != 1:
        raise SystemExit(f"{filename}: expected exactly one Pulse H-03 patch match: {old!r}")
    path.write_text(source.replace(old, new, 1), encoding="utf-8")


model = (ROOT / "features/pulse-h03.js").read_text(encoding="utf-8")
mesh = (ROOT / "assets/pulse-h03.mesh.json").read_text(encoding="utf-8").strip()
(SRC / "06lb-pulse-h03.js").write_text(model.replace("__PULSE_MESH__", mesh), encoding="utf-8")

replace("06i-armes.js", "const WEAPONS = {", """const WEAPONS = {
  pulse_h03: { id: 'pulse_h03', name: 'Pulse H-03', type: 'Laser hạng nặng', cat: 'ar', fam: 'rifle',
    model: 'pulse_h03', sound: 'sniper', auto: false, rpm: 20, recharge: 3,
    dmg: [125, 125], range: [0, 300], head: 1, legs: 1, mag: 1, reserve: 0, slots: [],
    spread: [0, 0], moveSpread: 0, recoil: { v: 0.023, h: 0.007, kick: 0.067, rot: 0.09 },
    adsTime: 0.31, adsFov: 0.72, move: 0.86, pattern: 'rand', loud: true,
    ai: { ideal: 30, aggr: 0.27 }, stats: { dmg: 1, acc: 1, rng: 1, rof: 0.06, mob: 0.39 },
    desc: 'Một tia xanh hạ địch khi bắn trúng. Tự hồi năng lượng sau 3 giây.' },""")
replace("06i-armes.js", "const FEEL = {", """const FEEL = {
  pulse_h03: { kick: 1.5, rot: 1.2, roll: 0.55, shake: 0.42, fov: 2.6, flash: 0.8, spring: [130, 12], smoke: 0, punch: 1.15, spark: 0 },""")
replace("07-bots.js", "if (mix[c] !== undefined) (byCat", "if (!WEAPONS[id].recharge && mix[c] !== undefined) (byCat")
replace("07c-controller.js", "  const canFire = !ent.busy", """  for (const slot of A.slots) {
    if (slot.def.recharge && slot.mag === 0 && now >= slot.readyAt) slot.mag = 1;
  }
  const canFire = !ent.busy""")
replace("07c-controller.js", "  w.mag--; A.shots++;", """  w.mag--; A.shots++;
  if (d.recharge) A.pulseReadyAt = w.readyAt = now + d.recharge;""")
replace("07c-controller.js", "    const dir = coneDir(f, d.pellets", "    const dir = d.recharge ? f : coneDir(f, d.pellets")
replace("07c-controller.js", "  A.fireCd = 60 / d.rpm;", "  if (!d.recharge) A.fireCd = 60 / d.rpm;")
replace("07-bots.js", """  if (tracer && muzzle) FX.tracers.add(muzzle, end);
  kcEvent('ray',""", """  if (def.recharge) {
    const from = muzzle || origin, impact = !!(mz || dz || hz || eh || w);
    pulseShotFx(from, end, impact);
    if (MATCH.online && netIsLocal(shooter)) {
      netEvent({ k: 'pulse', a: from.toArray(), b: end.toArray(), impact }, shooter);
    }
    kcEvent('pulse', { a: from.clone(), b: end.clone(), impact });
  } else if (tracer && muzzle) FX.tracers.add(muzzle, end);
  if (!def.recharge) kcEvent('ray',""")
replace("07-bots.js", "    dmg *= dmgMul;\n    bloodFx(end,", "    dmg = def.recharge ? def.dmg[0] : dmg * dmgMul;\n    if (!def.recharge) bloodFx(end,")
replace("04-fx.js", "FX.tracers.update(dt); updateRings(dt);", "FX.tracers.update(dt); pulseUpdateFx(dt); updateRings(dt);")
replace("08-player.js", "  if (!d.bolt && !d.pump) vmShell(d);", "  if (!d.bolt && !d.pump && !d.recharge) vmShell(d);")
replace("08-player.js", "  if (!d.silent) flashLight(muzzle, 3, 8, 0.05);", "  if (!d.silent) flashLight(muzzle, 3, 8, 0.05, d.recharge ? 0x54ff88 : undefined);")
replace("09-game.js", "!kn && w.mag <= Math.ceil(d.mag * 0.25)", "!kn && w.mag <= (d.recharge ? 0 : Math.ceil(d.mag * 0.25))")
replace("09-game.js", "  hudStyle(rh, 'opacity', low ? '1' : '0');", """  const charging = e.alive && !kn && d.recharge && w.mag === 0;
  hudStyle(rh, 'opacity', low || charging ? '1' : '0');
  if (charging) {
    hudText(rh, `Hồi năng lượng · ${Math.max(0, w.readyAt - now).toFixed(1)} s`);
    hudCls(rh, 'empty', false);
  }""")
replace("09b-killcam.js", "    } else if (ev.type === 'ray')", """    } else if (ev.type === 'pulse') {
      pulseShotFx(ev.a, ev.b, ev.impact);
    } else if (ev.type === 'ray')""")
replace("09c-net.js", "    if (!e.weapon.silent) {\n      const hit = rayWorld", "    if (!e.weapon.silent && !e.weapon.recharge) {\n      const hit = rayWorld")
replace("09c-net.js", "  if (ev.k === 'hit') {\n    const tgt = netLocal(ev.to);", """  if (ev.k === 'pulse') {
    const valid = (p) => Array.isArray(p) && p.length === 3 && p.every((n) => Number.isFinite(n) && Math.abs(n) < 10000);
    if (!valid(ev.a) || !valid(ev.b)) return;
    const a = new V3(...ev.a), b = new V3(...ev.b);
    if (a.distanceToSquared(b) > 302 ** 2) return;
    pulseShotFx(a, b, ev.impact === true);
    kcEvent('pulse', { a, b, impact: ev.impact === true });
  } else if (ev.k === 'hit') {
    const tgt = netLocal(ev.to);""")
replace("06-weapons.js", "const c = o.material.color, k = o.material.userData.camo", "const c = o.material.color, k = o.material.userData.pulseEnergy ? 'pulseEnergy' : o.material.userData.camo")
replace("06-weapons.js", "const WORLD_GUN_MATS = {", """const WORLD_GUN_MATS = {
  pulseEnergy: new THREE.MeshStandardMaterial({ color: 0x26ff72, emissive: 0x26ff72, emissiveIntensity: 0.85 }),""")
replace("06-weapons.js", "const WORLD_GUN_KEYS = ['light'", "const WORLD_GUN_KEYS = ['pulseEnergy', 'light'")
replace("08c-pickups.js", "function equipGroundGun(d) {\n  const P = PL.ent, A = P.arms;", """function equipGroundGun(d) {
  const P = PL.ent, A = P.arms;
  if (d.def.recharge && A.slots.some((slot, i) => i !== A.cur && slot.def.id === d.def.id)) {
    if (d.obj) removeDrop(d);
    return;
  }""")
replace("08c-pickups.js", "  A.slots[A.cur] = { def: d.def, mag: d.mag, reserve: d.reserve };", """  const readyAt = d.def.recharge ? A.pulseReadyAt || 0 : 0;
  A.slots[A.cur] = { def: d.def, mag: readyAt > MATCH.time ? 0 : d.mag, reserve: d.reserve, readyAt };""")
replace("06-weapons.js", "  VM.flash.rotation.z = Math.random()", """  for (const material of VM.flashM) {
    if (def.recharge) material.color.setRGB(0.18, 2.3, 0.55);
    else material.color.setRGB(2.3, 2.05, 1.7);
  }
  VM.flash.rotation.z = Math.random()""")
