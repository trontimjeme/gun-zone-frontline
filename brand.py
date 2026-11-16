from pathlib import Path
from PIL import Image
import os, re, shutil

logo = Image.open("azone-logo.png").convert("RGB")
logo.save("assets/logo.webp", lossless=True)
mark = logo.crop((3, 3, 39, 39))
for path in [*Path("assets/icon").glob("*"), *Path("assets/deck").glob("*"), Path("assets/apercu.jpg")]:
    if path.suffix not in {".ico", ".png", ".jpg"}:
        continue
    size = Image.open(path).size
    canvas = Image.new("RGB", size, logo.getpixel((0, 0)))
    art = mark if size[0] == size[1] else logo
    ratio = min(size[0] / art.width, size[1] / art.height) * 0.9
    art = art.resize(tuple(max(1, round(v * ratio)) for v in art.size), Image.Resampling.LANCZOS)
    canvas.paste(art, tuple((a-b)//2 for a,b in zip(size,art.size)))
    canvas.save(path)
for path in [Path("shell.html"), Path("build.py"), Path("assets/deck/installer.sh"), Path("i18n/en.txt"), *Path("src").glob("*.js")]:
    s = path.read_text()
    s = re.sub("Riposte: Frontline", "Gun ZONE", s, flags=re.I)
    s = s.replace('"short_name":"Riposte"', '"short_name":"Gun ZONE"').replace("www.playriposte.com", "gun-zone-frontline.vercel.app")
    if path.name == "05-audio.js":
        s = re.sub(r"const HIT_SAMPLE = '[^']*'", "const HIT_SAMPLE = 'AAAAAA=='", s)
    path.write_text(s)
for path in [*Path("assets/anim").glob("clips.*"), *Path("assets/sfx/fin").glob("*.mp3"), Path("dist/menu-theme.mp3")]:
    path.unlink(missing_ok=True)
Path("assets/rankup.mp3").write_bytes(b"")

def edit_source(file, old, new):
    path = Path("src") / file
    content = path.read_text()
    if content.count(old) != 1:
        raise ValueError(f"Unexpected source in {file}")
    path.write_text(content.replace(old, new))

edit_source("07-bots.js", "const BOT_NAMES = [\n  ['Dubois', 'Keller', 'Marchetti', 'Okafor', 'Novak'],", """const azoneRoster = ['AZONE TUẤN ANH', 'AZONE HÀ J', 'AZONE MINH CẬN', 'AZONE MINH CON',
  'AZONE TÙNG CẤU', 'AZONE GIANG', 'AZONE VUI', 'AZONE MY'];
for (let i = azoneRoster.length - 1; i > 0; i--) {
  const j = Math.floor(Math.random() * (i + 1));
  [azoneRoster[i], azoneRoster[j]] = [azoneRoster[j], azoneRoster[i]];
}
const BOT_NAMES = [
  azoneRoster.slice(0, 5),""")
edit_source("07-bots.js", "const TEAM_NAMES = ['Alpha', 'Bravo'];", "const TEAM_NAMES = ['AZONE', 'Bravo'];")
edit_source("09e-menus.js", "const SOLO_PAGES = {", """function soloNameRow() {
  const input = document.createElement('input');
  input.maxLength = 16;
  input.autocomplete = 'nickname';
  input.placeholder = 'Nhập tên của bạn';
  input.value = NET.nick;
  input.setAttribute('aria-label', 'Đặt tên người chơi');
  input.addEventListener('change', () => {
    const field = $('netName');
    field.value = input.value.normalize('NFC');
    field.dispatchEvent(new Event('change'));
    input.value = NET.nick;
    PL.ent.name = NET.nick;
    renderSolo();
  });
  return { k: 'text', key: 'soloName', label: 'Đặt tên người chơi', input };
}
const SOLO_PAGES = {""")
edit_source("09e-menus.js", "if (netInLobby()) rows.push({ k: 'note', text: SRV.on", "if (!ACCT.user) rows.unshift(soloNameRow());\n    if (netInLobby()) rows.push({ k: 'note', text: SRV.on")
edit_source("09-game.js", "for (let i = 0; i < 5; i++) makeBot", "PL.ent.name = NET.nick || _t('Vous');\n    for (let i = 0; i < 5; i++) makeBot")

# Shared in-match HUD for desktop and touch.
hud_style = """<style>
#killfeed,body.touch #killfeed{left:auto;right:max(12px,env(safe-area-inset-right));top:max(12px,env(safe-area-inset-top));align-items:flex-end;pointer-events:none}
#hitmarker.head::after{content:'💀';position:absolute;left:0;top:0;transform:translate(-50%,-50%);font:30vmin/1 'Segoe UI Emoji','Apple Color Emoji',sans-serif;filter:grayscale(1) brightness(1.65);opacity:.29;pointer-events:none}
</style>"""
shell = Path("shell.html")
shell.write_text(shell.read_text().replace("</head>", hud_style + "</head>", 1))

edit_source("09c-net.js", "const NET_PAGES = {", "let wifiTeam = '', wifiBusy = false;\nasync function wifiConnect() {\n  if (wifiBusy || NET.role !== 'off') return;\n  if (!netLib()) { netStatus('Hãy tải lại trang để kết nối WIFI TEAM.'); return; }\n  wifiBusy = true;\n  netStatus('Đang tìm đội trên Wi-Fi hiện tại…');\n  try {\n    const response = await fetch('/api/wifi-team', {cache:'no-store', signal:AbortSignal.timeout(10000)});\n    if (!response.ok) throw Error();\n    const {team} = await response.json();\n    if (!/^[a-f0-9]{32}$/.test(team)) throw Error();\n    if (NET.role !== 'off' || UI.screen !== 'multi') return;\n    wifiTeam = team;\n    netHost({code:'WTEAM', pub:false});\n  } catch { wifiTeam = ''; netStatus('Chưa kết nối được WIFI TEAM. Kiểm tra Internet rồi thử lại.'); }\n  finally { wifiBusy = false; }\n}\nconst NET_PAGES = {")
edit_source("09c-net.js", "    if (!acctOnlineOk()) { // le multijoueur demande un compte", "    rows.push({k:'btn',key:'wifi-team',label:'WIFI TEAM · Kết nối LAN',sub:'Chọn cùng Wi-Fi trên thiết bị rồi bấm để tự tạo hoặc vào phòng.',run:wifiConnect,disabled:!netLib()});\n    if (!acctOnlineOk()) { // le multijoueur demande un compte")
edit_source("09c-net.js", "function netPeerOpts() { return", "function netPeerOpts() { if (wifiTeam) return {debug:0, config:{iceServers:[]}}; return")
edit_source("09c-net.js", "new Peer(NET_PREFIX + code,", "new Peer((wifiTeam ? 'gunzone-wifi-' + wifiTeam : NET_PREFIX) + code,")
edit_source("09c-net.js", "peer.connect(NET_PREFIX + code,", "peer.connect((wifiTeam ? 'gunzone-wifi-' + wifiTeam : NET_PREFIX) + code,")
edit_source("09c-net.js", "const t = err && err.type;", "const t = err && err.type;\n  if (wifiTeam && t === 'unavailable-id' && NET.role === 'host' && !NET.joined) {\n    const team = wifiTeam; netReset(); wifiTeam = team; netJoinLobby('WTEAM'); return;\n  }")
edit_source("09c-net.js", "function netReset(msg) {", "function netReset(msg) {\n  wifiTeam = '';")
edit_source("09d-netrelay.js", "function netrUrl() {", "function netrUrl() {\n  if (wifiTeam) return '';")
edit_source("09j-compte.js", "function acctGate(code) {", "function acctGate(code) {\n  if (wifiTeam) return true;")
edit_source("09c-net.js", "function netLink() { return", "function netLink() { if (wifiTeam) return location.origin + location.pathname + '?wifi=1'; return")
edit_source("09c-net.js", "function netAutoJoin() {", "function netAutoJoin() {\n  if (new URLSearchParams(location.search).get('wifi') === '1') { uiGo('multi'); wifiConnect(); return; }")

# Sample the existing AZONE chest emblem from the project logo.
badge = logo.crop((3, 3, 39, 39)).resize((24, 24)).convert("RGB")
badge_rows = ["".join("1" if sum(px) > 350 else "0" for px in [badge.getpixel((x,y)) for x in range(24)]) for y in range(24)]
edit_source("06ga-tenues.js", "const SKIN_REL =", """function azoneTeamSkin(skin, team) {
  if (skin === 'azoneVarsity') skin = 'assault';
  return team === 0 && skin === 'assault' ? 'azoneVarsity' : skin;
}
SKINS.azoneVarsity = {
  ...SKINS.assault, name: 'AZONE Varsity', parts: { ...SKINS.assault.parts, patch: false },
  art(g, w, h) {
    g.fillStyle = '#173e34'; g.fillRect(0, 0, w, h);
    g.fillStyle = '#eee4c7';
    for (const y of [.02,.055,.91,.945]) g.fillRect(0,y*h,w,.012*h);
    g.fillStyle = '#112c26'; g.fillRect(.243*w,0,.014*w,h);
    g.fillStyle = '#ddc896';
    for(let i=1;i<=6;i++){g.beginPath();g.arc(w*.25,h*i/7,2,0,Math.PI*2);g.fill();}
    g.textAlign='center'; g.fillStyle='#f1dfac';
    const badge = """ + repr(badge_rows) + """;
    badge.forEach((row,y) => { for (let x=0;x<24;x++) if(row[x]==='1') g.fillRect(w*.322+x*.85,h*.32+y*1.3,1,1.5); });
    g.font='bold 30px sans-serif'; g.fillText('AZONE', w*.75, h*.39,w*.27);
  }
};
const SKIN_REL =""")
edit_source("06ga-tenues.js", "(e === PL.ent ? skinMine() : skinId(e.skin))", "azoneTeamSkin(e === PL.ent ? skinMine() : skinId(e.skin), e.team)")
edit_source("06g-body.js", "soldierVest(B, skin, hi); mark('gilet');", "if (skin !== 'azoneVarsity') soldierVest(B, skin, hi); mark('gilet');")
edit_source("06g-body.js", "0.0, { bump: (a, k)", "0.0, { ...(skin === 'azoneVarsity' ? { uv: (u, y) => atlasUV('art', u, 1 - (y - 1) / .485) } : {}), bump: (a, k)")
edit_source("06g-body.js", "uv: (u, v) => atlasUV('camo', 0.45 + u * 0.52, (v + 0.1) / 0.7)", """...(skin === 'azoneVarsity' ? {
        uv: () => GEAR_TILE.fab, col: (a,k,p,s) => new THREE.Color(s.v > .475 ? '#214b3b' : '#e9dfc7')
      } : {uv: (u, v) => atlasUV('camo', 0.45 + u * 0.52, (v + 0.1) / 0.7)})""")
edit_source("07-bots.js","makeSoldier(b.skin, team","makeSoldier(azoneTeamSkin(b.skin, team), team")
edit_source("07-bots.js","soldierLook(b.model, b.skin,","soldierLook(b.model, azoneTeamSkin(b.skin, b.team),")
edit_source("09c-net.js","makeSoldier(e.skin, skinRel(e)","makeSoldier(azoneTeamSkin(e.skin, e.team), skinRel(e)")
edit_source("09c-net.js","soldierLook(e.model, sk, skinRel(e))","soldierLook(e.model, azoneTeamSkin(sk, team), skinRel(e))")
edit_source("06e-gear.js","  g.drawImage(cam, 0, 0);","  if (fp && skin === 'azoneVarsity') { const cloth = cam.getContext('2d'); cloth.fillStyle = '#e9dfc7'; cloth.fillRect(0,0,768,768); }\n  g.drawImage(cam, 0, 0);")
edit_source("06f-hands.js","const mine = skinMine();","const mine = azoneTeamSkin(skinMine(), PL.ent && PL.ent.team);")
edit_source("09u-tenues.js","vmSetLook(s, 0);","vmSetLook(azoneTeamSkin(s, PL.ent && PL.ent.team), 0);")
edit_source("09u-tenues.js","vmSetLook(m, 0);","vmSetLook(azoneTeamSkin(m, PL.ent && PL.ent.team), 0);")

edit_source("06g-body.js", "function soldierGeometry(skin, lod) {", "function azoneArmor(B, hi) {\n  const plate = new THREE.Color(0x273a37), edge = new THREE.Color(0x172624);\n  const gold = new THREE.Color(0xe1b56c), strap = new THREE.Color(0x344640);\n  for (const side of [-1, 1]) {\n    const mount = gMat(0, 1.288, side < 0 ? -.132 : .119, 0, side < 0 ? Math.PI : 0);\n    const box = (w,h,d,x,y,z,color,angle=0) =>\n      gBox(B,w,h,d,.003,mount.clone().multiply(gMat(x,y,z,0,0,angle)),torsoW,color,'fab',0,hi?1:0);\n    box(.272,.208,.032,0,0,0,edge);\n    box(.25,.182,.015,0,.003,.021,plate);\n    for (const x of [-.091,.091]) {\n      box(.041,.104,.024,x,.125,-.019,strap);\n      if (hi) box(.048,.017,.015,x,.107,.001,gold);\n    }\n    for (const y of [-.064,-.042]) box(.201,.01,.009,0,y,.031,edge);\n    // Raised lettering in the outward-facing coordinate system of each plate.\n    const strokes = [\n      [[0,0,.42,1],[.42,1,.84,0],[.19,.43,.65,.43]],\n      [[0,1,.8,1],[.8,1,0,0],[0,0,.8,0]],\n      [[0,.13,0,.87],[0,.87,.13,1],[.13,1,.68,1],[.68,1,.81,.87],[.81,.87,.81,.13],[.81,.13,.68,0],[.68,0,.13,0],[.13,0,0,.13]],\n      [[0,0,0,1],[0,1,.8,0],[.8,0,.8,1]],\n      [[0,0,0,1],[0,1,.8,1],[0,.5,.65,.5],[0,0,.8,0]]\n    ];\n    strokes.forEach((letter,i)=>letter.forEach(([x,y,X,Y])=>{\n      const dx=(X-x)*.037, dy=(Y-y)*.044;\n      box(Math.hypot(dx,dy)+.004,.006,.008,-.105+i*.045+(x+X)*.0185,.005+(y+Y)*.022,.032,gold,Math.atan2(dy,dx));\n    }));\n  }\n  for (const x of [-.094,.094])\n    gBox(B,.045,.028,.175,.008,gMat(x,1.437,-.006),torsoW,strap,'fab');\n}\nfunction soldierGeometry(skin, lod) {")
edit_source("06g-body.js", "if (skin !== 'azoneVarsity') soldierVest(B, skin, hi);", "if (skin === 'azoneVarsity') azoneArmor(B, hi); else soldierVest(B, skin, hi);")

edit_source("08c-pickups.js", "if (mag + reserve <= 0) return null;", "")
edit_source("08c-pickups.js", "if (mag + reserve <= 0) mag", "if (!v.isPlayer && mag + reserve <= 0) mag")
edit_source("08c-pickups.js", "  const A = v.arms, w = A && A.slots[A.cur];", "  if (MATCH.online && !v.netBot && !v.remoteBot) {\n    if (v.model && v.model.gun) v.model.gun.visible = false;\n    if (NET.role === 'host' && v.isPlayer) publishDeathGun(v, deathGunAmmo(v));\n    return;\n  }\n  const A = v.arms, w = A && A.slots[A.cur];")
edit_source("08c-pickups.js", "  dropWeapon(w.def, mag, reserve, _dpV, _dpQ, vel);", "  const dropped = dropWeapon(w.def, mag, reserve, _dpV, _dpQ, vel);\n  if (v.isPlayer) dropped.fromPlayer = true;")
edit_source("08c-pickups.js", "if (mine && dist", "if (!d.fromPlayer && mine && dist")
edit_source("08c-pickups.js", "if (!same && dist", "if ((d.fromPlayer || !same) && dist")
edit_source("08c-pickups.js", "  const old = A.slots[A.cur], yaw", "  if (d.netDrop) {\n    if (NET.role === 'host') claimDeathGun(NET.me, d.netDrop);\n    else netSend({t:'takeGun', id:d.netDrop});\n    return;\n  }\n  equipGroundGun(d);\n}\nfunction equipGroundGun(d) {\n  const P = PL.ent, A = P.arms;\n  const old = A.slots[A.cur], yaw")
edit_source("08c-pickups.js", "function dropSwapAllowed()", "let deathGunSeq = 0;\nfunction deathGunAmmo(v) {\n  const w = v.arms.slots[v.arms.cur];\n  return {w:w.def.id, g:w.def.key, mag:w.mag, reserve:w.reserve};\n}\nfunction spawnDeathGun(m) {\n  if (!NET.on || DROP.list.some(d=>d.netDrop === m.id)) return;\n  const def = netWeaponDef(m);\n  const d = dropWeapon(def,clamp(m.mag|0,0,def.mag),clamp(m.reserve|0,0,def.reserve),\n    new V3(m.x,m.y,m.z),new THREE.Quaternion(),new V3());\n  d.netDrop = m.id; d.fromPlayer = true; d.age = clamp(m.age || 0,0,DROP.life);\n}\nfunction publishDeathGun(v, ammo) {\n  if (!ammo || v.voidDead) return;\n  const m = {...ammo,t:'deathGun',id:++deathGunSeq,x:v.pos.x,y:v.pos.y+.6,z:v.pos.z};\n  spawnDeathGun(m); netBroadcast(m,true);\n}\nfunction claimDeathGun(id,key) {\n  const d = DROP.list.find(d=>d.netDrop === key), picker = netEntity(id);\n  if (!d || !d.landed || !picker || !picker.alive || picker.pos.distanceToSquared(d.obj.position)>6.25) return;\n  const take = {t:'gunTaken',id:key,who:id,w:d.def.id,g:d.def.key,mag:d.mag,reserve:d.reserve};\n  if (id === NET.me) equipGroundGun(d); else removeDrop(d);\n  netBroadcast(take,true);\n}\nfunction dropSwapAllowed()")
edit_source("09-game.js", "netEvent({ k: 'kill', by:", "netEvent({ k: 'kill', ammo: v.isPlayer ? deathGunAmmo(v) : undefined, by:")
edit_source("09c-net.js", "    killEnt(e, killer, netWeaponName(ev.w, killer), !!ev.h, dir);", "    if (NET.role === 'host' && !e.remoteBot && !fall) publishDeathGun(e, ev.ammo);\n    killEnt(e, killer, netWeaponName(ev.w, killer), !!ev.h, dir);")
edit_source("09c-net.js", "    case 'nick': pl.n", "    case 'takeGun': if (NET.on && pl.ig && Number.isInteger(m.id)) claimDeathGun(id,m.id); break;\n    case 'nick': pl.n")
edit_source("09c-net.js", "  NET.hostSeen = performance.now();\n  switch (m.t) {", "  NET.hostSeen = performance.now();\n  switch (m.t) {\n    case 'deathGun': spawnDeathGun(m); return;\n    case 'gunTaken': {\n      const d = DROP.list.find(d=>d.netDrop === m.id);\n      if (NET.on && m.who === NET.me && PL.ent.alive) {\n        if (d) removeDrop(d);\n        equipGroundGun({def:netWeaponDef(m),mag:m.mag,reserve:m.reserve});\n      } else if (d) removeDrop(d);\n      return;\n    }")
edit_source("08c-pickups.js", "  removeDrop(d);\n  // l'arme rangée", "  if (d.obj) removeDrop(d);\n  // l'arme rangée")
edit_source("08c-pickups.js", "function clearDrops() {", "function clearDrops() { DROP.synced = false;")
edit_source("08c-pickups.js", "function updateDrops(dt) {", "function updateDrops(dt) {\n  if (NET.on && NET.role === 'client' && !DROP.synced) { DROP.synced = true; netSend({t:'listGuns'}); }")
edit_source("09c-net.js", "    case 'takeGun':", "    case 'listGuns':\n      if (NET.on && pl.ig) for (const d of DROP.list) if (d.netDrop) {\n        const p = d.obj.position;\n        netSendTo(pl,{t:'deathGun',id:d.netDrop,w:d.def.id,g:d.def.key,mag:d.mag,reserve:d.reserve,x:p.x,y:p.y,z:p.z,age:d.age});\n      }\n      break;\n    case 'takeGun':")

edit_source("08a-binds.js", "const bindDefault = (a) => BIND_DEFS.find((d) => d[0] === a)[1];", "const bindDefault = (a) => a === 'crouch' ? 'ControlRight' : a === 'use' ? 'End' : BIND_DEFS.find((d) => d[0] === a)[1];\nconst padKeys = Array.from({length:10}, (_,i) => 'Numpad' + i);")
edit_source("08a-binds.js", "function keyCanon(code) { if", "function keyCanon(code) {\n  if (!BIND.rev.has(code)) {\n    if (code === 'Numpad0') return 'KeyR';\n    if (/^Numpad[1-9]$/.test(code)) code = 'Digit' + code.slice(-1);\n  }\n  if")
edit_source("08a-binds.js", "...BIND_DEFS.map((d) => bindOf(d[0])),", "...BIND_DEFS.map((d) => bindOf(d[0])), ...padKeys,")
edit_source("08a-binds.js", " : keyLabel(bindOf(a));", " : [keyLabel(bindOf(a)), ...padKeys.filter(k => k !== bindOf(a) && keyCanon(k) === BIND_DEFS.find(d => d[0] === a)[1]).map(k => 'Num ' + k.slice(-1))].join(' / ');")
edit_source("08-player.js", "if (['Space', 'ArrowUp', 'ArrowDown'].includes(c))", "if (e.code === 'End' || /^Numpad[0-9]$/.test(e.code) || ['Space', 'ArrowUp', 'ArrowDown'].includes(c))")
